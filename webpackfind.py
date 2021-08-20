#!/usr/bin/env python
# coding: utf-8
import requests, argparse, sys, re, jsbeautifier, os, json, random, platform, traceback
from requests.packages import urllib3
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class webpackfind_class(object):

    def __init__(self):
        self.White = ["w3.org", "baidu.com", "sohu.com", "example.com", "purl.org", "microsoft.com",
                      "openxmlformats.org", "purl.oclc.org", "docs.oasis-open.org", "openoffice.org", "raphaeljs.com",
                      "bing.com", "wallstreetcn.com", "mozilla.org", "mozilla.org"]

    # 使用set对列表去重，并保持列表原来顺序
    def unique(self, arr):
        arr1 = list(set(arr))
        arr1.sort(key=arr.index)
        return arr1  # 返回去重后的数组

    # 从js内容提取URL。返回链接列表：js_url[]
    def Extract_URL(self, Js_content):
        pattern_raw = r"""
              (?:"|')                               # Start newline delimiter
              (
                ((?:[a-zA-Z]{1,10}://|//)           # Match a scheme [a-Z]*1-10 or //
                [^"'/]{1,}\.                        # Match a domainname (any character + dot)
                [a-zA-Z]{2,}[^"']{0,})              # The domainextension and/or path
                |
                ((?:/|\.\./|\./)                    # Start with /,../,./
                [^"'><,;| *()(%%$^/\\\[\]]          # Next character can't be...
                [^"'><,;|()]{1,})                   # Rest of the characters can't be
                |
                ([a-zA-Z0-9_\-/]{1,}/               # Relative endpoint with /
                [a-zA-Z0-9_\-/]{1,}                 # Resource name
                \.(?:[a-zA-Z]{1,4}|action)          # Rest + extension (length 1-4 or action)
                (?:[\?|/][^"|']{0,}|))              # ? mark with parameters
                |
                ([a-zA-Z0-9_\-]{1,}                 # filename
                \.(?:php|asp|aspx|jsp|json|
                     action|html|js|txt|xml)             # . + extension
                (?:\?[^"|']{0,}|))                  # ? mark with parameters
              )
              (?:"|')                               # End newline delimiter
            """
        pattern = re.compile(pattern_raw, re.VERBOSE)
        result = re.finditer(pattern, str(Js_content))
        if result == None:
            return None
        js_url = []
        for match in result:
            if match.group() not in js_url:
                js_url.append(match.group().strip('"').strip("'"))

        rule = r"['\"]+[0-9a-zA-Z-:\./?=]{4,}['\"]+"
        r = re.compile(rule)
        result = r.findall(str(Js_content))
        for i in result:
            if "." in i:
                if "/" in i:
                    js_url.append(i.strip('"').strip("'"))
        js_url = self.unique(js_url)
        return js_url

    # 提取页面源码，返回值为页面源码
    def Extract_html(self, URL, cookie=''):
        header = {"User-Agent": self.uarand(), "Cookie": cookie}
        try:
            re = requests.get(URL, headers=header, timeout=30, verify=False, allow_redirects=False)
            if re.status_code == 200:
                raw = re.content.decode("utf-8", "ignore")
                return raw
            else:
                print("[-]Status_code not 200")
                return None

        except Exception as e:
            print(e)

    # 写入文件
    def save_result(self, filename="", content="", jurisdiction="at"):
        fp = open(filename, jurisdiction, encoding='utf-8')
        fp.write(content + "\n")
        fp.close()

    # 创建文件夹
    def mkdir(self, path):
        path = path.strip()
        path = path.rstrip("\\")
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path)
            print(path + ' 创建成功')
            return True
        else:
            print(path + ' 目录已存在，正在清空目录重新更新文件。。。')
            self.del_file(path)
            return True

    # 清空文件夹内容
    def del_file(self, path):
        ls = os.listdir(path)
        for i in ls:
            c_path = os.path.join(path, i)
            if os.path.isdir(c_path):
                self.del_file(c_path)
            else:
                os.remove(c_path)

    # 返回一个列表，内容为目标字符在字符串中的位置 [3, 7, 10]
    def find_last(self, string, str):
        positions = []
        last_position = -1
        while True:
            position = string.find(str, last_position + 1)
            if position == -1: break
            last_position = position
            positions.append(position)
        return positions

    # 在所有的urls中提取出目标站的子域名
    def find_subdomain(self, urls, mainurl):
        fname = "./js/" + mainurl + "/" + mainurl + "_url_list.txt"
        self.save_result(fname, "", "w")
        url_raw = urlparse(mainurl)
        domain = url_raw.netloc
        miandomain = domain
        positions = self.find_last(domain, ".")
        if len(positions) > 1: miandomain = domain[positions[-2] + 1:]
        subdomains = []
        for url in urls:
            suburl = urlparse(url)
            subdomain = suburl.netloc
            # print(subdomain)
            if subdomain.strip() == "": continue
            if miandomain in subdomain:
                if subdomain not in subdomains:
                    if self.White_list_domain(subdomain):
                        subdomains.append(subdomain)
                        fname = "./js/" + mainurl + "/" + mainurl + "_url_list.txt"
                        self.save_result(fname, subdomain)

        return subdomains

    # 遍历指定目录，显示目录下的所有文件名
    def eachFile(self, filepath):
        url = []
        self.save_result(filepath + "/result.txt", "", "w")
        pathDir = os.listdir(filepath)
        for allDir in pathDir:
            child = os.path.join('%s%s' % (filepath, allDir))
            info = self.readFile(child)
            if info:
                for u in range(len(info)):
                    url.append(info[u])
        return url

    # 读取文件内容并打印
    def readFile(self, filename):
        url = []
        fopen = open(filename, 'r', encoding='utf-8')
        data = self.Extract_URL(fopen.read())
        self.save_result(os.path.dirname(filename) + "/result.txt", "【+】" + filename)
        print("【+】" + filename)
        for x in data:
            print("      " + x)
            self.save_result(os.path.dirname(filename) + "/result.txt", "      " + str(x))
            url.append(x)
        fopen.close()
        return url

    # 白名单判断是否过滤那个域名
    def White_list_domain(self, domain):
        for t in range(len(self.White)):
            if self.White[t] in domain:
                return False
        return True

    # 随机获取ua库
    def uarand(self):
        ie_type = ["chrome", "opera", "firefox", "internetexplorer", "safari"]
        with open('./pc_ua.json', 'r', encoding='utf8')as fp:
            json_data = json.load(fp)
            return json_data[ie_type[random.randint(0, len(ie_type) - 1)]][
                random.randint(0, len(json_data[ie_type[random.randint(0, len(ie_type) - 1)]]) - 1)]

    # url自动化遍历读取文件
    def url_for(self, domain):
        # 判断平台来启动selenium
        sys = platform.system()
        if sys == "Windows":
            path = r"./phantomjs_windows.exe"
        elif sys == "Linux":
            path = r"./phantomjs_liunx_x64"
        else:
            return False
        try:
            driver = webdriver.PhantomJS(executable_path=path)
            driver.get(domain)
            content = driver.page_source
            if urlparse(driver.current_url).netloc != urlparse(domain).netloc:
                content = self.Extract_html(domain)
        except Exception as e:
            print(e)
            content = self.Extract_html(domain)

        url = []
        if content:
            content = BeautifulSoup(content, "html.parser")
            script = content.find_all('script')
            if script:
                try:
                    for a in range(len(script)):
                        try:

                            new_domain = urlparse(domain).scheme + "://" + urlparse(domain).netloc + "/"
                            if script[a].get("src") != None:
                                if "http" in script[a].get("src"):
                                    url.append(script[a].get("src").replace("./", "/"))
                                elif "runtime" in script[a].get("src") or "app" in script[a].get("src") or "finance" in \
                                        script[a].get("src"):
                                    domain_url = new_domain + "/" + script[a].get("src").replace("./", "/")
                                    if "//" in script[a].get("src")[:2]:
                                        domain_url = "http:" + script[a].get("src").replace("./", "/")
                                        content = self.Extract_html(domain_url)
                                    else:
                                        content = self.Extract_html(domain_url)
                                    if content == None:
                                        try:
                                            fname = "./js/" + urlparse(domain).netloc + "/" + urlparse(
                                                domain).netloc + "_error_js_url_list.txt"
                                            self.save_result(fname,
                                                             new_domain + script[a].get("src").replace("./", "/"))
                                        except Exception as e:
                                            print("[E]Write File Failed!!%s" % e)
                                        pass
                                    if content.find("static/js") != -1:
                                        content = content[content.find("static/js"):-1]
                                        content = content[:content.find(".js")]
                                        content = re.findall(r'"(chunk-.*?)":"(.*?)"', str(content))
                                        for co in range(len(content)):
                                            url.append(new_domain + "/static/js/" + content[co][0] + "." + content[co][
                                                1] + ".js")
                                    else:
                                        content = content[content.find("js/"):-1]
                                        content = content[:content.find(".js")]
                                        content = re.findall(r'"(chunk-.*?)":"(.*?)"', str(content))
                                        for co in range(len(content)):
                                            url.append(
                                                new_domain + "/js/" + content[co][0] + "." + content[co][1] + ".js")
                                elif "manifest" in script[a].get("src"):
                                    domain_url = new_domain + "/" + script[a].get("src").replace("./", "/")
                                    if "//" in script[a].get("src")[:2]:
                                        domain_url = "http:" + script[a].get("src").replace("./", "/")
                                        content = self.Extract_html(domain_url)
                                    else:
                                        content = self.Extract_html(domain_url)
                                    url.append(domain_url)
                                    if content == None:
                                        try:
                                            fname = "./js/" + urlparse(domain).netloc + "/" + urlparse(
                                                domain).netloc + "_error_js_url_list.txt"
                                            self.save_result(fname, domain_url)
                                        except Exception as e:
                                            print("[E]Write File Failed!!%s" % e)
                                        pass
                                    content_b = re.findall(r'([0-9]+?):"(.*?)"', str(content))
                                    if content_b:
                                        for co in range(len(content_b)):
                                            url.append(
                                                new_domain + "/static/js/" + content_b[co][0] + "." + content_b[co][
                                                    1] + ".js")
                                    else:
                                        webpackJsonp = 0
                                        for fomnew in range(len(script)):
                                            if "app.js" in str(script[fomnew].get("src")):
                                                newcontent = self.Extract_html(
                                                    new_domain + "/" + str(script[fomnew].get("src")).replace("./",
                                                                                                              "/"))
                                                if newcontent:
                                                    webpackJsonp = \
                                                        re.findall(r'webpackJsonp\(\[(\d+?)\]\,', str(newcontent))[0]
                                                break
                                        if webpackJsonp != 0:
                                            for num in range(0, int(webpackJsonp) + 1):
                                                if content.find("static/js") != -1:
                                                    url.append(new_domain + str(urlparse(
                                                        new_domain + "/" + str(script[fomnew].get("src")).replace("./",
                                                                                                                  "/")).path).replace(
                                                        "///", "").split("/")[1] + "/static/js/" + str(num) + ".js")
                                                else:
                                                    url.append(new_domain + str(urlparse(
                                                        new_domain + "/" + str(script[fomnew].get("src")).replace("./",
                                                                                                                  "/")).path).replace(
                                                        "///", "").split("/")[1] + "/js/" + str(num) + ".js")
                                else:
                                    url.append(new_domain + "/" + script[a].get("src").replace("./", "/"))
                            else:
                                if str(script[a]).find("static/js") != -1:
                                    content = str(script[a])
                                    content = content[content.find("static/js"):-1]
                                    content = content[:content.find(".js")]
                                    content = re.findall(r'"(chunk-.*?)":"(.*?)"', str(content))
                                    for co in range(len(content)):
                                        url.append(
                                            new_domain + "/static/js/" + content[co][0] + "." + content[co][1] + ".js")
                                elif str(script[a]).find("js/") != -1:
                                    content = str(script[a])
                                    content = content[content.find("js/"):-1]
                                    content = content[:content.find(".js")]
                                    content = re.findall(r'"(chunk-.*?)":"(.*?)"', str(content))
                                    for co in range(len(content)):
                                        url.append(new_domain + "/js/" + content[co][0] + "." + content[co][1] + ".js")
                                elif str(script[a].text).find(".js") != -1:
                                    content = str(script[a].text).replace(" ", "").replace("\n", "").replace("\"", "'")
                                    content = re.findall(r'src=\'(.*?)\'', content)
                                    for co in range(len(content)):
                                        if urlparse(content[co]).netloc:
                                            url.append(content[co])
                                        else:
                                            url.append(
                                                new_domain + content[co][:content[co].find(".js") + 3].replace("./",
                                                                                                               ""))
                                else:
                                    content = re.findall(r'([0-9]+?):"(.*?)"', str(content))
                                    if content:
                                        for co in range(len(content)):
                                            url.append(
                                                new_domain + "/js/" + content[co][0] + "." + content[co][1] + ".js")
                        except Exception as e:
                            print(traceback.print_exc())
                            pass
                except Exception as e:
                    print(traceback.print_exc())
                    pass
            # 解决重复url问题
            new_url = []
            for u in range(len(url)):
                if self.White_list_domain(url[u]):
                    url[u] = url[u].replace("///", "/")
                    if url[u].find("?") == -1:
                        new_url.append(url[u].replace("///", "/"))
                    else:
                        new_url.append(url[u][:url[u].find("?")].replace("///", "/"))
            url = list(set(new_url))
            for u in range(len(url)):
                content = self.Extract_html(url[u])
                fname = "./js/" + urlparse(domain).netloc + "/" + url[u].split('/')[-1]
                try:
                    fp = open(fname, "at", encoding='utf-8')
                    fp.write(jsbeautifier.beautify(content))
                    fp.close()
                except Exception as e:
                    print("[E]Write File Failed!!%s" % e)
                    return False
            try:
                fname = "./js/" + urlparse(domain).netloc + "/" + urlparse(domain).netloc + "_js_url_list.txt"
                for u in range(len(url)):
                    self.save_result(fname, url[u])
                return True
            except Exception as e:
                print("[E]Write File Failed!!%s" % e)
                return False
        elif content == None:
            try:
                fname = "./js/" + urlparse(domain).netloc + "/" + urlparse(domain).netloc + "_error_js_url_list.txt"
                self.save_result(fname, domain)
                return True
            except Exception as e:
                print("[E]Write File Failed!!%s" % e)
                return False

    def find_osskey(self, domain):
        key_name = ['accessKeyId', 'accessKeySecret', 'accesskeyid', 'accesskeysecret', 'TmpSecretId', 'TmpSecretKey',
                    'secretAccessKey',
                    'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
        file_name = f'./js/{urlparse(domain).netloc}'
        print(file_name)
        for root, ds, fs in os.walk(file_name):
            for f in fs:
                if f.endswith('.js'):
                    fullname = os.path.join(root, f)
                    # yield fullname
                    with open(fullname, 'r', encoding='utf-8')  as f:
                        lines = f.readlines()
                        for lines in lines:
                            for key in key_name:

                                if key in lines:
                                    print(lines)


if __name__ == "__main__":
    urllib3.disable_warnings()
    parser = argparse.ArgumentParser(epilog='\tExample: \r\npython ' + sys.argv[0] + " -u http://www.baidu.com")
    parser.add_argument("-j", "--jsfile", help="遍历目录里面文件")
    parser.add_argument("-u", "--urlfile", help="自动化遍历html里面js")
    parser.add_argument("-s", "--subdomain", default=0, help="提取js中存在的url")
    args = parser.parse_args()
    webpackfind = webpackfind_class()
    if args.jsfile:
        info = webpackfind.eachFile(args.jsfile)
        if args.subdomain == 0:
            info = webpackfind.find_subdomain(info, os.path.basename(os.path.realpath(args.jsfile)))
            print(
                f"\n\n{'=' * 10}扫描子域名结果{'=' * 10}\n")
            print(info)

    elif args.urlfile:
        if urlparse(args.urlfile).netloc:
            if webpackfind.mkdir("./js/" + urlparse(args.urlfile).netloc + "/"):
                info = webpackfind.url_for(args.urlfile)
                if info:
                    info = webpackfind.eachFile("./js/" + urlparse(args.urlfile).netloc + "/")
                    if args.subdomain == 0:
                        info = webpackfind.find_subdomain(info, urlparse(args.urlfile).netloc)
                        print(
                            f"\n\n{'=' * 10}扫描子域名结果{'=' * 10}\n")
                        print(info)

                        print(
                            f"\n\n{'=' * 10}oss_key结果{'=' * 10}\n")
                        webpackfind.find_osskey(args.urlfile)


        else:
            print("python3 webpackfind.py -u http://www.baidu.com")
    else:  # URL列表
        print("python3 webpackfind.py -u http://www.baidu.com")
