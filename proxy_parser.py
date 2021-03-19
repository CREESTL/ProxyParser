import requests
from bs4 import BeautifulSoup

class ProxyURLParser:

    def __init__(self):
        self.ip_list = []
        self.ports_list = []
        self.all_proxy_list = []
        self.valid_proxy_list = []
        self.resource_link = 'https://free-proxy-list.net/'

    # function saves all valid proxies into file
    @ staticmethod
    def save_to_file(proxy_list):
        with open('valid_proxy.txt', 'w') as f:
            for string in proxy_list:
                f.write(string + '\n')

    # function reads the list of valid proxies from file
    def read_from_file(self):
        with open('valid_proxy.txt', 'r') as f:
            self.all_proxy_list = f.readlines()

    # function parses all proxies from website
    def get_all_proxies(self):
        response = requests.get(self.resource_link).text
        soup = BeautifulSoup(response, 'lxml')

        # looking for table elements
        tds = list(soup.find_all('td'))

        # getting all IPs
        for td in tds:
            td = str(td)[4:-5]
            parts = td.split('.')
            try:
                if int(parts[0]) in range(0, 200):
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

    # function checks if each of proxies is working
    def validate_proxies(self):
        for proxy in self.all_proxy_list:
            print(f'Validating proxy {proxy}...')
            link = 'http://icanhazip.com/'
            try:
                response = requests.get(link, proxies={'http': proxy, 'https': proxy}, timeout=2)
                if response.status_code == 200:
                    print(response.text)
                    print(f'GOOD PROXY')
                    self.valid_proxy_list.append(proxy)
                    self.save_to_file(self.valid_proxy_list)
            except:
                pass



