"""
HTTP Integration Tests for Cloud CLI Commands
"""

from tests.http.conftest import check_policy


def test_docker_ps_allowed(client, base_event):
    check_policy(client, base_event, "docker ps", "allow")


def test_docker_build_allowed(client, base_event):
    check_policy(client, base_event, "docker build -t myapp .", "allow")


def test_terraform_fmt_allowed(client, base_event):
    check_policy(client, base_event, "terraform fmt", "allow")


def test_terraform_plan_allowed(client, base_event):
    check_policy(client, base_event, "terraform plan", "allow")


def test_terraform_apply_denied(client, base_event):
    check_policy(client, base_event, "terraform apply", "deny")


def test_terraform_destroy_denied(client, base_event):
    check_policy(client, base_event, "terraform destroy", "deny")


def test_terraform_init_denied(client, base_event):
    check_policy(client, base_event, "terraform init", "deny")


def test_terragrunt_plan_allowed(client, base_event):
    check_policy(client, base_event, "terragrunt plan", "allow")


def test_terragrunt_apply_denied(client, base_event):
    check_policy(client, base_event, "terragrunt apply", "deny")


def test_az_list_allowed(client, base_event):
    check_policy(client, base_event, "az group list", "allow")


def test_az_create_denied(client, base_event):
    check_policy(client, base_event, "az group create -n test", "deny")


def test_az_delete_denied(client, base_event):
    check_policy(client, base_event, "az group delete -n test", "deny")


def test_kubectl_get_allowed(client, base_event):
    check_policy(client, base_event, "kubectl get pods", "allow")


def test_kubectl_delete_denied(client, base_event):
    check_policy(client, base_event, "kubectl delete pod mypod", "deny")


def test_gh_pr_view_allowed(client, base_event):
    check_policy(client, base_event, "gh pr view 123", "allow")


def test_gh_pr_diff_allowed(client, base_event):
    check_policy(client, base_event, "gh pr diff 30", "allow")


def test_gh_pr_create_defers_to_user(client, base_event):
    check_policy(client, base_event, "gh pr create --title 'Test'", None)
