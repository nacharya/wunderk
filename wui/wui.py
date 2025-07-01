import os
import re
import streamlit as st
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai.chat_models import ChatOpenAI

# from langchain_ollama import OllamaLLM, ChatOllama
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from common.config import ConfigInit
from common.llminfo import LLMInfo
from loguru import logger


def wui_llm():
    modellist = LLMInfo().modellist
    col1, col2 = st.columns(2)
    with col1:
        option = st.selectbox("Select the LLM", LLMInfo().get_providers())
    with col2:
        modelname = st.selectbox("Select a Model", modellist[option])
    config = cfg.json()
    ollama_base = f"http://{config['ollama']['host']}:{config['ollama']['port']}"
    openai_api_key = st.session_state.get("openai_api_key", "")
    template = """Question: {question}
    Instructions: {instructions}"""
    with st.form("my_form"):
        qtext = st.text_area("Enter question:", "Please tell me a joke")
        instext = st.text_area("Enter instructions:", "Please be brief")
        submitted = st.form_submit_button("Submit")
        if submitted:
            match option:
                case "OpenAI":
                    if not openai_api_key.startswith("sk-"):
                        st.warning("Please configure valid OpenAI API key!", icon="⚠")
                    else:
                        prompt = ChatPromptTemplate.from_template(template)
                        llm = ChatOpenAI(api_key=openai_api_key, model=modelname)
                        parser = StrOutputParser()
                        chain = prompt | llm | parser
                        st.info(
                            chain.invoke({"question": qtext, "instructions": instext})
                        )
                case "Google":
                    os.environ["GOOGLE_API_KEY"] = config["keys"]["Google"]
                    prompt = ChatPromptTemplate.from_template(template)
                    llm = ChatGoogleGenerativeAI(
                        model=modelname, google_api_key=config["keys"]["Google"]
                    )
                    parser = StrOutputParser()
                    chain = prompt | llm | parser
                    st.info(chain.invoke({"question": qtext, "instructions": instext}))
                case "Anthropic":
                    os.environ["ANTHROPIC_API_KEY"] = config["keys"]["Anthropic"]
                    prompt = ChatPromptTemplate.from_template(template)
                    llm = ChatAnthropic(model=modelname)
                    parser = StrOutputParser()
                    chain = prompt | llm | parser
                    st.info(chain.invoke({"question": qtext, "instructions": instext}))
                case "Ollama":
                    prompt = ChatPromptTemplate.from_template(template)
                    # llm = OllamaLLM(model=modelname, base_url=ollama_base)
                    llm = ChatOllama(model=modelname, base_url=ollama_base)
                    parser = StrOutputParser()
                    chain = prompt | llm | parser
                    llm_response = chain.invoke(
                        {"question": qtext, "instructions": instext}
                    )
                    if modelname.startswith("deepseek"):
                        cleaned = re.sub(
                            r"<think>.*?</think>", "", llm_response, flags=re.DOTALL
                        )
                        st.info(cleaned)
                    else:
                        st.info(llm_response)
                case _:
                    st.warning("Unknown Model", icon="⚠")


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def login():
    if st.button("Log in"):
        st.session_state.logged_in = True
        st.rerun()


def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()


def wui_main(cfg):
    config = cfg.json()
    st.session_state["openai_api_key"] = config["keys"]["OpenAI"]
    st.session_state["datadir"] = cfg.getv("datadir")
    pages = [
        st.Page(wui_llm, title="LLM", icon="💬"),
        st.Page("pages/01_Files.py", title="Files", icon="📁"),
        st.Page("pages/02_Search.py", title="Search", icon="🔍"),
        st.Page("pages/03_MCP.py", title="MCP", icon="📦"),
        st.Page(
            "pages/04_Settings.py",
            title="Settings",
            icon="⚙️",
        ),
    ]
    if st.session_state.logged_in:
        pages.append(st.Page(logout, title="Log out", icon=":material/logout:"))
    else:
        pages.append(st.Page(login, title="Log in", icon=":material/login:"))

    current_page = st.navigation(pages=pages, position="hidden")
    st.set_page_config(layout="wide")
    num_cols = max(len(pages) + 1, 8)
    columns = st.columns(num_cols, vertical_alignment="center")
    columns[0].write("**Wunderk**")
    for col, page in zip(columns[1:], pages):
        col.page_link(page, icon=page.icon)
    st.title(f"{current_page.icon} {current_page.title}")
    current_page.run()


if __name__ == "__main__":
    try:
        cfg = ConfigInit("wui")
        wui_main(cfg)
    except Exception as e:
        logger.error(str(e))
        st.error(str(e))
