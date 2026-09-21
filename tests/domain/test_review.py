from quiz.domain.models import Choice, Question, QuestionKind, QuestionResult, Quiz
from quiz.domain.review import review_attempt


def make_quiz() -> Quiz:
    return Quiz(
        id="k8s-bases-matin",
        title="K8s Bases - Matin",
        questions=(
            Question(
                id="q1",
                prompt="Question un ?",
                choices=(Choice("A", "x"), Choice("B", "y")),
                correct_labels=frozenset({"A"}),
                kind=QuestionKind.THEORY,
            ),
            Question(
                id="q2",
                prompt="Question deux ?",
                choices=(Choice("A", "x"), Choice("B", "y")),
                correct_labels=frozenset({"B"}),
                kind=QuestionKind.THEORY,
            ),
            Question(
                id="q3",
                prompt="Question trois ?",
                choices=(Choice("A", "x"), Choice("B", "y")),
                correct_labels=frozenset({"A"}),
                kind=QuestionKind.PRACTICE,
            ),
        ),
    )


def make_results(*, correctness: list[bool]) -> tuple[QuestionResult, ...]:
    return tuple(
        QuestionResult(
            question_id=f"q{i + 1}",
            given_labels=frozenset({"A"}),
            correct=correct,
        )
        for i, correct in enumerate(correctness)
    )


def test_review_lists_1_indexed_positions_of_wrong_questions():
    quiz = make_quiz()
    results = make_results(correctness=[True, False, False])

    review = review_attempt(quiz, results)

    assert review.wrong_positions == (2, 3)


def test_review_is_empty_when_all_correct():
    quiz = make_quiz()
    results = make_results(correctness=[True, True, True])

    review = review_attempt(quiz, results)

    assert review.wrong_positions == ()
    assert review.wrong_items == ()


def test_review_items_include_question_and_correct_answer_text():
    quiz = make_quiz()
    results = make_results(correctness=[True, False, True])

    review = review_attempt(quiz, results)

    assert len(review.wrong_items) == 1
    item = review.wrong_items[0]
    assert item.position == 2
    assert item.prompt == "Question deux ?"
    assert item.correct_choices == (Choice("B", "y"),)
