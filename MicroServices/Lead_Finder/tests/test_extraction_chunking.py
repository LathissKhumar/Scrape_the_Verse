from leadfinder.extraction.chunking import ContentChunker


def test_chunker_small_text_single_chunk():
    chunker = ContentChunker(chunk_size=1000)
    text = "Short text under the chunk size threshold."
    chunks = chunker.chunk_text(text)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunker_splits_large_paragraphs():
    chunker = ContentChunker(chunk_size=100, chunk_overlap=20, min_chunk_size=20)
    text = (
        "Paragraph 1 is here with some detailed explanations and words.\n\n"
        "Paragraph 2 is here with another set of words and sentences.\n\n"
        "Paragraph 3 is also here explaining further information."
    )
    chunks = chunker.chunk_text(text)
    assert len(chunks) > 1


def test_chunker_preserves_prefix():
    chunker = ContentChunker(chunk_size=500)
    text = "Data content inside."
    chunks = chunker.chunk_text(text, preserve_context_prefix="Header Context")
    assert len(chunks) == 1
    assert "Header Context" in chunks[0]
