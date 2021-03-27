import sys
import re
import queue
import threading
import requests


class ProxyParser:
    """
    Parses lots of proxy IPs from different sites, validates each of them, logs valid once into file
    """

    def __init__(self):
        # max threads used for work
        self.threads = 20
        # timeout for request
        self.timeout = 3
        # file to write checked proxies to
        self.output_file = 'valid_proxy.txt'
        # list of proxies
        self.proxies = []
        # checking via https
        self.https = True
        # threads for working with source links
        self.source_threads = []
        # site to check if proxy is working
        self.check_website = "httpbin.org/ip"
        # number of working and not working proxies
        self.dead = 0
        self.alive = 0
        # LIFO of proxies
        self.q = queue.Queue()
        # list of sites to parse proxies from
        self.proxy_sources = [
        ["http://spys.me/proxy.txt", "%ip%:%port% "],
        ["http://www.httptunnel.ge/ProxyListForFree.aspx", " target=\"_new\">%ip%:%port%</a>"],
        ["https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.json",
         "\"ip\":\"%ip%\",\"port\":\"%port%\","],
        ["https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list",
         '"host": "%ip%".*?"country": "(.*?){2}",.*?"port": %port%'],
        ["https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt", '%ip%:%port% (.*?){2}-.-S \\+'],
        ["https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt", '%ip%", "type": "http", "port": %port%'],
        ["https://www.us-proxy.org/",
         "<tr><td>%ip%<\\/td><td>%port%<\\/td><td>(.*?){2}<\\/td><td class='hm'>.*?<\\/td><td>.*?<\\/td><td class='hm'>.*?<\\/td><td class='hx'>(.*?)<\\/td><td class='hm'>.*?<\\/td><\\/tr>"],
        ["https://free-proxy-list.net/",
         "<tr><td>%ip%<\\/td><td>%port%<\\/td><td>(.*?){2}<\\/td><td class='hm'>.*?<\\/td><td>.*?<\\/td><td class='hm'>.*?<\\/td><td class='hx'>(.*?)<\\/td><td class='hm'>.*?<\\/td><\\/tr>"],
        ["https://www.sslproxies.org/",
         "<tr><td>%ip%<\\/td><td>%port%<\\/td><td>(.*?){2}<\\/td><td class='hm'>.*?<\\/td><td>.*?<\\/td><td class='hm'>.*?<\\/td><td class='hx'>(.*?)<\\/td><td class='hm'>.*?<\\/td><\\/tr>"],
        ["https://www.proxy-list.download/api/v0/get?l=en&t=https", '"IP": "%ip%", "PORT": "%port%",'],
        ["https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=6000&country=all&ssl=yes&anonymity=all",
         "%ip%:%port%"],
        ["https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt", "%ip%:%port%"],
        ["https://raw.githubusercontent.com/shiftytr/proxy-list/master/proxy.txt", "%ip%:%port%"],
        ["https://proxylist.icu/", "<td>%ip%:%port%</td><td>http<"],
        ["https://proxylist.icu/proxy/1", "<td>%ip%:%port%</td><td>http<"],
        ["https://proxylist.icu/proxy/2", "<td>%ip%:%port%</td><td>http<"],
        ["https://proxylist.icu/proxy/3", "<td>%ip%:%port%</td><td>http<"],
        ["https://proxylist.icu/proxy/4", "<td>%ip%:%port%</td><td>http<"],
        ["https://proxylist.icu/proxy/5", "<td>%ip%:%port%</td><td>http<"],
        ["https://www.hide-my-ip.com/proxylist.shtml", '"i":"%ip%","p":"%port%",'],
        ["https://raw.githubusercontent.com/scidam/proxy-list/master/proxy.json", '"ip": "%ip%",\n.*?"port": "%port%",']
    ]


    def fetch_from_sources(self, url, custom_regex):
        """ Fetches lists of proxies IPs from sites """
        n = 0
        proxy_list = requests.get(url, timeout=5).text
        proxy_list = proxy_list.replace('null', '"N/A"')
        custom_regex = custom_regex.replace('%ip%', '([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3})')
        custom_regex = custom_regex.replace('%port%', '([0-9]{1,5})')
        for proxy in re.findall(re.compile(custom_regex), proxy_list):
            self.proxies.append(proxy[0] + ":" + proxy[1])
            n += 1
        sys.stdout.write("{0: >5} proxies fetched from {1}\n".format(n, url))

    def find_proxies(self):
        """ Creates a file with working proxy IPs """

        # fetching all IPs to check them later
        for source in self.proxy_sources:
            t = threading.Thread(target=self.fetch_from_sources, args=(source[0], source[1]))
            self.source_threads.append(t)
            t.start()
        for t in self.source_threads:
            t.join()
        proxies_unique = list(set(self.proxies))
        print("{0: >5} proxies fetched total, {1} unique.".format(len(self.proxies), len(proxies_unique)))
        self.proxies = proxies_unique

        # filling the LIFO
        for x in self.proxies:
            self.q.put([x, "N/A"])

        # checking each proxy and writing valid once into file
        with open(self.output_file, 'w') as f:

            def check_proxies():

                while not self.q.empty():
                    proxy = self.q.get()
                    try:
                        resp = requests.get(("https" if self.https else "http") + ("://" + self.check_website),
                                            proxies={'http': 'http://' + proxy[0], 'https': 'http://' + proxy[0]},
                                            timeout=self.timeout)
                        if resp.status_code != 200:
                            pass
                        f.write("{}|{}|{:.2f}s\n".format(proxy[0], proxy[1], resp.elapsed.total_seconds()))
                        if self.alive % 30 == 0:
                            f.flush()
                        self.alive += 1
                    except:
                        self.dead += 1

                    sys.stdout.write(
                        "\rChecked %{:.2f} - (Alive: {} - Dead: {})".format((self.alive + self.dead) / len(self.proxies) * 100, self.alive, self.dead))
                    sys.stdout.flush()

            # proxies are checked in multiple threads
            threads_list = []
            for i in range(0, self.threads):
                t = threading.Thread(target=check_proxies)
                t.start()
                threads_list.append(t)
            for t in threads_list:
                t.join()

            # writing info into console
            sys.stdout.write("\rCompleted - Alive: {} - Dead: {}         \n".format(self.alive, self.dead))
            print("")


p = ProxyParser()
p.find_proxies()