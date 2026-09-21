from quiz.adapters.questions_aiken.discovery import AvailableQuiz, discover_quizzes


def test_discover_quizzes_lists_aiken_files_with_titles(tmp_path):
    (tmp_path / "k8s-bases-matin.aiken").write_text(
        "%title: K8s Bases - Matin\n\nQ ?\nA) x\nB) y\nANSWER: A\n"
    )
    (tmp_path / "k8s-dev-matin.aiken").write_text("Q ?\nA) x\nB) y\nANSWER: A\n")

    quizzes = discover_quizzes(tmp_path)

    assert quizzes == (
        AvailableQuiz(path=tmp_path / "k8s-bases-matin.aiken", title="K8s Bases - Matin"),
        AvailableQuiz(path=tmp_path / "k8s-dev-matin.aiken", title="k8s-dev-matin"),
    )


def test_discover_quizzes_falls_back_to_filename_stem_when_no_title(tmp_path):
    (tmp_path / "sample-quiz.aiken").write_text("Q ?\nA) x\nB) y\nANSWER: A\n")

    quizzes = discover_quizzes(tmp_path)

    assert quizzes[0].title == "sample-quiz"


def test_discover_quizzes_sorted_by_filename(tmp_path):
    (tmp_path / "z-quiz.aiken").write_text("Q ?\nA) x\nB) y\nANSWER: A\n")
    (tmp_path / "a-quiz.aiken").write_text("Q ?\nA) x\nB) y\nANSWER: A\n")

    quizzes = discover_quizzes(tmp_path)

    assert [q.path.name for q in quizzes] == ["a-quiz.aiken", "z-quiz.aiken"]


def test_discover_quizzes_ignores_non_aiken_files(tmp_path):
    (tmp_path / "notes.txt").write_text("not a quiz")
    (tmp_path / "quiz.aiken").write_text("Q ?\nA) x\nB) y\nANSWER: A\n")

    quizzes = discover_quizzes(tmp_path)

    assert len(quizzes) == 1


def test_discover_quizzes_empty_dir_returns_empty_tuple(tmp_path):
    assert discover_quizzes(tmp_path) == ()


def test_discover_quizzes_missing_dir_returns_empty_tuple(tmp_path):
    assert discover_quizzes(tmp_path / "does-not-exist") == ()
