import pytest

from book_series_numbering_repairer.core import analyze


def test_long_decimal_positions_do_not_round_into_collisions():
    a = "1.123456789012345678901234567890123456789"
    b = "1.123456789012345678901234567890123456788"
    report = analyze({"entries": [{"number": a}, {"number": b}]})
    assert [row["source_index"] for row in report["entries"]] == [1, 0]
    assert report["collisions"] == []
    assert report["entries"][1]["normalized_order"] == a


def test_repeating_fractions_are_exact_and_reduce():
    report = analyze(
        {
            "entries": [
                {"number": "1/3"},
                {"number": "0.3333333333333333333333333333"},
                {"number": "2/6"},
            ]
        }
    )
    assert [row["source_index"] for row in report["entries"]] == [1, 0, 2]
    assert report["collisions"] == [
        {"series": "", "normalized_order": "1/3", "source_indices": [0, 2]}
    ]
    again = analyze(report)
    assert [row["number"] for row in again["entries"]] == [
        row["number"] for row in report["entries"]
    ]
    assert again["collisions"] == [
        {"series": "", "normalized_order": "1/3", "source_indices": [1, 2]}
    ]


@pytest.mark.parametrize("value", [True, False, [], {}, "1e1001", "1e-1001", "9" * 257])
def test_invalid_or_excessive_numeric_operands(value):
    with pytest.raises((ValueError, TypeError)):
        analyze({"entries": [{"number": value}]})


@pytest.mark.parametrize("extra", [{"title": None}, {"order_mode": []}])
def test_malformed_fields_are_actionable(extra):
    data = {"entries": [{"number": 1, "title": "A"}]}
    if "title" in extra:
        data["entries"][0].update(extra)
    else:
        data.update(extra)
    with pytest.raises((ValueError, TypeError)):
        analyze(data)


def test_preview_keeps_large_numeric_values_as_text():
    import json

    from book_series_numbering_repairer.preview import render_html

    number = 123456789012345678901234567890123456789
    report = analyze(
        {
            "entries": [{"number": number, "reading_order": number}],
            "special_labels": {"later": number + 1},
        }
    )
    html = render_html(report)
    payload = html.split('id="data">', 1)[1].split("</script>", 1)[0]
    preview = json.loads(payload)
    assert preview["entries"][0]["number"] == str(number)
    assert preview["special_labels"]["later"] == str(number + 1)
