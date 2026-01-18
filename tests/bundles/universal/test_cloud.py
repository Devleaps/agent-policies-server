import pytest
from src.bundles_impl import bash_rules_bundle_universal
from tests.helpers import assert_allow, assert_deny, assert_pass


def test_docker_build(bash_event):
    assert_allow(bash_rules_bundle_universal, bash_event("docker build ."))
    assert_allow(bash_rules_bundle_universal, bash_event("docker build -t agent-policy-server ."))
    assert_allow(bash_rules_bundle_universal, bash_event("docker build -t myapp:1.0.0 ."))
    assert_allow(bash_rules_bundle_universal, bash_event("docker build -t app ./subdir"))
    assert_allow(bash_rules_bundle_universal, bash_event("docker build --tag myapp:latest ."))
    assert_deny(bash_rules_bundle_universal, bash_event("docker build -t app /home/user/project"))


def test_gh_api(bash_event):
    assert_allow(bash_rules_bundle_universal, bash_event("gh api --method GET /repos/owner/repo"))
    assert_allow(bash_rules_bundle_universal, bash_event("gh api /repos/owner/repo --method GET"))
    assert_deny(bash_rules_bundle_universal, bash_event("gh api /repos/owner/repo"))
    assert_deny(bash_rules_bundle_universal, bash_event("gh api --method POST /repos/owner/repo/issues"))


def test_gh_read_only_commands(bash_event):
    assert_allow(bash_rules_bundle_universal, bash_event("gh issue list"))
    assert_allow(bash_rules_bundle_universal, bash_event("gh issue view 123"))
    assert_allow(bash_rules_bundle_universal, bash_event("gh issue status"))
    assert_allow(bash_rules_bundle_universal, bash_event("gh pr list"))
    assert_allow(bash_rules_bundle_universal, bash_event("gh pr view 456"))
    assert_allow(bash_rules_bundle_universal, bash_event("gh pr status"))
    assert_allow(bash_rules_bundle_universal, bash_event("gh repo list"))
    assert_allow(bash_rules_bundle_universal, bash_event("gh repo view owner/repo"))
    assert_allow(bash_rules_bundle_universal, bash_event("gh run list"))
    assert_allow(bash_rules_bundle_universal, bash_event("gh run view 789"))
    assert_allow(bash_rules_bundle_universal, bash_event("gh workflow list"))
    assert_allow(bash_rules_bundle_universal, bash_event("gh workflow view build.yml"))
    assert_allow(bash_rules_bundle_universal, bash_event("gh release list"))
    assert_allow(bash_rules_bundle_universal, bash_event("gh release view v1.0.0"))
    assert_allow(bash_rules_bundle_universal, bash_event("gh auth status"))


def test_terraform_allowed_commands(bash_event):
    assert_allow(bash_rules_bundle_universal, bash_event("terraform fmt"))
    assert_allow(bash_rules_bundle_universal, bash_event("terraform fmt -recursive"))
    assert_allow(bash_rules_bundle_universal, bash_event("terraform fmt -check"))
    assert_allow(bash_rules_bundle_universal, bash_event("terraform plan"))
    assert_allow(bash_rules_bundle_universal, bash_event("terraform plan -out=plan.tfplan"))


def test_terraform_denied_commands(bash_event):
    assert_deny(bash_rules_bundle_universal, bash_event("terraform apply"))
    assert_deny(bash_rules_bundle_universal, bash_event("terraform apply -auto-approve"))
    assert_deny(bash_rules_bundle_universal, bash_event("terraform destroy"))
    assert_deny(bash_rules_bundle_universal, bash_event("terraform init"))
    assert_deny(bash_rules_bundle_universal, bash_event("terraform import"))


def test_terragrunt_allowed_commands(bash_event):
    assert_allow(bash_rules_bundle_universal, bash_event("terragrunt plan"))
    assert_allow(bash_rules_bundle_universal, bash_event("terragrunt plan -out=plan.tfplan"))


def test_terragrunt_denied_commands(bash_event):
    assert_deny(bash_rules_bundle_universal, bash_event("terragrunt apply"))
    assert_deny(bash_rules_bundle_universal, bash_event("terragrunt apply -auto-approve"))
    assert_deny(bash_rules_bundle_universal, bash_event("terragrunt destroy"))
    assert_deny(bash_rules_bundle_universal, bash_event("terragrunt run-all apply"))


def test_azure_cli_allowed_commands(bash_event):
    assert_allow(bash_rules_bundle_universal, bash_event("az vm list"))
    assert_allow(bash_rules_bundle_universal, bash_event("az group list --output table"))
    assert_allow(bash_rules_bundle_universal, bash_event("az account list"))
    assert_allow(bash_rules_bundle_universal, bash_event("az vm show --name myvm"))
    assert_allow(bash_rules_bundle_universal, bash_event("az group show --name myrg"))


def test_azure_cli_denied_commands(bash_event):
    assert_deny(bash_rules_bundle_universal, bash_event("az vm delete --name myvm"))
    assert_deny(bash_rules_bundle_universal, bash_event("az vm create --name myvm"))
    assert_deny(bash_rules_bundle_universal, bash_event("az group delete --name myrg"))
    assert_deny(bash_rules_bundle_universal, bash_event("az storage account update"))
