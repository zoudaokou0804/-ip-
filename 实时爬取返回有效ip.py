import requests
import time
import threading
from queue import Queue
import random
import pandas as pd
from scrapy import Selector
import pymysql
import telnetlib # 测试方法2

# https://www.xicidaili.com/nn/ 西刺代理
# http://tool.chinaz.com/port/ 网站验证ip有效性
"""
从列表中随机获取请求头的方法
https://www.toolnb.com/tools/createuseragent.html 通过该网站可以随机生成请求头
"""
def getheaders():
    user_agent_list = [
        "Mozilla/5.0 (Windows; U; Windows NT 5.01) AppleWebKit/535.15.5 (KHTML, like Gecko) Version/5.0 Safari/535.15.5",
        "Mozilla/5.0 (Android 1.6; Mobile; rv:49.0) Gecko/49.0 Firefox/49.0",
        "Mozilla/5.0 (compatible; MSIE 7.0; Windows 95; Trident/5.1)",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10_5_7 rv:4.0; bn-IN) AppleWebKit/533.33.6 (KHTML, like Gecko) Version/4.0.1 Safari/533.33.6",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 5_1_1 like Mac OS X) AppleWebKit/531.2 (KHTML, like Gecko) CriOS/30.0.806.0 Mobile/47E619 Safari/531.2",
        "Opera/8.37.(X11; Linux i686; zh-SG) Presto/2.9.175 Version/11.00",
        "Opera/8.43.(Windows NT 5.2; fy-NL) Presto/2.9.179 Version/12.00",
        "Opera/9.29.(X11; Linux i686; ca-FR) Presto/2.9.161 Version/11.00",
        "Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.0; Trident/4.0)",
        "Mozilla/5.0 (Android 2.0.1; Mobile; rv:66.0) Gecko/66.0 Firefox/66.0"
    ]
    UserAgent = random.choice(user_agent_list)
    headers = {"User-Agent": UserAgent}
    return headers

# 利用telnetlib测试方法，不太准，建议以下面方法为主
def test_ip(ip,port):
    try:
        telnetlib.Telnet(ip,port,timeout=2)
        print(ip+':'+port, '有效ip')
        return True
    except:
        print("代理ip无效！")
        return False


"""
is_enable函数用来判断获取的ip是否有效
ip_port字符串形势如 "112.87.79.123:9999"(ip:port)
"""
def is_enable(ip,port):
    proxies = {
        "http": "http://" + ip+':'+port,
        "https": "http://" +  ip+':'+port,
    }
    try:
        res = requests.get('https://www.baidu.com/',
                           headers=getheaders(),
                           proxies=proxies,
                           timeout=2)
        print(ip+':'+port, '有效ip')
        return True
    except Exception as e:
        # print(ip+':'+port, '无效ip')
        return False

"""
crawl_ips函数：采集西祠代理ip方法
参数methodflag代表后面存入数据的方式
methodflag=1采用存入数据库方式
methodflag=0采用写入txt文本方式
pgn:要爬取西祠代理ip的页面数量
"""
def crawl_ips(pgn=1): 
    print('获取代理IP中......')
    for i in range(1, pgn+1): # 制定爬取的页数  这里只爬取西刺代理第1页
        response = requests.get("http://www.xicidaili.com/nn/{0}".format(i), headers=getheaders())
        selector = Selector(text=response.text)
        all_trs = selector.xpath('//table[@id="ip_list"]//tr[position()>1]')
        ip_list = []
        for tr in all_trs:
            # speed = tr.xpath("./td[@class='country'][3]//@title").extract()[0].split('秒')[0]
            ip = tr.xpath("./td[2]/text()").extract()[0]
            port = tr.xpath("./td[3]/text()").extract()[0]
            # type = tr.xpath("./td[6]/text()").extract()[0]     
            if is_enable(ip,port):
                print('获取代理IP完成')
                return ip,port
    



if __name__ == '__main__':
    crawl_ips()
