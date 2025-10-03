from src.pip.install_requirements import pip_install_requirements_rule
from src.pip.freeze import pip_freeze_rule, requirements_rule
from src.pip.uninstall import pip_uninstall_rule
from src.pip.install_packages import pip_install_packages_rule

all_rules = [
    pip_install_requirements_rule,
    pip_freeze_rule,
    pip_uninstall_rule,
    pip_install_packages_rule,
    requirements_rule
]