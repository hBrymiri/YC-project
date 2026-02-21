# BackEnd/__init__.py

from .Train_face_reg import Recognizer
from .database import insert_embedding, fetch_all_embeddings

__all__ = ["Recognizer", "insert_embedding", "fetch_all_embeddings"]
