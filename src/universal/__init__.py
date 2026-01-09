"""Universal file/system utility policies (cd, rm, rmdir, mv, find, sleep, sudo, kill, and common whitelist)."""

from src.universal.whitelist_always import whitelist_always_rule
from src.universal.whitelist_safe_paths import whitelist_safe_paths_rule
from src.universal.custom_always import custom_always_rule
from src.universal.cd_allow import cd_safe_operations_rule
from src.universal.cd_upward import cd_upward_navigation_rule
from src.universal.rm_allow import rm_safe_operations_rule
from src.universal.rmdir_allow import rmdir_safe_operations_rule
from src.universal.mv_allow import mv_safe_operations_rule
from src.universal.find_policy import find_exec_rule, find_safe_operations_rule
from src.universal.sleep_allow import sleep_duration_rule
from src.universal.sudo_block import sudo_block_rule
from src.universal.kill_block import kill_block_rule
from src.universal.awk_block import awk_block_rule
from src.universal.sqlite3_allow import sqlite3_safe_operations_rule
from src.universal.absolute_path_executables import absolute_path_executable_rule
from src.universal.legacy_code_guidance import legacy_code_guidance_rule
from src.universal.readme_license_guidance import readme_license_guidance_rule
from src.universal.tmp_cat_block import tmp_cat_block_rule

# Middleware
from src.universal.bash_middleware import all_middleware as bash_middleware
from src.universal.time_middleware import all_middleware as time_middleware
from src.universal.timeout_middleware import all_middleware as timeout_middleware

all_rules = [
    absolute_path_executable_rule,
    whitelist_always_rule,
    whitelist_safe_paths_rule,
    custom_always_rule,
    cd_upward_navigation_rule,
    cd_safe_operations_rule,
    rm_safe_operations_rule,
    rmdir_safe_operations_rule,
    mv_safe_operations_rule,
    tmp_cat_block_rule,
    find_exec_rule,
    find_safe_operations_rule,
    sleep_duration_rule,
    sudo_block_rule,
    kill_block_rule,
    awk_block_rule,
    sqlite3_safe_operations_rule,
]

all_post_file_edit_rules = [
    legacy_code_guidance_rule,
    readme_license_guidance_rule,
]

all_middleware = [
    *bash_middleware,
    *time_middleware,
    *timeout_middleware
]
