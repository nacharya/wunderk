from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

import streamlit as st
import asyncio
import nest_asyncio
import atexit
from loguru import logger

from mcp import ClientSession, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import MultiServerMCPClient

from langgraph.prebuilt import create_react_agent
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from typing import Dict, List, Optional, Any


from common.config import ConfigInit
from common.mcp import MCPConfig
from common.llminfo import LLMInfo


# Apply nest_asyncio to allow nested asyncio event loops used for Streamlit's execution model
nest_asyncio.apply()


# Helper functions
def run_async(coro):
    """Run an async function within the stored event loop."""
    return st.session_state.loop.run_until_complete(coro)


async def get_tools_from_client(client: MultiServerMCPClient) -> List[BaseTool]:
    """Get tools from the MCP client."""
    return await client.get_tools()


async def establish_mcp_connection(
    config: Dict[str, Any], mcp_names: List[str]
) -> MultiServerMCPClient:
    """Establish a connection to the MCP servers."""
    if not mcp_names:
        raise ValueError("No MCP server names provided.")

    client = MultiServerMCPClient(config)
    all_tools = client.get_tools()
    st.session_state.client = client
    st.session_state.tools = all_tools
    return client


async def run_agent(agent, message: str) -> Dict:
    """Run the agent with the provided message."""
    return await agent.ainvoke({"messages": message})


async def run_tool(tool, **kwargs):
    """Run a tool with the provided parameters."""
    return await tool.ainvoke(**kwargs)


def on_shutdown():
    # Proper cleanup when the session ends
    if st.session_state.client is not None:
        try:
            # Close the client properly
            run_async(st.session_state.client.__aexit__(None, None, None))
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")


def reset_connection_state():
    """Reset all connection-related session state variables."""
    if st.session_state.client is not None:
        try:
            # Close the existing client properly
            run_async(st.session_state.client.__aexit__(None, None, None))
        except Exception as e:
            print(f"Error closing previous client: {str(e)}")

    st.session_state.client = None
    st.session_state.agent = None
    st.session_state.tools = []


def create_agent(llm, tools: Optional[List[BaseTool]] = None) -> create_react_agent:
    """Create a language model agent with the specified tools."""
    st.session_state.agent = create_react_agent(llm, st.session_state.tools)
    return st.session_state.agent


def create_llm_model(llm_provider: str, api_key: str, model_name: str):
    """Create a language model based on the selected provider."""
    if llm_provider == "OpenAI":
        return ChatOpenAI(
            openai_api_key=api_key,
            model=model_name,
            temperature=0.7,
        )
    elif llm_provider == "Anthropic":
        return ChatAnthropic(
            anthropic_api_key=api_key,
            model=model_name,
            temperature=0.7,
        )
    elif llm_provider == "Google":
        return ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model=model_name,
            temperature=0.7,
            max_tokens=None,
            max_retries=2,
        )
    elif llm_provider == "Ollama":
        return ChatOllama(
            model=model_name,
            temperature=0.7,
            # other params...
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")


def tab_chat(config):
    st.write("chat")
    col1, col2 = st.columns(2)
    llm_selected = col1.checkbox("Use LLM", value=False)
    mcp_selected = col2.checkbox("Use MCP", value=False)
    if llm_selected:
        st.write("LLM selected", st.session_state.llm_provider)
        st.write("Model name", st.session_state.model_name)

    if mcp_selected:
        mcp_config = MCPConfig(config["mcp"]["filename"])
        jconfig = mcp_config.json()
        configs = [jconfig["mcpServers"][name] for name in st.session_state.mcp_names]
        st.write("MCP configs: ", configs)
        # establish a connection to the selected MCPs
        if len(st.session_state.mcp_names) > 0:
            st.session_state.client = run_async(
                establish_mcp_connection(configs, st.session_state.mcp_names)
            )
            st.write("MCP servers connected: ", st.session_state.mcp_names)
            st.write("MCP Tools: ", st.session_state.tools)


def tab_info(config):
    st.write("info")
    st.write("MCP selected names: ", st.session_state.mcp_names)
    st.write("LLM provider: ", st.session_state.llm_provider)
    st.write("Model name: ", st.session_state.model_name)


def tab_model(config):
    col1, col2, col3 = st.columns(3)
    with col1:
        llm_provider = st.selectbox(
            "Select LLM",
            LLMInfo().get_providers(),
            index=0,
            on_change=reset_connection_state,
        )
        noKey = False
        if llm_provider == "Ollama":
            noKey = True
        else:
            api_key = config["keys"][llm_provider]
    with col2:
        # Model selection based on provider
        model_name = st.selectbox(
            "Select Model",
            options=LLMInfo().get_model_list(llm_provider),
            index=0,
            on_change=reset_connection_state,
        )
        st.session_state.llm_provider = llm_provider
        st.session_state.model_name = model_name
        if not noKey:
            st.session_state.api_key = api_key
    with col3:
        st.write("Select MCP Servers")
        mcpctr = st.container()
        mcp_list = []
        mcp_config = MCPConfig(config["mcp"]["filename"])
        mcp_names = mcp_config.get_mcp_names()
        if "mcp_names" not in st.session_state:
            st.session_state.mcp_names = mcp_names
        for i in mcp_names:
            chk = mcpctr.checkbox(i)
            if chk:
                mcp_list.append(i)
        st.session_state.mcp_names = mcp_list
    if len(st.session_state.mcp_names) > 0:
        st.write("Selected MCP servers: ", st.session_state.mcp_names)


def MCPMain(cfg):
    # Session state initialization
    if "client" not in st.session_state:
        st.session_state.client = None
    if "agent" not in st.session_state:
        st.session_state.agent = None
    if "tools" not in st.session_state:
        st.session_state.tools = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "servers" not in st.session_state:
        st.session_state.servers = {}
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "Single Server"
    if "tool_executions" not in st.session_state:
        st.session_state.tool_executions = []
    if "loop" not in st.session_state:
        st.session_state.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(st.session_state.loop)

    atexit.register(on_shutdown)
    config = cfg.json()
    logger.debug("MCP")
    model_tab, chat_tab, info_tab = st.tabs(["Models", "Chat", "Info"])
    with model_tab:
        tab_model(config)
    with chat_tab:
        tab_chat(config)
    with info_tab:
        tab_info(config)


if __name__ == "__main__":
    cfg = ConfigInit("wui")
    MCPMain(cfg)
