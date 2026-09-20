from quiz.adapters.identity_hostname.provider import (
    GENERIC_HOSTNAMES,
    HostnameIdentityProvider,
)
from quiz.domain.models import Student


def test_resolves_student_from_first_hostname_label():
    provider = HostnameIdentityProvider(
        hostname_fn=lambda: "sacha.brx2022.uptime-formation.fr",
        prompt_fn=lambda: "unused",
    )

    student = provider.resolve_student()

    assert student == Student(display_name="Sacha")


def test_resolves_bare_hostname_without_domain():
    provider = HostnameIdentityProvider(
        hostname_fn=lambda: "julien",
        prompt_fn=lambda: "unused",
    )

    assert provider.resolve_student() == Student(display_name="Julien")


def test_falls_back_to_prompt_when_hostname_is_generic():
    for generic in GENERIC_HOSTNAMES:
        provider = HostnameIdentityProvider(
            hostname_fn=lambda h=generic: h,
            prompt_fn=lambda: "Marie Dupont",
        )

        assert provider.resolve_student() == Student(display_name="Marie Dupont")


def test_falls_back_to_prompt_when_hostname_is_empty():
    provider = HostnameIdentityProvider(
        hostname_fn=lambda: "",
        prompt_fn=lambda: "Marie Dupont",
    )

    assert provider.resolve_student() == Student(display_name="Marie Dupont")
