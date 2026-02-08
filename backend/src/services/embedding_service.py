"""
Embedding Service
Uses Sentence-BERT for semantic text embeddings.
BERT understands context: "React developer" ≈ "Frontend engineer"
"""

from sentence_transformers import SentenceTransformer
from typing import List, Optional
import numpy as np
import logging

from core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Sentence-BERT embedding service for semantic understanding.
    
    Why BERT over TF-IDF:
    - TF-IDF: Word counting. "Java" (coffee) = "Java" (code)
    - BERT: Context understanding. "React" ≈ "Frontend" even without exact match
    """
    
    _instance: Optional["EmbeddingService"] = None
    _model: Optional[SentenceTransformer] = None
    
    def __new__(cls):
        """Singleton pattern to avoid loading model multiple times."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the embedding model."""
        if self._model is None:
            self._load_model()
    
    def _load_model(self):
        """Load the Sentence-BERT model."""
        try:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info(f"Embedding model loaded successfully. Dimension: {settings.EMBEDDING_DIMENSION}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    @property
    def model(self) -> SentenceTransformer:
        """Get the embedding model."""
        if self._model is None:
            self._load_model()
        return self._model
    
    def encode(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to encode
            
        Returns:
            List of floats (384 dimensions for MiniLM)
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return [0.0] * settings.EMBEDDING_DIMENSION
        
        embedding = self.model.encode(text, show_progress_bar=False)
        return embedding.tolist()
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to encode
            
        Returns:
            List of embeddings
        """
        if not texts:
            return []
        
        # Replace empty strings with placeholders
        processed_texts = [t if t and t.strip() else " " for t in texts]
        
        embeddings = self.model.encode(
            processed_texts,
            show_progress_bar=False,
            batch_size=32
        )
        return embeddings.tolist()
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        emb1 = np.array(self.encode(text1))
        emb2 = np.array(self.encode(text2))
        
        # Cosine similarity
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def batch_similarity(self, query: str, candidates: List[str]) -> List[float]:
        """
        Compute similarity between a query and multiple candidates.
        
        Args:
            query: Query text
            candidates: List of candidate texts
            
        Returns:
            List of similarity scores
        """
        query_emb = np.array(self.encode(query))
        candidate_embs = np.array(self.encode_batch(candidates))
        
        # Compute cosine similarities
        similarities = []
        query_norm = np.linalg.norm(query_emb)
        
        for cand_emb in candidate_embs:
            cand_norm = np.linalg.norm(cand_emb)
            if query_norm == 0 or cand_norm == 0:
                similarities.append(0.0)
            else:
                similarity = float(np.dot(query_emb, cand_emb) / (query_norm * cand_norm))
                similarities.append(similarity)
        
        return similarities


# Global embedding service instance
def get_embedding_service() -> EmbeddingService:
    """Get the global embedding service instance."""
    return EmbeddingService()
