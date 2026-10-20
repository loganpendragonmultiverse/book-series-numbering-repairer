
import pytest

from book_series_numbering_repairer.cli import main


@pytest.mark.parametrize(
    "text",
    [
        "number,number,title\n1,2,A\n",
        "number,,title\n1,2,A\n",
        "number,title\n1,A,extra\n",
        "number,title\n1\n",
        "",
        'number,title\n1,"unterminated',
    ],
)
def test_invalid_csv_structure_is_actionable(tmp_path, capsys, text):
    source = tmp_path / "input.csv"
    source.write_text(text)
    before = source.read_bytes()
    assert main([str(source)] + []) == 2
    assert "error:" in capsys.readouterr().err
    assert source.read_bytes() == before


def test_valid_quoted_multiline_csv(tmp_path, capsys):
    source = tmp_path / "input.csv"
    source.write_text('number,title,text\n1,"A\nmultiline title","Some, text"\n')
    assert main([str(source), "--format", "json"] + []) == 0
    output = capsys.readouterr().out
    assert "multiline title" in output
