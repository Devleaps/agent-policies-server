"""
HTTP Integration Tests for Podman Commands
"""

from tests.http.conftest import check_policy


def test_podman_machine_list_allowed(client, base_event):
    check_policy(client, base_event, "podman machine list", "allow")


def test_podman_machine_ps_allowed(client, base_event):
    check_policy(client, base_event, "podman machine ps", "allow")


def test_podman_machine_inspect_allowed(client, base_event):
    check_policy(client, base_event, "podman machine inspect myvm", "allow")


def test_podman_machine_exists_allowed(client, base_event):
    check_policy(client, base_event, "podman machine exists myvm", "allow")


def test_podman_machine_ssh_ask(client, base_event):
    check_policy(client, base_event, "podman machine ssh myvm", "ask")


def test_podman_machine_init_allowed(client, base_event):
    check_policy(client, base_event, "podman machine init", "allow")


def test_podman_machine_start_allowed(client, base_event):
    check_policy(client, base_event, "podman machine start myvm", "allow")


def test_podman_machine_stop_allowed(client, base_event):
    check_policy(client, base_event, "podman machine stop myvm", "allow")


def test_podman_ps_allowed(client, base_event):
    check_policy(client, base_event, "podman ps", "allow")


def test_podman_inspect_allowed(client, base_event):
    check_policy(client, base_event, "podman inspect mycontainer", "allow")


def test_podman_images_allowed(client, base_event):
    check_policy(client, base_event, "podman images", "allow")


def test_podman_volume_ls_allowed(client, base_event):
    check_policy(client, base_event, "podman volume ls", "allow")


def test_podman_network_ls_allowed(client, base_event):
    check_policy(client, base_event, "podman network ls", "allow")


def test_podman_version_allowed(client, base_event):
    check_policy(client, base_event, "podman version", "allow")


def test_podman_info_allowed(client, base_event):
    check_policy(client, base_event, "podman info", "allow")


def test_podman_system_df_allowed(client, base_event):
    check_policy(client, base_event, "podman system df", "allow")
