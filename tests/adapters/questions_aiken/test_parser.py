import pytest

from quiz.adapters.questions_aiken.parser import (
    AikenParseError,
    extract_formation,
    extract_session,
    extract_title,
    parse_aiken,
)
from quiz.domain.models import QuestionKind


def test_parses_single_question_single_answer():
    text = """\
Quelle commande liste les pods ?
A) kubectl get pods
B) kubectl list pods
C) kubectl show pods
ANSWER: A
"""
    questions = parse_aiken(text)

    assert len(questions) == 1
    q = questions[0]
    assert q.prompt == "Quelle commande liste les pods ?"
    assert [c.label for c in q.choices] == ["A", "B", "C"]
    assert q.choices[0].text == "kubectl get pods"
    assert q.correct_labels == frozenset({"A"})
    assert q.kind == QuestionKind.THEORY  # default when no %kind% marker


def test_parses_multiple_questions_separated_by_blank_line():
    text = """\
Question un ?
A) x
B) y
ANSWER: A

Question deux ?
A) x
B) y
ANSWER: B
"""
    questions = parse_aiken(text)

    assert len(questions) == 2
    assert questions[0].prompt == "Question un ?"
    assert questions[1].prompt == "Question deux ?"
    assert questions[1].correct_labels == frozenset({"B"})


def test_supports_multi_select_answers_as_extension():
    text = """\
Quelles commandes sont valides ?
A) kubectl get pods
B) kubectl apply -f x.yaml
C) kubectl frobnicate
ANSWER: A,B
"""
    questions = parse_aiken(text)

    assert questions[0].correct_labels == frozenset({"A", "B"})


def test_supports_kind_marker_comment():
    text = """\
%kind: practice
Executez la commande pour lister les pods.
A) kubectl get pods
B) kubectl list pods
ANSWER: A
"""
    questions = parse_aiken(text)

    assert questions[0].kind == QuestionKind.PRACTICE
    assert questions[0].prompt == "Executez la commande pour lister les pods."


def test_generates_stable_ids_from_position():
    text = """\
Question un ?
A) x
B) y
ANSWER: A

Question deux ?
A) x
B) y
ANSWER: B
"""
    questions = parse_aiken(text)

    assert questions[0].id == "q1"
    assert questions[1].id == "q2"


def test_raises_on_missing_answer_line():
    text = """\
Question sans reponse ?
A) x
B) y
"""
    with pytest.raises(AikenParseError):
        parse_aiken(text)


def test_raises_on_answer_referencing_unknown_label():
    text = """\
Question ?
A) x
B) y
ANSWER: Z
"""
    with pytest.raises(AikenParseError):
        parse_aiken(text)


def test_extracts_title_marker():
    text = """\
%title: K8s Bases - Matin

Question un ?
A) x
B) y
ANSWER: A
"""
    assert extract_title(text) == "K8s Bases - Matin"


def test_extract_title_returns_none_when_absent():
    text = """\
Question un ?
A) x
B) y
ANSWER: A
"""
    assert extract_title(text) is None


def test_parse_aiken_ignores_title_marker_line():
    text = """\
%title: K8s Bases - Matin

Question un ?
A) x
B) y
ANSWER: A
"""
    questions = parse_aiken(text)

    assert len(questions) == 1
    assert questions[0].prompt == "Question un ?"


def test_extracts_formation_marker():
    text = """\
%formation: Kubernetes Bases
%session: matin

Question un ?
A) x
B) y
ANSWER: A
"""
    assert extract_formation(text) == "Kubernetes Bases"
    assert extract_session(text) == "matin"


def test_extract_formation_returns_none_when_absent():
    text = "Question un ?\nA) x\nB) y\nANSWER: A\n"
    assert extract_formation(text) is None
    assert extract_session(text) is None


def test_parse_aiken_ignores_formation_and_session_marker_lines():
    text = """\
%formation: Kubernetes Bases
%session: matin
%title: K8s Bases - Matin

Question un ?
A) x
B) y
ANSWER: A
"""
    questions = parse_aiken(text)

    assert len(questions) == 1
    assert questions[0].prompt == "Question un ?"
