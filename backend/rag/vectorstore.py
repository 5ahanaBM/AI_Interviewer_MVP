import json
import os
from typing import List, Tuple

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

class QuestionVectorStore:
    """
    Manages question embeddings and FAISS-based search.
    """

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.embeddings = OpenAIEmbeddings()
        self.index = None
        self.questions = []

    def load_questions(self) -> List[Document]:
        """
        Loads questions from the JSON file and converts to Document format for FAISS.
        """
        with open(self.data_path, "r", encoding="utf-8") as f:
            self.questions = json.load(f)

        documents = []
        for item in self.questions:
            metadata = {
                "tags": item.get("tags", []),
                "difficulty": item.get("difficulty", "Unknown")
            }
            documents.append(Document(page_content=item["question"], metadata=metadata))
        return documents

    def build_index(self):
        """
        Builds a FAISS index from question documents.
        """
        docs = self.load_questions()
        self.index = FAISS.from_documents(docs, self.embeddings)

    def search(self, query: str, k: int = 3) -> List[Tuple[str, dict]]:
        """
        Searches the FAISS index for questions related to the query.

        Returns:
            List of tuples (question_text, metadata).
        """
        results = self.index.similarity_search_with_score(query, k=k)
        return [(doc.page_content, doc.metadata) for doc, _ in results]
