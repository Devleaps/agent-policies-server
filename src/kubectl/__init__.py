from src.kubectl.allow import kubectl_read_only_rule

# Export all rules for the registry
all_rules = [
    kubectl_read_only_rule
]