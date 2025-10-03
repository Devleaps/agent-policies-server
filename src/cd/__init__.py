from src.cd.allow import cd_safe_operations_rule
from src.cd.upward import cd_upward_navigation_rule

all_rules = [cd_upward_navigation_rule, cd_safe_operations_rule]
all_middleware = []