from quiz.domain.models import Attempt, Choice, Question, QuestionKind, QuestionResult, Student
from datetime import datetime


def make_question(correct: frozenset[str] = frozenset({"A"})) -> Question:
    return Question(
        id="q1",
        prompt="Quelle commande liste les pods ?",
        choices=(
            Choice("A", "kubectl get pods"),
            Choice("B", "kubectl list pods"),
        ),
        correct_labels=correct,
        kind=QuestionKind.PRACTICE,
    )


def test_question_is_correct_matches_exact_label_set():
    q = make_question(correct=frozenset({"A"}))

    assert q.is_correct(frozenset({"A"})) is True
    assert q.is_correct(frozenset({"B"})) is False


def test_question_is_correct_supports_multi_select():
    q = make_question(correct=frozenset({"A", "B"}))

    assert q.is_correct(frozenset({"A", "B"})) is True
    assert q.is_correct(frozenset({"A"})) is False


def test_attempt_score_counts_correct_results_only():
    results = (
        QuestionResult(question_id="q1", given_labels=frozenset({"A"}), correct=True),
        QuestionResult(question_id="q2", given_labels=frozenset({"B"}), correct=False),
        QuestionResult(question_id="q3", given_labels=frozenset({"A"}), correct=True),
    )
    attempt = Attempt(
        quiz_id="k8s-bases-matin",
        student=Student(display_name="Alban Crommer"),
        results=results,
        started_at=datetime(2026, 9, 20, 9, 0),
        finished_at=datetime(2026, 9, 20, 9, 10),
    )

    assert attempt.score == 2
    assert attempt.total == 3
