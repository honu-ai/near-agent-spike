import traceback

import structlog

from google.adk import Agent
from google.adk.tools import BaseTool, FunctionTool, ToolContext, AgentTool
from google.adk.tools import google_search
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams, SseConnectionParams
from honu_google_adk.main import HonuToolSet

from .settings import AgentSettings
from .system_prompt import SYSTEM_PROMPT
from .tools import generate_hero_images

logger = structlog.get_logger('near_agent')


async def pass_tool_errors_back_to_agent(tool: BaseTool, args: dict, tool_context: ToolContext):
    try:
        return await tool.run_async(args=args, tool_context=tool_context)
    except Exception as e:
        logger.error(
            'unhandled_exception',
            tool_name=tool.name,
            args=args,
            exc_info=traceback.format_exc(),
        )
        return {"error": str(e)}


search_agent = Agent(
    name="search_agent",
    model="gemini-2.5-flash",          # Google Search requires a Gemini 2 model
    instruction="You specialize in web research with Google Search.",
    tools=[google_search],
)

root_agent = Agent(
    name="near_agent",
    model="gemini-2.5-pro",
    description=SYSTEM_PROMPT,
    tools=[
        HonuToolSet(AgentSettings.HONU_MCP_HOST, 'model_management'),
        AgentTool(search_agent),
        FunctionTool(generate_hero_images),
        McpToolset(
            connection_params=SseConnectionParams(
                url=AgentSettings.NEAR_MCP_URL,
            ),
        ),
    ],
    before_tool_callback=[pass_tool_errors_back_to_agent],
)

