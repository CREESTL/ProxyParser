from proxy_parser import ProxyURLParser as Parser

"""
1) Run the code
2) Look check 'valid_proxy.txt' file after 
"""

parser = Parser()
parser.get_all_proxies()
parser.validate_proxies()
