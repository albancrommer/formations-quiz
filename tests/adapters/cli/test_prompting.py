from quiz.adapters.cli.prompting import parse_answer_input
from quiz.domain.models import Choice, Question, QuestionKind


def make_question() -> Question:
    return Question(
        id="q1",
        prompt="?",
        choices=(Choice("A", "x"), Choice("B", "y"), Choice("C", "z")),
        correct_labels=frozenset({"A"}),
        kind=QuestionKind.THEORY,
    )


def test_parses_single_letter():
    assert parse_answer_input("A", make_question()) == frozenset({"A"})


def test_is_case_insensitive():
    assert parse_answer_input("a", make_question()) == frozenset({"A"})


def test_parses_comma_separated_multi_select():
    assert parse_answer_input("A,C", make_question()) == frozenset({"A", "C"})


def test_strips_whitespace_around_commas():
    assert parse_answer_input(" a , c ", make_question()) == frozenset({"A", "C"})


def test_raises_value_error_on_unknown_label():
    import pytest

    with pytest.raises(ValueError):
        parse_answer_input("Z", make_question())


def test_raises_value_error_on_empty_input():
    import pytest

    with pytest.raises(ValueError):
        parse_answer_input("", make_question())
