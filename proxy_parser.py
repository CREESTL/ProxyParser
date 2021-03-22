import requests
from bs4 import BeautifulSoup


class ProxyURLParser:
    """
    Class is used to parse list of working proxies from specific website
    """

    def __init__(self):
        self.ip_list = []
        self.ports_list = []
        self.all_proxy_list = []
        self.valid_proxy_list = []
        # that's the site to parse
        self.resource_link = 'https://free-proxy-list.net/'

    @ staticmethod
    def save_to_file(proxy_list):
        """ Saves all valid proxies into file """
        with open('valid_proxy.txt', 'w') as f:
            for string in proxy_list:
                f.write(string + '\n')

    def read_from_file(self):
        """ Reads all proxies from file """
        with open('valid_proxy.txt', 'r') as f:
            self.all_proxy_list = f.readlines()

    def get_all_proxies(self):
        """ Parses all proxies from website"""
        response = requests.get(self.resource_link).text
        soup = BeautifulSoup(response, 'lxml')

        # looking for table elements
        tds = list(soup.find_all('td'))

        # getting all IPs
        for td in tds:
            td = str(td)[4:-5]
            parts = td.split('.')
            try:
                if int(parts[0]) in range(0, 255):
                    if 7 < len(td) < 15:
                        if int(td[0]) in range(0, 255):
                            self.ip_list.append(td)
            except ValueError:
                pass

        # getting all ports
        for td in tds:
            td = str(td)[4:-5]
            try:
                int(td)
                self.ports_list.append(td)
            except ValueError:
                pass

        # combining all together
        for ip, port in zip(self.ip_list, self.ports_list):
            self.all_proxy_list.append(ip + ":" + port)

    def validate_proxies(self):
        """ Checks if all proxies are working """
        for proxy in self.all_proxy_list:
            print(f'Validating proxy {proxy}...')
            link = 'http://icanhazip.com/'
            try:
                response = requests.get(link, proxies={'https': proxy}, timeout=2)
                if response.status_code == 200:
                    print(f'GOOD PROXY')
                    self.valid_proxy_list.append(proxy)
                    self.save_to_file(self.valid_proxy_list)
            except:
                pass



