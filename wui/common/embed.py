"""
EmbeddingDocuments: Handles document embedding and collection management for Qdrant vector DB.
"""

from loguru import logger
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models
from typing import List
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter


class EmbeddingDocuments:
    def __init__(self, file_list: List[str], qdrant_url: str):
        self.file_list = file_list
        self.qdrant_client = QdrantClient(url=qdrant_url)
        self.vector_store = QdrantVectorStore(client=self.qdrant_client)

    def add_files(self, files: List[str]):
        """Add files to the embedding list."""
        self.file_list.extend(files)
        logger.debug(f"Files added for embedding: {files}")

    def remove_files(self, files: List[str]):
        """Remove files from the embedding list."""
        for file in files:
            try:
                self.file_list.remove(file)
                logger.debug(f"File removed: {file}")
            except ValueError:
                logger.warning(f"File not found: {file}")

    def load_documents(self):
        """Load file contents as documents."""
        documents = []
        if not self.file_list:
            logger.error("No files to embed. Please add files first.")
            return []
        for file in self.file_list:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                    documents.append({"file": file, "content": content})
                    logger.debug(f"Loaded: {file}")
            except Exception as e:
                logger.error(f"Error reading {file}: {e}")
        return documents

    def split_documents(self, documents, chunk_size=1000):
        """Split documents into chunks for embedding."""
        if not documents:
            logger.error("No documents to split.")
            return []
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=200, length_function=len
        )
        return splitter.split_documents(documents)

    def hf_embeddings(self):
        """Return HuggingFace embedding model."""
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
            model_kwargs={},
            encode_kwargs={"normalize_embeddings": False},
        )

    def perform_embedding(self, cname: str):
        """Embed loaded documents and upsert to Qdrant."""
        documents = self.load_documents()
        if not documents:
            logger.error("No documents loaded for embedding.")
            return
        hf = self.hf_embeddings()
        for doc in documents:
            self.qdrant_client.upsert(
                collection_name=cname,
                points=[
                    models.PointStruct(
                        id=doc["file"],
                        vector={
                            "text-title": hf.embed_query(doc["file"]),
                            "text-content": hf.embed_query(doc["content"]),
                        },
                        payload=doc["content"],
                    )
                ],
            )

    def create_collection(self, collection_name: str):
        """Create a Qdrant collection if it doesn't exist."""
        collections = self.qdrant_client.get_collections()
        existing = [c.name for c in collections.collections]
        if collection_name in existing:
            logger.info(f"Collection '{collection_name}' already exists.")
            return
        self.qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "text-content": models.VectorParams(
                    size=768, distance=models.Distance.COSINE
                ),
                "text-title": models.VectorParams(
                    size=768, distance=models.Distance.COSINE
                ),
            },
        )
        logger.debug(f"Collection '{collection_name}' created.")
