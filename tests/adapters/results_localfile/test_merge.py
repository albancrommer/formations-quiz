from quiz.adapters.results_localfile.merge import AttemptRow, collect_attempts


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


def test_collect_attempts_reads_all_yaml_files_recursively(tmp_path):
    host_a = tmp_path / "vnc-server-sacha"
    host_b = tmp_path / "vnc-server-julien"
    host_a.mkdir()
    host_b.mkdir()

    write_result(
        host_a / "20260921-090000_k8s-bases-matin_sacha.yaml",
        quiz_id="k8s-bases-matin",
        student="Sacha",
        score=5,
        total=6,
        started_at="2026-09-21T09:00:00",
        finished_at="2026-09-21T09:10:00",
    )
    write_result(
        host_b / "20260921-091500_k8s-bases-matin_julien.yaml",
        quiz_id="k8s-bases-matin",
        student="Julien",
        score=6,
        total=6,
        started_at="2026-09-21T09:15:00",
        finished_at="2026-09-21T09:22:00",
    )

    rows = collect_attempts(tmp_path)

    assert len(rows) == 2
    assert AttemptRow(
        student="Sacha",
        quiz_id="k8s-bases-matin",
        score=5,
        total=6,
        started_at="2026-09-21T09:00:00",
        finished_at="2026-09-21T09:10:00",
        source_file=host_a / "20260921-090000_k8s-bases-matin_sacha.yaml",
    ) in rows


def test_collect_attempts_sorted_by_finished_at(tmp_path):
    write_result(
        tmp_path / "second.yaml",
        quiz_id="k8s-bases-matin",
        student="Julien",
        score=6,
        total=6,
        started_at="2026-09-21T09:15:00",
        finished_at="2026-09-21T09:22:00",
    )
    write_result(
        tmp_path / "first.yaml",
        quiz_id="k8s-bases-matin",
        student="Sacha",
        score=5,
        total=6,
        started_at="2026-09-21T09:00:00",
        finished_at="2026-09-21T09:10:00",
    )

    rows = collect_attempts(tmp_path)

    assert [r.student for r in rows] == ["Sacha", "Julien"]


def test_collect_attempts_returns_empty_for_empty_dir(tmp_path):
    assert collect_attempts(tmp_path) == []


def test_collect_attempts_skips_malformed_yaml_and_reports_it(tmp_path):
    good = tmp_path / "good.yaml"
    write_result(
        good,
        quiz_id="k8s-bases-matin",
        student="Sacha",
        score=5,
        total=6,
        started_at="2026-09-21T09:00:00",
        finished_at="2026-09-21T09:10:00",
    )
    bad = tmp_path / "bad.yaml"
    bad.write_text("not: [valid, yaml: structure\n")

    rows = collect_attempts(tmp_path)

    assert len(rows) == 1
    assert rows[0].student == "Sacha"


def test_collect_attempts_skips_yaml_missing_required_fields(tmp_path):
    incomplete = tmp_path / "incomplete.yaml"
    incomplete.write_text("quiz_id: k8s-bases-matin\n")

    rows = collect_attempts(tmp_path)

    assert rows == []


def test_collect_attempts_ignores_non_yaml_files(tmp_path):
    (tmp_path / "notes.txt").write_text("not a result file")

    rows = collect_attempts(tmp_path)

    assert rows == []
