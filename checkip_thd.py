import requests
import time
import threading
from queue import Queue
import random
import pymysql
import pandas as pd

# 随机获取请求头函数
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


def is_enable(ip_port,li):
    proxies = {
        "http": "http://" + ip_port,
        "https": "http://" + ip_port,
    }
    try:
        res = requests.get('https://www.baidu.com/',
                           headers=getheaders(),
                           proxies=proxies,
                           timeout=2)
        print(ip_port, '能用')

        li.append(ip_port) # 返回有效ip列表
    except Exception as e:
        print(ip_port, '不能用')


# 从txt文件中读取数据处理
def checkip_from_txt(
        originfile,handlefile,li=[]):  # filepath文件中数据格式必须是："ip：port" 如 112.87.79.123:9999
    ips_ports_list = []
    # ips.txt: 从西刺爬取的IP
    with open(originfile) as f:
        for line in f:
            ips_ports_list.append(line.strip())
    thread_list = []
    for ip_port in ips_ports_list:
        t = threading.Thread(target=is_enable, args=(ip_port, li,))
        t.start()
        thread_list.append(t)
    for t in thread_list:
        t.join()
    print('*'*30+'有效数据筛选完成'+'*'*30)
    print(li)
    with open(handlefile,'w') as f:
        for ip in li:
            f.write(ip+'\n')
    print('*'*30+'有用ip文件写入完成'+'*'*30)
    


# 从mysql数据库中读取数据处理
def checkip_from_sql(host='localhost',
                     user='root',
                     password='123wangchao',
                     database='proxy_pool',li=[]):
    dbconn = pymysql.connect(host,  user, password, database)
    sql = """SELECT ip,port FROM proxy_ip;"""
    all_ip = pd.read_sql(sql, dbconn)
    thread_list = []
    for index, row in all_ip.iterrows():
        ip = row['ip']
        port = row['port']
        ip_port = ip + ':' + port
        t = threading.Thread(target=is_enable, args=(ip_port,li, ))
        t.start()
        thread_list.append(t)
    for t in thread_list:
        t.join()
    print('*'*30+'有效数据筛选完成'+'*'*30)
    print(li)
    cursor=dbconn.cursor()
    insert_sql1 = ''' truncate table proxy_ip_useful '''
    cursor.execute(insert_sql1)
    dbconn.commit()
    for ip in li:
        insert_sql2 = '''
                insert into proxy_ip_useful(ip,port)
                values('{0}','{1}')'''.format(ip.split(':')[0], ip.split(':')[1])
        cursor.execute(insert_sql2)
        dbconn.commit()
    print('*'*30+'数据库表更新完成'+'*'*30)


if __name__ == '__main__':
    originfile = 'origin_ip.txt'
    handlefile = 'useful_ip.txt'
    useful_ip=checkip_from_txt(originfile,handlefile)
    # checkip_from_sql()
