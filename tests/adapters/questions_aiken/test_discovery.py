from quiz.adapters.questions_aiken.discovery import AvailableQuiz, discover_quizzes, group_quizzes


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


def test_discover_quizzes_reads_formation_and_session(tmp_path):
    (tmp_path / "k8s-bases-matin.aiken").write_text(
        "%formation: Kubernetes Bases\n%session: matin\n%title: K8s Bases - Matin\n\nQ ?\nA) x\nB) y\nANSWER: A\n"
    )

    quizzes = discover_quizzes(tmp_path)

    assert quizzes[0].formation == "Kubernetes Bases"
    assert quizzes[0].session == "matin"


def test_discover_quizzes_formation_and_session_none_when_absent(tmp_path):
    (tmp_path / "plain.aiken").write_text("Q ?\nA) x\nB) y\nANSWER: A\n")

    quizzes = discover_quizzes(tmp_path)

    assert quizzes[0].formation is None
    assert quizzes[0].session is None


def test_discover_quizzes_sorted_with_matin_before_apres_midi_within_formation(tmp_path):
    (tmp_path / "bases-apres-midi.aiken").write_text(
        "%formation: Kubernetes Bases\n%session: apres-midi\n%title: Bases - Apres-midi\n\nQ ?\nA) x\nB) y\nANSWER: A\n"
    )
    (tmp_path / "bases-matin.aiken").write_text(
        "%formation: Kubernetes Bases\n%session: matin\n%title: Bases - Matin\n\nQ ?\nA) x\nB) y\nANSWER: A\n"
    )

    quizzes = discover_quizzes(tmp_path)

    assert [q.session for q in quizzes] == ["matin", "apres-midi"]


def test_group_quizzes_groups_by_formation_preserving_matin_first_order(tmp_path):
    (tmp_path / "dev-apres-midi.aiken").write_text(
        "%formation: Kubernetes Dev\n%session: apres-midi\n%title: Dev - Apres-midi\n\nQ ?\nA) x\nB) y\nANSWER: A\n"
    )
    (tmp_path / "dev-matin.aiken").write_text(
        "%formation: Kubernetes Dev\n%session: matin\n%title: Dev - Matin\n\nQ ?\nA) x\nB) y\nANSWER: A\n"
    )
    (tmp_path / "bases-apres-midi.aiken").write_text(
        "%formation: Kubernetes Bases\n%session: apres-midi\n%title: Bases - Apres-midi\n\nQ ?\nA) x\nB) y\nANSWER: A\n"
    )
    (tmp_path / "bases-matin.aiken").write_text(
        "%formation: Kubernetes Bases\n%session: matin\n%title: Bases - Matin\n\nQ ?\nA) x\nB) y\nANSWER: A\n"
    )

    quizzes = discover_quizzes(tmp_path)
    groups = group_quizzes(quizzes)

    assert [g.formation for g in groups] == ["Kubernetes Bases", "Kubernetes Dev"]
    assert [q.session for q in groups[0].quizzes] == ["matin", "apres-midi"]
    assert [q.session for q in groups[1].quizzes] == ["matin", "apres-midi"]


def test_group_quizzes_puts_ungrouped_quizzes_in_their_own_bucket(tmp_path):
    (tmp_path / "plain.aiken").write_text("Q ?\nA) x\nB) y\nANSWER: A\n")

    quizzes = discover_quizzes(tmp_path)
    groups = group_quizzes(quizzes)

    assert len(groups) == 1
    assert groups[0].formation is None
    assert len(groups[0].quizzes) == 1
