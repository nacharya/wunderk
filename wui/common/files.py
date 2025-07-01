"""
Directory: Utility class for file and directory operations (listing, metadata, copy/move, vectorization, etc).
"""

import os
import pathlib
import shutil
import time
from typing import List, Tuple
import pandas as pd
from loguru import logger
from markitdown import MarkItDown
from .embed import EmbeddingDocuments


class Directory:
    def __init__(self, basedir: str, rootdir: str):
        self.rootdir = rootdir
        self.basedir = basedir
        self.dirname = os.path.join(basedir, rootdir)
        self.basepath = pathlib.Path(self.dirname)

    def files(self, pattern: str) -> List[Tuple[str, str, str, str]]:
        """List files matching pattern."""
        all_files = []
        for i in self.basepath.rglob(pattern):
            parent = i.parent.name
            sname = str(i.relative_to(self.dirname))
            ftype = (
                "📂 Directory"
                if i.is_dir()
                else "🗒️ File"
                if i.is_file()
                else "🔗 Symlink"
                if i.is_symlink()
                else ""
            )
            stime = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(i.stat().st_ctime)
            )
            all_files.append((sname, ftype, parent, stime))
        return all_files

    def subdirs(self) -> List[str]:
        """List subdirectories."""
        return [i.name for i in self.basepath.iterdir() if i.is_dir()]

    def fullpath(self, file: str) -> str:
        return os.path.join(self.dirname, file)

    def df(self, filelist: List[Tuple[str, str, str, str]]) -> pd.DataFrame:
        return pd.DataFrame(filelist, columns=["File", "Type", "Parent", "Created"])

    def delete_files(self, df):
        """Delete files or directories listed in DataFrame."""
        for f in df["File"]:
            fname = self.fullpath(f)
            logger.info(f"Deleting {fname}")
            if os.path.isfile(fname):
                os.remove(fname)
            elif os.path.isdir(fname):
                shutil.rmtree(fname)

    def metadata_files(self, df):
        """Return metadata DataFrame for files in df."""
        metadata = []
        for f in df["File"]:
            fname = self.fullpath(f)
            file_stats = os.stat(fname)
            metadata.append(
                {
                    "File": f,
                    "Size (bytes)": file_stats.st_size,
                    "Created": time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(file_stats.st_ctime)
                    ),
                    "Modified": time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(file_stats.st_mtime)
                    ),
                    "Accessed": time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(file_stats.st_atime)
                    ),
                    "Permissions": oct(file_stats.st_mode)[-3:],
                    "Owner": file_stats.st_uid,
                    "Group": file_stats.st_gid,
                    "Inode": file_stats.st_ino,
                    "Device": file_stats.st_dev,
                    "Links": file_stats.st_nlink,
                    "File Type": "Directory" if os.path.isdir(fname) else "File",
                    "Path": fname,
                }
            )
        df = pd.DataFrame(metadata)
        df.set_index("Path", inplace=True)
        return df

    def rename_file(self, df, new_name):
        """Rename a single file."""
        if len(df) != 1:
            logger.error("Rename requires exactly one file selected.")
            return
        old_name = df["File"].iloc[0]
        old_full_path = self.fullpath(old_name)
        new_full_path = os.path.join(self.dirname, new_name)
        if os.path.exists(new_full_path):
            logger.error(f"File {new_full_path} already exists.")
            return
        os.rename(old_full_path, new_full_path)
        logger.info(f"Renamed {old_name} to {new_name}")

    def copy_files(self, df, dest):
        """Copy files to destination directory."""
        for f in df["File"]:
            fname = self.fullpath(f)
            destname = os.path.join(self.basedir, os.path.join(dest, f))
            if os.path.isfile(fname):
                shutil.copy2(fname, destname)
            elif os.path.isdir(fname):
                shutil.copytree(fname, destname, dirs_exist_ok=True)

    def move_files(self, df, dest):
        """Move files to destination directory."""
        for f in df["File"]:
            fname = self.fullpath(f)
            destname = os.path.join(self.basedir, os.path.join(dest, f))
            shutil.move(fname, destname)

    def addfiles_context(self, df, context):
        logger.info(f"Adding context to files in {context}")
        # TODO: Implement context addition logic

    def convert_file(self, file_path):
        """Convert a file to markdown using MarkItDown."""
        file_name = os.path.basename(file_path)
        md = MarkItDown(enable_plugins=False)
        result = md.convert(file_path)
        save_filename = os.path.join(os.path.dirname(file_path), file_name + ".md")
        with open(save_filename, "w") as f:
            f.write(result.text_content)
        logger.info(f"Converted {file_name} to {save_filename}")

    def convert_files(self, df):
        """Convert all files in df to markdown."""
        for f in df["File"]:
            self.convert_file(self.fullpath(f))

    def vectorize_files(self, df, collection_name, qdrant_url):
        """Vectorize files using EmbeddingDocuments."""
        ed = EmbeddingDocuments(df["File"].tolist(), qdrant_url)
        ed.create_collection(collection_name)
        ed.perform_embedding(collection_name)
