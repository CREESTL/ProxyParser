import re
import threading
import requests


class AnonProxyChecker:

    # path_to_list is a path to the .txt list of bought proxies
    def __init__(self, path_to_list):
        self.valid_proxies = self.read_from_file(path_to_list)
        self.anon_proxies = []
        self.clear_log()
        self.threads = 20
        self.timeout = 3
        self.link = 'https://httpbin.org/'

    @staticmethod
    def read_from_file(path):
        """ Reads all proxies from file """
        with open(path, 'r') as f:
            valid = f.readlines()
        return valid

    def clear_log(self):
        try:
            f = open('anon_proxy.txt', 'w')
        except FileNotFoundError:
            return

    def check_if_IP(self, text):
        """ Checks if IP is in the text """
        regex = '"%ip%:%port%'
        regex = regex.replace('%ip%', '([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3})')
        regex = regex.replace('%port%', '([0-9]{1,5})')
        found_ips = re.findall(re.compile(regex), text)
        if found_ips:
            return True
        return False

    @staticmethod
    def save_to_file(proxy):
        """ Saves anonymous proxies into file"""
        with open('anon_proxy.txt', 'a') as f:
            f.write(proxy)

    def check_if_proxy_anon(self):
        """ Checks if each proxy from the list is not only valid, but anonymous """
        while self.valid_proxies:
            proxy = self.valid_proxies.pop()
            try:
                resp = requests.get(self.link, proxies={'http': 'http://' + proxy, 'https': 'http://' + proxy}, timeout=self.timeout)
                text = resp.text
                headers = ''.join(header for header in resp.headers)
                if resp.status_code == 200:
                    if (not self.check_if_IP(text)) and (not self.check_if_IP(headers)):
                        self.anon_proxies.append(proxy)
                        self.save_to_file(proxy)
            except:
                pass

    def find_anon_proxies(self):
        # proxies are checked in multiple threads
        threads_list = []
        for i in range(0, self.threads):
            t = threading.Thread(target=self.check_if_proxy_anon)
            t.start()
            threads_list.append(t)
        for t in threads_list:
            t.join()


if __name__ == "__main__":
    p = AnonProxyChecker('valid_proxy.txt')
    p.find_anon_proxies()

