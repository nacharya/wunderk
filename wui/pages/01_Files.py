import os
import streamlit as st
from common.config import ConfigInit
from common.files import Directory
from common.llminfo import LLMInfo
from loguru import logger
from streamlit_js_eval import streamlit_js_eval


def read_markdown(filename):
    with open(filename, "r") as f:
        content = f.read()
    return content


def FilesBrowse(dirc, selector_name):
    df = dirc.df(dirc.files("*"))
    df.drop(columns=["Parent"], inplace=True)
    df["Select"] = False
    st.session_state[dirc.dirname] = df
    edited_df = st.data_editor(
        df,
        key=selector_name,
        hide_index=True,
        column_config={
            "Select": st.column_config.CheckboxColumn(),
            "Type": st.column_config.TextColumn(),
        },
        use_container_width=True,
    )
    return edited_df


def FileViewActions(dirc, edited_df):
    file_selected = False
    col1, col2, col3 = st.columns(3)
    with col1:
        actctr1 = st.container()
        actctr1.dataframe(
            edited_df[edited_df["Select"]]["File"].tolist(), use_container_width=True
        )
    with col2:
        actctr2 = st.container()
        action = actctr2.selectbox(
            "Actions",
            ("View", "Convert", "Analyze", "Summarize", "Translate"),
            label_visibility="collapsed",
        )
    with col3:
        match action:
            case "View":
                file_selected = True
                file_name = edited_df[edited_df["Select"]].iloc[0]["File"]
                st.session_state["file_selected"] = file_name
                st.session_state["view_action"] = "View"
                view_type = st.selectbox(
                    "Select View Type",
                    ("None", "Markdown", "Image"),
                    key="view_type_selector",
                    label_visibility="collapsed",
                )
                logger.debug(f"Selected view type: {view_type}")
            case "Convert":
                dirc.convert_files(edited_df[edited_df["Select"]])
                file_type = st.selectbox(
                    "Select File Type",
                    ("Text", "Markdown", "Image", "PDF"),
                    key="file_type_selector",
                    label_visibility="collapsed",
                )
                logger.debug(f"Selected file type for conversion: {file_type}")
                st.toast("Filed converted!", icon="ℹ️")
                # streamlit_js_eval(js_expressions="parent.window.location.reload()")
            case "Analyze":
                file_selected = True
                file_name = edited_df[edited_df["Select"]].iloc[0]["File"]
                st.session_state["file_selected"] = file_name
                st.session_state["view_action"] = "Analyze"
                anal_type = st.selectbox(
                    "Select Analysis Type",
                    ("Sentiment", "Topic", "Summary"),
                    key="analysis_type_selector",
                    label_visibility="collapsed",
                )
                logger.debug(f"Selected analysis type: {anal_type}")
            case "Summarize":
                file_selected = True
                file_name = edited_df[edited_df["Select"]].iloc[0]["File"]
                st.session_state["file_selected"] = file_name
                st.session_state["view_action"] = "Summarize"
                summ_type = st.selectbox(
                    "Select Summary Type",
                    ("Short", "Medium", "Long"),
                    key="summary_type_selector",
                    label_visibility="collapsed",
                )
                logger.debug(f"Selected summary type: {summ_type}")
            case "Translate":
                file_selected = True
                file_name = edited_df[edited_df["Select"]].iloc[0]["File"]
                st.session_state["file_selected"] = file_name
                st.session_state["view_action"] = "Translate"
                st.toast("Filed translated!", icon="ℹ️")
                lang_type = st.selectbox(
                    "Select Language",
                    (
                        "English",
                        "Spanish",
                        "French",
                        "German",
                        "Hindi",
                        "Nepali",
                        "Tamil",
                        "Japanese",
                    ),
                    key="language_type_selector",
                    label_visibility="collapsed",
                )
                logger.debug(f"Selected language type: {lang_type}")
            case _:
                logger.warning("Need a valid selection")

    if file_selected and st.session_state["view_action"] == "View":
        file = st.session_state["file_selected"]
        if view_type == "Markdown":
            mdbuf = read_markdown(dirc.fullpath(file))
            with st.expander("File Details", expanded=True):
                st.markdown(mdbuf, unsafe_allow_html=True)
    if file_selected and st.session_state["view_action"] == "Summarize":
        file = st.session_state["file_selected"]
        colx1, colx2 = st.columns(2)
        with colx1:
            option = st.selectbox(
                "Select the LLM", LLMInfo().get_providers(), key="llm_provider_selector"
            )
        with colx2:
            modelname = st.selectbox(
                "Select a Model", LLMInfo().get_model_list(option), key="model_selector"
            )

        sbutton = st.button("Summarize", key="summarize_button")
        if sbutton:
            with st.expander("File Details", expanded=True):
                st.write("Using Model: ", modelname, " from Provider: ", option)
                st.write("File: ", file, " for summarization. Please wait...")
            st.toast("File summarized!", icon="ℹ️")
            # streamlit_js_eval(js_expressions="parent.window.location.reload()")
    if file_selected and st.session_state["view_action"] == "Translate":
        file = st.session_state["file_selected"]
        colx1, colx2 = st.columns(2)
        with colx1:
            option = st.selectbox("Select the LLM", LLMInfo().get_providers())
        with colx2:
            modelname = st.selectbox(
                "Select a Model", LLMInfo().get_model_list(option), key="model_selector"
            )
        sbutton = st.button("Translate", key="summarize_button")
        if sbutton:
            with st.expander("File Details", expanded=True):
                st.write("Using Model: ", modelname, " from Provider: ", option)
                st.write("File: ", file, " for summarization. Please wait...")
            st.toast("File translated!", icon="ℹ️")
            # streamlit_js_eval(js_expressions="parent.window.location.reload()")
    if file_selected and st.session_state["view_action"] == "Analyze":
        file = st.session_state["file_selected"]
        colx1, colx2 = st.columns(2)
        with colx1:
            option = st.selectbox("Select the LLM", LLMInfo().get_providers())
        with colx2:
            modelname = st.selectbox(
                "Select a Model", LLMInfo().get_model_list(option), key="model_selector"
            )
        sbutton = st.button("Analyze", key="analyze_button")
        if sbutton:
            with st.expander("File Details", expanded=True):
                st.write("Using Model: ", modelname, " from Provider: ", option)
                st.write("File: ", file, " for summarization. Please wait...")
            st.toast("File analyzed!", icon="ℹ️")
            # streamlit_js_eval(js_expressions="parent.window.location.reload()")


def FileManageActions(dirc, edited_df):
    col1, col2, col3 = st.columns(3)
    with col1:
        actctr1 = st.container()
        actctr1.dataframe(
            edited_df[edited_df["Select"]]["File"].tolist(), use_container_width=True
        )
    with col2:
        actctr2 = st.container()
        action = actctr2.selectbox(
            "Actions",
            (
                "Delete",
                "Move",
                "Metadata",
                "Rename",
                "Copy",
            ),
            label_visibility="collapsed",
        )
    with col3:
        actctr3 = st.container()
        match action:
            case "Delete":
                dbutton = actctr3.button("Delete")
                if dbutton:
                    dirc.delete_files(edited_df[edited_df["Select"]])
                    st.toast("Filed deleted!", icon="ℹ️")
                    streamlit_js_eval(js_expressions="parent.window.location.reload()")
            case "Move":
                mdest = actctr3.text_input(
                    "Enter destination directory to move files",
                    value=dirc.dirname,
                    placeholder="e.g. /path/to/destination",
                    label_visibility="collapsed",
                )
                dbutton = actctr3.button("Move")
                if dbutton:
                    if len(mdest) > 0:
                        if not os.path.exists(mdest):
                            st.toast("Destination directory does not exist!", icon="⚠")
                            os.makedirs(mdest, exist_ok=True)
                        if not mdest.endswith("/"):
                            mdest += "/"
                        dirc.move_files(edited_df[edited_df["Select"]], mdest)
                        st.toast("File moved!", icon="ℹ️")
                        streamlit_js_eval(
                            js_expressions="parent.window.location.reload()"
                        )
            case "Metadata":
                dbutton = actctr3.button("Metadata")
                if dbutton:
                    file_meta_df = dirc.metadata_files(edited_df[edited_df["Select"]])

            case "Rename":
                new_name = actctr3.text_input(
                    "Enter new name for the file",
                    value=edited_df[edited_df["Select"]].iloc[0]["File"],
                    placeholder="e.g. new_file_name.txt",
                    label_visibility="collapsed",
                )
                dbutton = actctr3.button("Rename")
                if dbutton:
                    if len(new_name) > 0:
                        dirc.rename_files(edited_df[edited_df["Select"]], new_name)
                        st.toast("File renamed!", icon="ℹ️")
                        streamlit_js_eval(
                            js_expressions="parent.window.location.reload()"
                        )
            case "Copy":
                mdest = actctr3.text_input(
                    "Enter destination directory to copy files",
                    value=dirc.dirname,
                    placeholder="e.g. /path/to/destination",
                    label_visibility="collapsed",
                )
                dbutton = actctr3.button("Copy")
                if dbutton:
                    if len(mdest) > 0:
                        if not os.path.exists(mdest):
                            st.toast("Destination directory does not exist!", icon="⚠")
                            os.makedirs(mdest, exist_ok=True)
                        if not mdest.endswith("/"):
                            mdest += "/"
                        dirc.copy_files(edited_df[edited_df["Select"]], mdest)
                        st.toast("File copied!", icon="ℹ️")
                        streamlit_js_eval(
                            js_expressions="parent.window.location.reload()"
                        )
            case _:
                logger.warning("Need a valid selection")
    if action == "Metadata":
        file_meta_df = dirc.metadata_files(edited_df[edited_df["Select"]])
        with st.expander("File Metadata", expanded=True):
            st.dataframe(
                file_meta_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "File": st.column_config.TextColumn(),
                    "Size (bytes)": st.column_config.NumberColumn(),
                    "Created": st.column_config.TextColumn(),
                    "Modified": st.column_config.TextColumn(),
                    "Accessed": st.column_config.TextColumn(),
                    "Permissions": st.column_config.TextColumn(),
                    "Owner": st.column_config.TextColumn(),
                    "Group": st.column_config.TextColumn(),
                    "Inode": st.column_config.TextColumn(),
                    "Device": st.column_config.TextColumn(),
                    "Links": st.column_config.NumberColumn(),
                    "File Type": st.column_config.TextColumn(),
                    "Path": st.column_config.TextColumn(),
                },
            )


def FileIndexActions(config, dirc, edited_df):
    qdrant_url = f"http://{config['qdrant']['host']}:{config['qdrant']['port']}"
    col1, col2, col3 = st.columns(3)
    with col1:
        actctr1 = st.container()
        actctr1.dataframe(
            edited_df[edited_df["Select"]]["File"].tolist(), use_container_width=True
        )
    with col2:
        actctr2 = st.container()
        action = actctr2.selectbox(
            "Actions",
            ("Vectorize", "Convert", "Context", "Collection"),
            label_visibility="collapsed",
        )
    with col3:
        actctr3 = st.container()
        match action:
            case "Vectorize":
                cname = actctr3.text_input(
                    "Enter collection name for files",
                    value=dirc.dirname,
                    placeholder="e.g. collection_name",
                    label_visibility="collapsed",
                )
                dbutton = actctr3.button("Vectorize")
                if dbutton:
                    dirc.vectorize_files(
                        edited_df[edited_df["Select"]], cname, qdrant_url
                    )
                    st.toast("Files Vectorized!", icon="ℹ️")
                    streamlit_js_eval(js_expressions="parent.window.location.reload()")

            case "Convert":
                dbutton = actctr3.button("Convert")
                if dbutton:
                    dirc.convert_files(edited_df[edited_df["Select"]])
                    st.toast("Filed converted!", icon="ℹ️")
                    streamlit_js_eval(js_expressions="parent.window.location.reload()")

            case "Context":
                cname = actctr3.text_input(
                    "Enter context name for files",
                    value=dirc.dirname,
                    placeholder="e.g. context_name",
                    label_visibility="collapsed",
                )
                dbutton = actctr3.button("Context")
                if dbutton:
                    # TODO
                    dirc.addfiles_context(edited_df[edited_df["Select"]], cname)
                    st.toast("Filed added to context!", icon="ℹ️")
                    streamlit_js_eval(js_expressions="parent.window.location.reload()")

            case "Collection":
                cname = actctr3.text_input(
                    "Enter collection name for files",
                    value=dirc.dirname,
                    placeholder="e.g. collection_name",
                    label_visibility="collapsed",
                )
                dbutton = actctr3.button("Collecition")
                if dbutton:
                    if len(cname) > 0:
                        st.write("Collection Name: ", cname)
                    st.toast("Files Collected!", icon="ℹ️")
                    streamlit_js_eval(js_expressions="parent.window.location.reload()")

            case _:
                logger.warning("Need a valid selection")


def tab_view(config):
    dirpath = st.session_state.get("filesdirpath")
    dirc = Directory(dirpath, "")
    edited_df = FilesBrowse(dirc, "view_selector")
    if len(edited_df[edited_df["Select"]]) > 0:
        FileViewActions(dirc, edited_df)
    return


def tab_manage(config):
    dirpath = st.session_state["filesdirpath"]
    if not dirpath:
        dirpath = config["datadir"] + "/files"
        st.session_state["filesdirpath"] = dirpath
    dirc = Directory(dirpath, "")
    ctr1 = st.container()
    up_files = ctr1.file_uploader(
        "Choose your files to upload", accept_multiple_files=True, key="file_uploader"
    )
    if up_files is not None:
        for file in up_files:
            ctr1.write(file)
            bytes_data = file.read()
            filename = dirc.dirname + "/" + file.name
            with open(filename, "wb") as f:
                f.write(bytes_data)
    edited_df = FilesBrowse(dirc, "upload_selector")
    if len(edited_df[edited_df["Select"]]) > 0:
        FileManageActions(dirc, edited_df)
    return


def tab_index(config):
    dirpath = st.session_state["filesdirpath"]
    if not dirpath:
        dirpath = config["datadir"] + "/files"
        st.session_state["filesdirpath"] = dirpath
    dirc = Directory(dirpath, "")
    edited_df = FilesBrowse(dirc, "index_selector")
    if len(edited_df[edited_df["Select"]]) > 0:
        FileIndexActions(config, dirc, edited_df)
    return


def FileMain(config):
    datadir = config["datadir"]
    filesdirpath = datadir + "/files"
    st.session_state["filesdirpath"] = filesdirpath
    topctr = st.container()
    col1, col2, col3 = topctr.columns(3)
    with col1:
        st.write("📁", st.session_state["filesdirpath"])
    with col2:
        folder_choice = st.selectbox(
            "Select Folder",
            ["Current Folder", "Change Folder", "New Folder"],
            key="folder_choice",
            label_visibility="collapsed",
        )
    with col3:
        if folder_choice == "Change Folder":
            sdirs = ["None"] + Directory(st.session_state["filesdirpath"], "").subdirs()
            logger.debug(f"Subdirectories: {sdirs}")
            subdirname = st.selectbox(
                "Select a subdirectory",
                sdirs,
                key="subdir_selector",
                label_visibility="collapsed",
            )
            if subdirname and subdirname != "None":
                st.session_state["filesdirpath"] = (
                    st.session_state["filesdirpath"] + "/" + subdirname
                )
                streamlit_js_eval(js_expressions="parent.window.location.reload()")
        elif folder_choice == "New Folder":
            new_folder_name = st.text_input(
                "Enter new folder name",
                value="",
                placeholder="e.g. new_folder",
                label_visibility="collapsed",
            )
            if new_folder_name:
                new_folder_path = os.path.join(
                    st.session_state["filesdirpath"], new_folder_name
                )
                if not os.path.exists(new_folder_path):
                    os.makedirs(new_folder_path, exist_ok=True)
                    st.session_state["filesdirpath"] = new_folder_path
                    st.toast("New folder created!", icon="ℹ️")
                    streamlit_js_eval(js_expressions="parent.window.location.reload()")
                else:
                    st.toast("Folder already exists!", icon="⚠")
            else:
                st.toast("Please enter a folder name!", icon="⚠")
        elif folder_choice == "Current Folder":
            pass  # do nothing
    view_tab, upload_tab, index_tab = st.tabs(["View", "Manage", "Index"])
    with view_tab:
        tab_view(config)
    with upload_tab:
        tab_manage(config)
    with index_tab:
        tab_index(config)


def main():
    try:
        cfg = ConfigInit("wui")
        FileMain(cfg.json())
    except Exception as e:
        st.error(str(e))
        logger.error(str(e))


if __name__ == "__main__":
    main()
