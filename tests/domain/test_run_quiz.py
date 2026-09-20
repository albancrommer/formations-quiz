from datetime import datetime

from quiz.domain.models import Choice, Question, QuestionKind, Quiz, Student
from quiz.domain.run_quiz import AnswerQuestion, run_quiz


def make_quiz() -> Quiz:
    return Quiz(
        id="k8s-bases-matin",
        title="K8s Bases - Matin",
        questions=(
            Question(
                id="q1",
                prompt="Quelle commande liste les pods ?",
                choices=(Choice("A", "kubectl get pods"), Choice("B", "kubectl list pods")),
                correct_labels=frozenset({"A"}),
                kind=QuestionKind.PRACTICE,
            ),
            Question(
                id="q2",
                prompt="Quel objet gere des Pods identiques ?",
                choices=(Choice("A", "ConfigMap"), Choice("B", "ReplicaSet")),
                correct_labels=frozenset({"B"}),
                kind=QuestionKind.THEORY,
            ),
        ),
    )


class FixedClock:
    def __init__(self, times: list[datetime]) -> None:
        self._times = iter(times)

    def now(self) -> datetime:
        return next(self._times)


def test_run_quiz_scores_answers_and_builds_attempt():
    quiz = make_quiz()
    student = Student(display_name="Sacha")
    answers: list[AnswerQuestion] = lambda question: (
        frozenset({"A"}) if question.id == "q1" else frozenset({"A"})  # q2 wrong on purpose
    )
    clock = FixedClock([datetime(2026, 9, 20, 9, 0), datetime(2026, 9, 20, 9, 5)])

    attempt = run_quiz(quiz=quiz, student=student, answer_question=answers, clock=clock.now)

    assert attempt.quiz_id == "k8s-bases-matin"
    assert attempt.student == student
    assert attempt.started_at == datetime(2026, 9, 20, 9, 0)
    assert attempt.finished_at == datetime(2026, 9, 20, 9, 5)
    assert attempt.score == 1
    assert attempt.total == 2
    assert attempt.results[0].correct is True
    assert attempt.results[1].correct is False


def test_run_quiz_calls_answer_question_once_per_question_in_order():
    quiz = make_quiz()
    asked_ids: list[str] = []

    def answers(question: Question) -> frozenset[str]:
        asked_ids.append(question.id)
        return question.correct_labels

    clock = FixedClock([datetime(2026, 9, 20, 9, 0), datetime(2026, 9, 20, 9, 5)])

    run_quiz(quiz=quiz, student=Student("Sacha"), answer_question=answers, clock=clock.now)

    assert asked_ids == ["q1", "q2"]
