from app.extraction.schema import ExtractionSchema, FieldRule
from app.extraction.tables import TableExtractor


def test_table_extractor_success():
    html = """
    <html>
        <body>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Price</th>
                        <th>Rating</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Widget Alpha</td>
                        <td>$10.00</td>
                        <td>4.5</td>
                    </tr>
                    <tr>
                        <td>Widget Beta</td>
                        <td>$20.00</td>
                        <td>4.8</td>
                    </tr>
                </tbody>
            </table>
        </body>
    </html>
    """
    schema = ExtractionSchema(
        fields=[
            FieldRule(name="product"),
            FieldRule(name="price"),
            FieldRule(name="rating"),
        ]
    )

    extractor = TableExtractor()
    tables = extractor.extract_tables(html)
    assert len(tables) == 1
    assert tables[0]["score"] >= 0.8
    assert tables[0]["headers"] == ["Product", "Price", "Rating"]

    records = extractor.extract(html, schema)
    assert len(records) == 2
    assert records[0]["product"] == "Widget Alpha"
    assert records[0]["price"] == "$10.00"
    assert records[1]["product"] == "Widget Beta"


def test_table_extractor_layout_table_rejected():
    html = """
    <table>
        <tr>
            <td>Only one layout cell</td>
        </tr>
    </table>
    """
    extractor = TableExtractor()
    tables = extractor.extract_tables(html)
    assert len(tables) == 0
