import json

import pytest

from book_series_numbering_repairer.cli import main
from book_series_numbering_repairer.core import analyze, render_json
from book_series_numbering_repairer.preview import render_html


def test_distinct_series_and_stable_collision_evidence():
    report = analyze(
        {
            "entries": [
                {"series": " B ", "number": "1/2", "title": "first"},
                {"series": "A", "number": ".5", "title": "other"},
                {"series": "B", "number": "special", "title": "second"},
                {"series": "B", "number": "0", "title": "prequel"},
            ],
            "special_labels": {"special": "0.50"},
        }
    )
    assert report["series_groups"] == ["B", "A"]
    assert [e["title"] for e in report["entries"]] == ["prequel", "first", "second", "other"]
    assert report["collisions"] == [
        {"series": "B", "normalized_order": "0.5", "source_indices": [0, 2]}
    ]
    assert report["ambiguous_orders"] == ["0.5"]
    assert json.loads(render_json(report)) == report


def test_same_numbers_in_distinct_series_do_not_collide():
    report = analyze({"entries": [{"series": s, "number": "Book 1"} for s in ["A", "a", "B"]]})
    assert report["collisions"] == [] and report["ambiguous_orders"] == []


def test_publication_and_reading_groups():
    entries = [
        {"series": "A", "number": 1, "publication_order": 2, "reading_order": 0},
        {"series": "B", "number": 1, "publication_order": 1},
        {"series": "A", "number": 2, "publication_order": 1},
    ]
    assert [e["source_index"] for e in analyze({"entries": entries})["entries"]] == [0, 2, 1]
    assert [
        e["source_index"]
        for e in analyze({"entries": entries, "order_mode": "publication"})["entries"]
    ] == [2, 0, 1]


def test_csv_json_and_html_preserve_groups(tmp_path, capsys):
    path = tmp_path / "books.csv"
    path.write_text('series,title,number\n"A & <B>",One,1\nOther,Two,1\n', encoding="utf-8")
    assert main([str(path), "--format", "json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["collisions"] == []
    assert report["entries"][0]["series"] == "A & <B>"
    assert analyze(report)["series_groups"] == report["series_groups"]
    output = render_html(report)
    assert "Series group" in output
    assert "A & <B>" not in output
    assert "['series','Series group']" in output
    assert "normalized_order','display','source_index" in output


@pytest.mark.parametrize("series", [None, 1, [], {}])
def test_invalid_series(series):
    with pytest.raises(TypeError, match="series"):
        analyze({"entries": [{"number": 1, "series": series}]})


def test_signed_zero_collisions_use_numeric_identity():
    report = analyze(
        {
            "entries": [
                {"series": "A", "number": "-0", "title": "negative"},
                {"series": "B", "number": "0"},
                {"series": "A", "number": "0", "title": "positive"},
                {"series": "A", "number": "-0/2", "title": "fraction"},
                {"series": "A", "number": "special", "title": "label"},
            ],
            "special_labels": {"special": "-0.00"},
        }
    )
    assert report["collisions"] == [
        {"series": "A", "normalized_order": "0", "source_indices": [0, 2, 3, 4]}
    ]
    assert report["ambiguous_orders"] == ["0"]
    entries = report["entries"][:4]
    assert [e["title"] for e in entries] == ["negative", "positive", "fraction", "label"]
    assert entries[0]["normalized_order"] == "-0"
    assert entries[0]["display"] == "Book -0: negative"
