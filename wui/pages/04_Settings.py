import streamlit as st
import os
import pandas as pd
from common.config import ConfigInit
from common.vectordb import VectorDB
from common.mcp import MCPConfig

from loguru import logger

# st.set_page_config(
#    page_title="Settings",
#    page_icon=os.path.join("images", "favicon.ico"),
#    layout="wide",
#    menu_items=None,
# )
# st.title("⚙️ Settings")


def CollectionsUI(cfg):
    config = cfg.json()
    vurl = f"http://{config['qdrant']['host']}:{config['qdrant']['port']}"
    vdb = VectorDB(vurl)

    list_ctr = st.container()
    list_ctr.dataframe(
        vdb.collections_df(),
        column_config={
            "Collection": st.column_config.TextColumn(),
            "Status": st.column_config.TextColumn(),
        },
        use_container_width=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Create Collection")
        create_ctr = st.container()
        col_name = create_ctr.text_input("Collection Name")
        if create_ctr.button("Create"):
            vdb.create_collection(col_name)
            st.success(f"Collection {col_name} created successfully")
    with col2:
        st.subheader("Delete Collection")
        delete_ctr = st.container()
        all = st.checkbox("Select all")
        if all:
            selected_collections = delete_ctr.multiselect(
                "Select one or more collections:", vdb.collections(), vdb.collections()
            )
        else:
            selected_collections = delete_ctr.multiselect(
                "Select one or more collections:", vdb.collections()
            )
        if delete_ctr.button("Delete"):
            for col_name in selected_collections:
                vdb.delete_collection(col_name)
                st.success(f"Collection {col_name} deleted successfully")
    return


def tab_data(config):
    col1, col2 = st.columns(2)
    with col1:
        setctr1 = st.container()
        config["name"] = setctr1.text_input("Name", value=config["name"])
    with col2:
        setctr2 = st.container()
        config["datadir"] = setctr2.text_input(
            "Data Directory", value=config["datadir"]
        )
    subdir_check = st.checkbox("Subdirectories")
    if subdir_check:
        subdir_ctr = st.container()
        config["subdirs"] = subdir_ctr.text_input(
            "Subdirectories", value=config["subdirs"]
        )


def tab_vector(config):
    col1, col2 = st.columns(2)
    with col1:
        config["ollama"]["host"] = st.text_input(
            "Ollama Host", value=config["ollama"]["host"]
        )
        config["qdrant"]["host"] = st.text_input(
            "Qdrant Host", value=config["qdrant"]["host"]
        )
    with col2:
        config["ollama"]["port"] = st.number_input(
            "Ollama Port", value=config["ollama"]["port"], step=1
        )
        config["qdrant"]["port"] = st.number_input(
            "Qdrant Port", value=config["qdrant"]["port"], step=1
        )
    dashboard = st.checkbox("Qdrant Dashboard")
    if dashboard:
        col1, col2 = st.columns(2)
        with col1:
            dashboard_ctr = st.container()
            url = dashboard_ctr.text_input(
                "Dashboard URL",
                value=f"http://{config['qdrant']['host']}:{config['qdrant']['port']}/dashboard",
                label_visibility="collapsed",
            )
        with col2:
            st.link_button(url=url, label="Qdrant Dashboard")
        collection_mgmt = st.checkbox("Manage Collections")
        if collection_mgmt:
            CollectionsUI(cfg)


def tab_mcp(config):
    mcp_config = MCPConfig(config["mcp"]["filename"])

    with st.container():
        st.subheader("MCP Servers")
        if "mcp_name" not in st.session_state:
            st.session_state["mcp_name"] = None
        col1, col2, col3 = st.columns(3)
        with col1:
            slist = mcp_config.get_mcp_names()
            option = st.selectbox(
                "Select the MCP",
                slist,
                label_visibility="collapsed",
            )
            if option:
                st.session_state["mcp_name"] = option
                mcp_instance = mcp_config.get_mcp_instance(option)
                st.session_state["mcp_instance"] = mcp_instance
        with col2:
            actctr2 = st.container()
            action = actctr2.selectbox(
                "Actions",
                ("View", "Edit", "Delete", "Add"),
                label_visibility="collapsed",
            )
        with col3:
            if "mcp_action" not in st.session_state:
                st.session_state["mcp_action"] = "View"
            st.session_state["mcp_action"] = action

    mcp_instance = MCPInstance(
        name=st.session_state.get("mcp_name", None),
        mcp_instance=st.session_state.get("mcp_instance", {}),
    )
    mcp_instance.display(action=st.session_state.get("mcp_action", "View"))


class MCPInstance:
    def __init__(self, name, mcp_instance):
        self.name = name
        self.mcp_instance = mcp_instance

    def display(self, action=None):
        """Display MCP instance details based on the action."""
        match action:
            case "Add":
                self.new()
            case "Edit":
                self.edit()
            case "Delete":
                self.delete()
            case "View":
                self.view_ro()
            case _:
                logger.debug(f"Unknown action: {action}")
                self.view_ro()

    def view_ro(self):
        """Display MCP instance details in a box."""
        logger.debug(f"Viewing MCP instance: {self.name}")
        with st.expander(f"**MCP Instance: {self.name}**", expanded=True):
            st.text_input("type", self.mcp_instance.type, disabled=True)
            st.text_input("command", self.mcp_instance.command, disabled=True)
            st.text_input("args", self.mcp_instance.args, disabled=True)
            st.text_input("env", self.mcp_instance.env, disabled=True)
            st.text_input("timeout", str(self.mcp_instance.timeout), disabled=True)
            if hasattr(self.mcp_instance, "serverUrl"):
                st.text_input("serverUrl", self.mcp_instance.serverUrl, disabled=True)
            else:
                self.mcp_instance.serverUrl = ""
                st.text_input("serverUrl", self.mcp_instance.serverUrl, disabled=True)
            if hasattr(self.mcp_instance, "transport"):
                st.text_input("transport", self.mcp_instance.transport, disabled=True)
            else:
                self.mcp_instance.transport = "http"
                st.text_input("transport", self.mcp_instance.transport, disabled=True)
            if hasattr(self.mcp_instance, "sse_timeout"):
                st.text_input(
                    "sse_timeout", str(self.mcp_instance.sse_timeout), disabled=True
                )
            else:
                self.mcp_instance.sse_timeout = 60
                st.text_input(
                    "sse_timeout", str(self.mcp_instance.sse_timeout), disabled=True
                )
            st.text_input("headers", self.mcp_instance.headers, disabled=True)

    def edit(self):
        """Edit MCP instance details."""
        with st.expander(f"**Edit MCP Instance: {self.name}**", expanded=True):
            self.mcp_instance.type = st.selectbox(["stdio", "sse"])
            if self.mcp_instance.type == "stdio":
                self.mcp_instance.command = st.text_input(
                    "Command", self.mcp_instance.command
                )
                self.mcp_instance.args = st.data_editor(
                    self.mcp_instance.args,
                    column_config={"value": st.column_config.TextColumn()},
                )
                self.mcp_instance.env = st.data_editor(
                    self.mcp_instance.env,
                    column_config={
                        "key": st.column_config.TextColumn(),
                        "value": st.column_config.TextColumn(),
                    },
                )
            elif self.mcp_instance.type == "sse":
                self.mcp_instance.serverUrl = st.text_input(
                    "Server URL", self.mcp_instance.serverUrl
                )
                self.mcp_instance.transport = st.selectbox(
                    "Transport", ["http", "websocket"], index=0
                )
                self.mcp_instance.sse_timeout = st.number_input(
                    "SSE Timeout", value=self.mcp_instance.sse_timeout, step=1
                )
            else:
                logger.error(f"Unknown MCP type: {self.mcp_instance.type}")
                st.error(f"Unknown MCP type: {self.mcp_instance.type}")
                return
            self.mcp_instance.timeout = st.number_input(
                "Timeout", value=self.mcp_instance.timeout, step=1
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Changes"):
                    st.success(f"MCP Instance {self.name} updated successfully")
            with col2:
                if st.button("Cancel"):
                    st.session_state["mcp_action"] = "View"
                    st.session_state["mcp_name"] = None
                    st.session_state["mcp_instance"] = {}
                    st.success("Changes cancelled")

    def delete(self):
        """Delete MCP instance."""
        if st.button(f"Delete MCP Instance: {self.name}"):
            st.session_state["mcp_instance"] = None
            st.success(f"MCP Instance {self.name} deleted successfully")

    def new(self):
        """Create a new MCP instance."""
        with st.expander("New MCP Instance", expanded=True):
            self.name = st.text_input("Name")
            self.mcp_instance = {
                "type": st.text_input("Type"),
                "command": st.text_input("Command"),
                "args": st.data_editor(
                    self.mcp_instance.args,
                    column_config={"value": st.column_config.TextColumn()},
                ),
                "env": st.data_editor(
                    self.mcp_instance.env,
                    column_config={
                        "key": st.column_config.TextColumn(),
                        "value": st.column_config.TextColumn(),
                    },
                ),
                "timeout": st.number_input("Timeout", value=30, step=1),
                "serverUrl": st.text_input("Server URL"),
                "transport": st.text_input("Transport"),
                "sse_timeout": st.number_input("SSE Timeout", value=60, step=1),
                "headers": st.data_editor(
                    self.mcp_instance.headers,
                    column_config={
                        "key": st.column_config.TextColumn(),
                        "value": st.column_config.TextColumn(),
                    },
                ),
            }

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Create"):
                    st.success(f"MCP Instance {self.name} created successfully")
            with col2:
                if st.button("Cancel"):
                    st.session_state["mcp_action"] = "View"
                    st.session_state["mcp_name"] = None
                    st.session_state["mcp_instance"] = {}
                    st.success("Creation cancelled")


def SettingsMain(config):
    main_tab, vector_tab, mcp_tab = st.tabs(["Data", "VectorDB", "MCP"])
    with main_tab:
        tab_data(config)
    with vector_tab:
        tab_vector(config)
    with mcp_tab:
        tab_mcp(config)


if __name__ == "__main__":
    try:
        cfg = ConfigInit("wui")
        SettingsMain(cfg.json())
    except Exception as e:
        st.error(str(e))
        logger.error(str(e))
