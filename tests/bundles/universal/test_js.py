from src.bundles_impl import bash_rules_bundle_universal
from tests.helpers import assert_allow, assert_ask


def test_pnpm_install(bash_event):
    # pnpm install can install arbitrary packages, so it requires user confirmation
    assert_ask(bash_rules_bundle_universal, bash_event("pnpm install"))
    assert_ask(bash_rules_bundle_universal, bash_event("pnpm install --frozen-lockfile"))
    assert_ask(bash_rules_bundle_universal, bash_event("pnpm install package-name"))


def test_pnpm_build(bash_event):
    assert_allow(bash_rules_bundle_universal, bash_event("pnpm build"))
    assert_allow(bash_rules_bundle_universal, bash_event("pnpm build --production"))
