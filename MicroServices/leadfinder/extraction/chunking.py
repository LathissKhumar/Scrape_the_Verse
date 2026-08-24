"""Content chunker for splitting large texts with sentence boundary preservation."""

import re

_PARAGRAPH_SPLIT_PATTERN = re.compile(r"\n\s*\n")
_SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+")


class ContentChunker:
    """Chunks text and HTML content with sentence-boundary awareness, overlap, and context preservation."""

    def __init__(
        self,
        chunk_size: int = 1500,
        chunk_overlap: int = 200,
        min_chunk_size: int = 50,
    ) -> None:
        self.chunk_size = max(chunk_size, 50)
        self.chunk_overlap = max(0, min(chunk_overlap, self.chunk_size // 2))
        self.min_chunk_size = min_chunk_size

    def chunk_text(
        self,
        text: str,
        preserve_context_prefix: str | None = None,
    ) -> list[str]:
        """Split plain or markdown text into chunks respecting sentence and paragraph boundaries."""
        cleaned = text.strip()
        if not cleaned:
            return []

        if len(cleaned) <= self.chunk_size:
            if preserve_context_prefix:
                return [f"{preserve_context_prefix.strip()}\n\n{cleaned}"]
            return [cleaned]

        paragraphs = [
            p.strip() for p in _PARAGRAPH_SPLIT_PATTERN.split(cleaned) if p.strip()
        ]
        chunks: list[str] = []
        current_chunk: list[str] = []
        current_length = 0

        for para in paragraphs:
            para_len = len(para)
            if current_length + para_len + 2 <= self.chunk_size:
                current_chunk.append(para)
                current_length += para_len + 2
            else:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    overlap_para = (
                        current_chunk[-1]
                        if len(current_chunk[-1]) <= self.chunk_overlap
                        else ""
                    )
                    current_chunk = [overlap_para] if overlap_para else []
                    current_length = len(overlap_para)

                if para_len > self.chunk_size:
                    sentences = _SENTENCE_SPLIT_PATTERN.split(para)
                    for sent in sentences:
                        sent_len = len(sent)
                        if current_length + sent_len + 1 <= self.chunk_size:
                            current_chunk.append(sent)
                            current_length += sent_len + 1
                        else:
                            if current_chunk:
                                chunks.append(" ".join(current_chunk))
                            current_chunk = [sent]
                            current_length = sent_len
                else:
                    current_chunk.append(para)
                    current_length += para_len + 2

        if current_chunk:
            chunk_str = "\n\n".join(current_chunk).strip()
            if chunk_str:
                chunks.append(chunk_str)

        if preserve_context_prefix:
            prefix = preserve_context_prefix.strip()
            chunks = [f"{prefix}\n\n{c}" for c in chunks]

        return [
            c
            for c in chunks
            if len(c.strip()) >= self.min_chunk_size or len(chunks) == 1
        ]
