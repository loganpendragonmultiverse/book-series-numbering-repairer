import pytest

from book_series_numbering_repairer.core import analyze


@pytest.mark.parametrize(
    "number", ["NaN", "Infinity", "-Infinity", "1/0", "NaN/2", "1/Infinity", "1/x", "a", "1/2/3"]
)
def test_nonfinite_and_invalid_fraction(number: str) -> None:
    with pytest.raises((ValueError, TypeError), match=r"entries\[0\].number"):
        analyze({"entries": [{"number": number}]})


def test_aliases_and_stable_ties() -> None:
    report = analyze(
        {
            "entries": [
                {"number": n, "title": str(i)}
                for i, n in enumerate(["Book 1", "1.0", "1/2", "prequel", "zero", "0"])
            ]
        }
    )
    assert [item["title"] for item in report["entries"]] == ["3", "4", "5", "2", "0", "1"]
    assert set(report["ambiguous_orders"]) == {"0", "1"}


@pytest.mark.parametrize("entries", ["wrong", [None]])
def test_bad_entries(entries: object) -> None:
    with pytest.raises((ValueError, TypeError)):
        analyze({"entries": entries})


def test_explicit_orders_labels_and_csv_preview(tmp_path, capsys) -> None:
    from book_series_numbering_repairer.cli import main
    from book_series_numbering_repairer.preview import render_html

    entries = [
        {"number": "special", "title": "</script><script>bad</script>", "publication_order": 2},
        {"number": "1", "publication_order": 1, "reading_order": 0},
    ]
    data = {"entries": entries, "special_labels": {"special": "0.5"}}
    assert analyze(data)["entries"][0]["reading_order"] == 0
    assert analyze({**data, "order_mode": "publication"})["entries"][0]["publication_order"] == 1
    assert "</script><script>bad" not in render_html(analyze(data))
    source = tmp_path / "books.csv"
    source.write_text("title,number,publication_order\nOne,1,2\nTwo,2,1\n")
    assert main([str(source), "--order", "publication", "--format", "html"]) == 0
    assert "Download edited JSON" in capsys.readouterr().out


@pytest.mark.parametrize(
    "extra", [{"order_mode": "guessed"}, {"special_labels": []}, {"order_mode": "publication"}]
)
def test_invalid_order_contract(extra) -> None:
    with pytest.raises((ValueError, TypeError)):
        analyze({"entries": [{"number": 1}], **extra})
