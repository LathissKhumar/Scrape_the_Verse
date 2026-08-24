"""Lightweight relevance ranking and filtering of content chunks using cosine similarity."""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticFilter:
    """Lightweight relevance ranking and filtering of content chunks using cosine similarity."""

    def __init__(
        self,
        similarity_threshold: float = 0.05,
        top_k: int = 5,
        min_word_count: int = 2,
    ) -> None:
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k
        self.min_word_count = min_word_count

    def rank_and_filter(
        self,
        chunks: list[str],
        query: str,
        top_k: int | None = None,
        threshold: float | None = None,
    ) -> list[tuple[str, float]]:
        """Rank chunks by similarity to query, returning list of (chunk_text, similarity_score)."""
        effective_k = top_k or self.top_k
        effective_threshold = (
            threshold if threshold is not None else self.similarity_threshold
        )

        if not chunks:
            return []

        # Filter out empty or whitespace-only chunks
        valid_chunks = [c for c in chunks if len(c.split()) >= self.min_word_count]
        if not valid_chunks:
            valid_chunks = [c for c in chunks if c.strip()]

        if not valid_chunks:
            return []

        if not query or not query.strip():
            return [(c, 1.0) for c in valid_chunks[:effective_k]]

        try:
            corpus = [query] + valid_chunks
            vectorizer = TfidfVectorizer(stop_words="english")
            tfidf_matrix = vectorizer.fit_transform(corpus)

            query_vec = tfidf_matrix[0:1]
            chunk_vecs = tfidf_matrix[1:]

            scores = cosine_similarity(query_vec, chunk_vecs)[0]

            scored_chunks: list[tuple[str, float]] = []
            for chunk, score in zip(valid_chunks, scores):
                scored_chunks.append((chunk, float(score)))

            # Sort descending by score
            scored_chunks.sort(key=lambda item: item[1], reverse=True)

            # Filter by threshold if matches exist above threshold
            filtered = [
                item for item in scored_chunks if item[1] >= effective_threshold
            ]
            if filtered:
                return filtered[:effective_k]

            return scored_chunks[:effective_k]

        except Exception:
            return [(c, 1.0) for c in valid_chunks[:effective_k]]
