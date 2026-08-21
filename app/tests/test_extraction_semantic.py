from app.extraction.semantic import SemanticFilter


def test_semantic_filter_ranks_relevant_chunks():
    filter_engine = SemanticFilter(top_k=2)
    chunks = [
        "Company quarterly financial earnings and revenues for Q3.",
        "Wireless Bluetooth noise cancelling headphones with long battery life.",
        "Privacy policy, terms of service and website cookie disclaimer.",
        "Bluetooth earphone features, sound quality, and charging case specs.",
    ]
    query = "Find Bluetooth headphones price and features"

    ranked = filter_engine.rank_and_filter(chunks, query=query, top_k=2)
    assert len(ranked) <= 2
    top_chunk, score = ranked[0]
    assert "Bluetooth" in top_chunk
    assert score > 0.0
