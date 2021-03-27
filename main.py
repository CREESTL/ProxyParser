from proxy_parser import ProxyURLParser as OldParser
from proxy_parser_v2 import ProxyParser as Parser

"""
1) Run the code
2) Look check 'valid_proxy.txt' file after 
"""

# --old version with less sites to parse
# parser = Parser()
# parser.get_all_proxies()
# parser.validate_proxies()

# --new version with variety of sites to parse
parser = Parser()
parser.find_proxies()

