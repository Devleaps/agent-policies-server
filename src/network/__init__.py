"""Network policies (curl, nslookup, webfetch, websearch)."""

from src.network.curl_allow import curl_localhost_rule
from src.network.webfetch_whitelist import webfetch_whitelist_rule
from src.network.websearch_allow import websearch_allow_rule

all_rules = [curl_localhost_rule, webfetch_whitelist_rule, websearch_allow_rule]
