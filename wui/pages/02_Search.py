import streamlit as st

from common.config import ConfigInit

from qdrant_client import QdrantClient
from loguru import logger


def SearchUI(cfg):
    config = cfg.json()
    qclient = QdrantClient(
        url=f"http://{config['qdrant']['host']}:{config['qdrant']['port']}"
    )
    if "search_text" not in st.session_state:
        st.session_state.search_text = ""
    instr = ""
    with st.form("search_form"):
        col1, col2 = st.columns([7, 1])
        with col1:
            query = st.text_input(
                instr, value=instr, placeholder="Search", label_visibility="collapsed"
            )
            if query != st.session_state.search_text:
                st.session_state.search_text = query
    with col2:
        submitted = st.form_submit_button("Search")

    if query and submitted:
        logger.debug(f"Searching for: {query}")
        st.write("Searching...", query)


if __name__ == "__main__":
    try:
        cfg = ConfigInit("wui")
        SearchUI(cfg)
    except Exception as e:
        st.error(str(e))
        logger.error(str(e))
        st.stop()
