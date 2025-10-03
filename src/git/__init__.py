from src.git.allow import git_status_rule
from src.git.diff import git_diff_rule
from src.git.log import git_log_rule
from src.git.restore import git_restore_rule
from src.git.show import git_show_rule

all_rules = [git_status_rule, git_diff_rule, git_log_rule, git_restore_rule, git_show_rule]