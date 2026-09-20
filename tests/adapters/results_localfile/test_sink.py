from datetime import datetime

import yaml

from quiz.adapters.results_localfile.sink import LocalFileResultSink
from quiz.domain.models import Attempt, QuestionResult, Student


def make_attempt() -> Attempt:
    return Attempt(
        quiz_id="k8s-bases-matin",
        student=Student(display_name="Sacha"),
        results=(
            QuestionResult(question_id="q1", given_labels=frozenset({"A"}), correct=True),
            QuestionResult(question_id="q2", given_labels=frozenset({"B"}), correct=False),
        ),
        started_at=datetime(2026, 9, 20, 9, 0, 0),
        finished_at=datetime(2026, 9, 20, 9, 5, 30),
    )


def test_save_writes_one_yaml_file_in_output_dir(tmp_path):
    sink = LocalFileResultSink(output_dir=tmp_path)

    sink.save(make_attempt())

    files = list(tmp_path.glob("*.yaml"))
    assert len(files) == 1


def test_filename_encodes_student_quiz_and_timestamp(tmp_path):
    sink = LocalFileResultSink(output_dir=tmp_path)

    sink.save(make_attempt())

    filename = next(tmp_path.glob("*.yaml")).name
    assert "sacha" in filename.lower()
    assert "k8s-bases-matin" in filename
    assert "20260920" in filename


def test_written_yaml_contains_score_and_answers(tmp_path):
    sink = LocalFileResultSink(output_dir=tmp_path)

    sink.save(make_attempt())

    content = yaml.safe_load(next(tmp_path.glob("*.yaml")).read_text())

    assert content["quiz_id"] == "k8s-bases-matin"
    assert content["student"] == "Sacha"
    assert content["score"] == 1
    assert content["total"] == 2
    assert content["results"] == [
        {"question_id": "q1", "given": ["A"], "correct": True},
        {"question_id": "q2", "given": ["B"], "correct": False},
    ]


def test_creates_output_dir_if_missing(tmp_path):
    output_dir = tmp_path / "results" / "nested"
    sink = LocalFileResultSink(output_dir=output_dir)

    sink.save(make_attempt())

    assert list(output_dir.glob("*.yaml"))
