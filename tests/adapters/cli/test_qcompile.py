import csv

from quiz.adapters.cli.qcompile_main import main


def write_result(path, *, quiz_id, student, score, total, started_at, finished_at):
    path.write_text(
        f"""\
quiz_id: {quiz_id}
student: {student}
started_at: '{started_at}'
finished_at: '{finished_at}'
score: {score}
total: {total}
results: []
"""
    )


def test_writes_csv_with_one_row_per_attempt(tmp_path):
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    write_result(
        results_dir / "a.yaml",
        quiz_id="k8s-bases-matin",
        student="Sacha",
        score=5,
        total=6,
        started_at="2026-09-21T09:00:00",
        finished_at="2026-09-21T09:10:00",
    )
    write_result(
        results_dir / "b.yaml",
        quiz_id="k8s-dev-matin",
        student="Julien",
        score=6,
        total=6,
        started_at="2026-09-21T09:15:00",
        finished_at="2026-09-21T09:22:00",
    )
    out_csv = tmp_path / "report.csv"

    exit_code = main([str(results_dir), "--out", str(out_csv)])

    assert exit_code == 0
    with out_csv.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert rows[0]["student"] == "Sacha"
    assert rows[0]["quiz_id"] == "k8s-bases-matin"
    assert rows[0]["score"] == "5"
    assert rows[0]["total"] == "6"


def test_defaults_output_path_to_report_csv_in_cwd(tmp_path, monkeypatch):
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    write_result(
        results_dir / "a.yaml",
        quiz_id="k8s-bases-matin",
        student="Sacha",
        score=5,
        total=6,
        started_at="2026-09-21T09:00:00",
        finished_at="2026-09-21T09:10:00",
    )
    monkeypatch.chdir(tmp_path)

    exit_code = main([str(results_dir)])

    assert exit_code == 0
    assert (tmp_path / "report.csv").exists()


def test_errors_cleanly_on_empty_results_dir(tmp_path, capsys):
    results_dir = tmp_path / "empty"
    results_dir.mkdir()

    exit_code = main([str(results_dir)])

    assert exit_code == 1
    assert "aucun" in capsys.readouterr().err.lower()


def test_errors_cleanly_on_missing_results_dir(tmp_path, capsys):
    exit_code = main([str(tmp_path / "does-not-exist")])

    assert exit_code == 1
