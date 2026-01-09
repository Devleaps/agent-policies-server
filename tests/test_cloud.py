import pytest
from src.cloud.docker_build import docker_build_rule
from src.cloud.gh_api import gh_api_rule
from tests.helpers import assert_allow, assert_deny


def test_docker_build(bash_event):
    assert_allow(docker_build_rule, bash_event("docker build ."))
    assert_allow(docker_build_rule, bash_event("docker build -t agent-policy-server ."))
    assert_allow(docker_build_rule, bash_event("docker build -t myapp:1.0.0 ."))
    assert_allow(docker_build_rule, bash_event("docker build -t app ./subdir"))
    assert_allow(docker_build_rule, bash_event("docker build --tag myapp:latest ."))
    assert_deny(docker_build_rule, bash_event("docker build -t app /home/user/project"), "absolute path")


def test_gh_api(bash_event):
    assert_allow(gh_api_rule, bash_event("gh api --method GET /repos/owner/repo"))
    assert_allow(gh_api_rule, bash_event("gh api /repos/owner/repo --method GET"))
    assert_deny(gh_api_rule, bash_event("gh api /repos/owner/repo"))
    assert_deny(gh_api_rule, bash_event("gh api --method POST /repos/owner/repo/issues"))
