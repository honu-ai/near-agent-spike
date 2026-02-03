# Honu x Near Agent Spike

A simple test Agent that showcases the interconectionality between Honu Agents and the NEAR Protocol by charging NEAR for performing services to the User's happiness.
Currently as a demonstration this agent is designed to read the Business Objects to help generate Hero Images for the User's Website

## Requirements
- Docker
- Ngrok
- NEAR MCP Server
- Near Keystore for the Business' Wallet
  - For the testcase you may need to work with the Agent to manually import your Business' private key into the system but this will be improved later
- Google Cloud Account with a Storage Bucket and a Gemini API Key

## Setting Up
- You will need 3 Terminal Tabs to run this system.
- Tab 1; Spin up the Near MCP Server using SSE and the Keystore;
  - `npx @nearai/near-mcp@latest run --port 4000 --remote --key-dir /path/to/keystore`
- Rename `.env.example` to `.env` and populate the required fields;
  - `GCP_PROJECT` is the name of your project in Google Cloud
  - `GOOGLE_API_KEY` is the API Key for Gemini
  - `GENERATED_IMAGE_BUCKET_NAME` is the name of the Bucket to store the generated images in.
- Tab 2; Run `docker compose up` to spin up the Agent Container
- Tab 3; Run `ngrok http 7999`
  - Copy the URL from the output of this command
  - Go to `https://hap.honutech.dev`, navigate to your model and under `Engage` click `Engage external agent`
  - As the `base_url`, input the copied URL
  - As the `app_name`, input `near_agent`
  - Click confirm, and open the chat sidebar. The agent should appear shortly with an introduction message.
