import requests
from scrapy import  selector,Selector
import pymysql
import telnetlib # 测试方法2

import time
import threading
from queue import Queue
import random
from tqdm import tqdm

"""
方法1
判断获取的ip是否可行
该方法为单线程，实在是太慢了，pass掉，搞搞多线程
"""
def judge1_ip(ip, port):
    # 判断给出的代理 ip 是否可用
    http_url = 'http://www.163.com/'
    proxy_url = 'http://{0}:{1}'.format(ip, port)

    print("proxy_url", proxy_url)
    try:
        proxy_dict = {
            'http': proxy_url
        }
        response = requests.get(http_url, proxies=proxy_dict)

    except Exception as e:
        print("[没有返回]代理 ip {0} 及 端口号 {1} 不可用".format(ip, port))
        return False
    else:
        code = response.status_code
        if code >= 200 or code < 300:
            print("代理 ip {0} 及 端口号 {1} 可用".format(ip, port))
            html_doc = str(response.content, 'gbk')
            print(html_doc)
            return True
        else:
            print("[有返回，但是状态码异常]代理 ip {0} 及 端口号 {1} 不可用".format(ip, port))
            return False

"""
测试方法2
"""
def judge2_ip(ip,port):
    try:
        telnetlib.Telnet(ip,port,timeout=2)
        print("代理ip有效！")
        return True
    except:
        print("代理ip无效！")
        return False



"""
爬取代理ip
"""
def crawl_ips():
    headers = {"user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1"}
    for i in range(1, 2): # 制定爬取的页数  这里只爬取西刺代理第1页
        response = requests.get("http://www.xicidaili.com/nn/{0}".format(i), headers=headers)
        selector = Selector(text=response.text)
        all_trs = selector.xpath('//table[@id="ip_list"]//tr[position()>1]')
        ip_list = []
        for tr in all_trs:
            speed = tr.xpath("./td[@class='country'][3]//@title").extract()[0].split('秒')[0]
            ip = tr.xpath("./td[2]/text()").extract()[0]
            port = tr.xpath("./td[3]/text()").extract()[0]
            type = tr.xpath("./td[6]/text()").extract()[0]     
            ip_list.append((ip, port, speed, type))      

            # 暂不进行ip有效性判断，存入数据后统一进行判别（利于提高效率）
            # if judge2_ip(ip,port):
            #     ip_list.append((ip, port, speed, type))
            # else:
            #     pass

        # 方式1：将ip及port写入txt文件,只读'w'方式
        with open('ips.txt','w',encoding='utf-8') as f:
            ip_list=tqdm(ip_list,desc='存入txt文件',leave=True) # 列表变为进度条
            for ip_info in ip_list:
                f.writelines(ip_info[0]+':'+ip_info[1]+'\n')
        # 方式2：将ip及port存入mysql指定数据库中的指定表中
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='123wangchao', charset='utf8', db='proxy_pool')
        cursor = conn.cursor()
        # 先清空原表
        insert_sql1 = ''' truncate table proxy_ip '''
        cursor.execute(insert_sql1)
        conn.commit()
        ip_list=tqdm(ip_list,desc='存入mysql  ',leave=True) # 列表变为进度条
        for ip_info in ip_list:
            insert_sql2 = '''
                    insert into proxy_ip(ip,port,speed,proxy_type)
                    values('{0}','{1}','{2}','{3}')'''.format(ip_info[0], ip_info[1], ip_info[2], ip_info[3])
            # print(insert_sql)
            cursor.execute(insert_sql2)
            conn.commit()
        print('**********************数据获取完成**********************')

if __name__ == "__main__":
    crawl_ips()