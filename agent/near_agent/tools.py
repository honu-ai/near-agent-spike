from typing import Optional, Any
from uuid import uuid4

import httpx
from PIL import Image
from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai.types import GenerateContentConfig, ImageConfig

from .settings import AgentSettings


def generate_hero_images(
        business_summary: str,
        tool_context: ToolContext,
        user_request: Optional[str] = None,
        image_to_edit: Optional[str] = None,
) -> dict:
    """
    Using a summary of the business plan, and potentially some user feedback and an image to edit, generate some image ideas that could be used for the header for the post.
    :param business_summary: A summary of the Business Plan. Will be used to prompt the generation.
    :param user_request: If the User provides any feedback on an image, provide this as well to add it to the prompt.
    :param image_to_edit:
        - If the User is requesting an edit for an image, provide the url for the image they want to edit so it can be included in the prompt.
        - This URL can be for one of the images generated previously by your tool, or the User can provide a publicly accessible URL as well.
    :return:
        - A list of image urls that can be returned to render in the conversation for the User to see and review.
        - These are URLs for a GCP Bucket with 30 day retention, but when the Blog Post is deployed for the first time the image will be installed into the Business' repository.
        - Do not edit the URLs, return them all as is. Use proper markdown image embedding syntax to have the image show up in the chat.
    """
    business_id = tool_context.state.get('model_ref').split('|')[-1]
    client = genai.Client()
    lines = [
        'Generate a hero image for a website for the following Business idea:',
        business_summary,
    ]

    storage_client = storage.Client(AgentSettings.GCP_PROJECT)
    bucket = storage_client.get_bucket(AgentSettings.GENERATED_IMAGE_BUCKET_NAME)

    if user_request:
        lines.append('')
        lines.append('The User has made the following request that you should keep in mind:')
        lines.append(user_request)
    chat_contents: list[Any] = ['\n'.join(lines)]

    if image_to_edit:
        # Download the image from the Bucket and add it to the image
        if AgentSettings.GENERATED_IMAGE_BUCKET_NAME in image_to_edit:
            download_file_name = image_to_edit.rstrip('/').split('/')[-1]
            download_path = f'/tmp/{download_file_name}'
            blob = bucket.blob(download_file_name)
            with open(download_path, 'wb') as fp:
                blob.download_to_file(fp)
            image = Image.open(download_path)
            chat_contents.append(image)
        else:
            # Download the image directly into a temp file and add it to the prompt
            download_path = f'/tmp/{business_id}_{uuid4()}.tmp'
            response = httpx.get(image_to_edit)
            if not response.is_success:
                return {
                    'success': False,
                    'message': 'Could not download the provided image. Response content included.',
                    'response': response.text,
                    'status': response.status_code,
                }
            with open(download_path, 'wb') as fp:
                fp.write(response.content)
            image = Image.open(download_path)
            chat_contents.append(image)

    # Send the request to generate some images
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=chat_contents,
        config=GenerateContentConfig(
            response_modalities=['Image'],
            image_config=ImageConfig(aspect_ratio='16:9'),
        )
    )

    if not response.parts:
        return {
            'success': False,
            'message': 'Gemini API did not appear to return any images. Including their full response object.',
            'response': response.model_dump(),
        }

    image_urls = []
    for part in response.parts:
        if part.inline_data is not None:
            generated_image = part.as_image()
            if not generated_image:
                continue
            if not generated_image.image_bytes:
                continue
            # Generate a random name
            file_name = f'{business_id}_{uuid4()}.png'
            blob = bucket.blob(file_name)
            blob.upload_from_string(generated_image.image_bytes)
            image_urls.append(blob.public_url)
    return {'success': True, 'image_urls': image_urls}
