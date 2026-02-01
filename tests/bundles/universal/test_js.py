from src.evaluation import evaluate_bash_rules
from tests.helpers import assert_allow, assert_ask


def test_pnpm_install(bash_event):
    # pnpm install can install arbitrary packages, so it requires user confirmation
    assert_ask(evaluate_bash_rules, bash_event("pnpm install"))
    assert_ask(evaluate_bash_rules, bash_event("pnpm install --frozen-lockfile"))
    assert_ask(evaluate_bash_rules, bash_event("pnpm install package-name"))


def test_pnpm_build(bash_event):
    assert_allow(evaluate_bash_rules, bash_event("pnpm build"))
    assert_allow(evaluate_bash_rules, bash_event("pnpm build --production"))
