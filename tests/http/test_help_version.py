"""
HTTP Integration Tests for --help / --version on known executables.
"""

import pytest

from tests.http.conftest import check_policy


@pytest.mark.parametrize(
    "command",
    [
        "git --version",
        "git --help",
        "git commit --help",
        "docker run --help",
        "kubectl --help",
        "kubectl apply --help",
        "terraform --help",
        "terraform apply --help",
        "terragrunt --version",
        "az --help",
        "az group --help",
        "gh --version",
        "uv --version",
        "uv run --help",
        "cargo build --help",
        "python --version",
        "python3 --help",
        "node --version",
        "yarn --version",
        "jq --help",
        "az --version 2>/dev/null",
    ],
)
def test_help_and_version_allowed(client, base_event, command):
    check_policy(client, base_event, command, "allow")


@pytest.mark.parametrize(
    "command",
    [
        "python script.py --help",
        "node script --help",
        "node scripts/build.js --version",
        "yarn some-script --help",
        "uv run script.py --help",
        "uv run pytest --help",
        "npx some-package --help",
        "uvx some-package --help",
        "some-unknown-tool --help",
        "docker run -it --help",
        "cargo run ./x --help",
    ],
)
def test_help_that_could_run_code_defers_to_user(client, base_event, command):
    check_policy(client, base_event, command, None)


@pytest.mark.parametrize(
    "command",
    [
        "terraform apply",
        "terraform apply --help --auto-approve",
        "kubectl apply -f x.yaml",
        "az group create -n rg -l westeurope",
    ],
)
def test_catch_all_denies_still_apply(client, base_event, command):
    check_policy(client, base_event, command, "deny")
