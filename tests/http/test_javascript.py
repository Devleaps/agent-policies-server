"""
HTTP Integration Tests for JavaScript Package Managers
"""

from tests.http.conftest import check_policy


def test_npm_install_ask(client, base_event):
    check_policy(client, base_event, "npm install", "ask")


def test_npm_test_allowed(client, base_event):
    check_policy(client, base_event, "npm test", "allow")


def test_npm_run_test_allowed(client, base_event):
    check_policy(client, base_event, "npm run test", "allow")


def test_npm_run_build_allowed(client, base_event):
    check_policy(client, base_event, "npm run build", "allow")


def test_yarn_install_ask(client, base_event):
    check_policy(client, base_event, "yarn install", "ask")


def test_yarn_test_allowed(client, base_event):
    check_policy(client, base_event, "yarn test", "allow")


def test_pnpm_install_ask(client, base_event):
    check_policy(client, base_event, "pnpm install", "ask")


def test_pnpm_build_allowed(client, base_event):
    check_policy(client, base_event, "pnpm build", "allow")
