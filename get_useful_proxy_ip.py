import requests
import time
import threading
from queue import Queue
import random
import pandas as pd
from scrapy import Selector
import pymysql
import telnetlib # 测试方法2
from tqdm import tqdm


"""
函数默认参数配置
path_list:文件路径列表
sql_config：数据库配置参数
tablename：数据库存储数据表名称
"""

# path_list=['origin_ip.txt','useful_ip.txt','proxy_ip','proxy_ip_useful'] # 文件路径及数据库表名称
# sql_config={"host":"localhost","user":"root","password":"123wangchao","db":"proxy_pool","charset":'utf8'} # 数据库配置
# # tablename=['proxy_ip','proxy_ip_useful'] # 存入数据库的表名称



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

"""
crawl_ips函数：采集西祠代理ip方法
参数methodflag代表后面存入数据的方式
methodflag=1采用存入数据库方式
methodflag=0采用写入txt文本方式
pgn:要爬取西祠代理ip的页面数量
"""
def crawl_ips(methodflag,pgn=1,orgfile='origin_ip.txt'): 
    headers = {"user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1"}
    for i in range(1, pgn+1): # 制定爬取的页数  这里只爬取西刺代理第1页
        response = requests.get("http://www.xicidaili.com/nn/{0}".format(i), headers=getheaders())
        selector = Selector(text=response.text)
        all_trs = selector.xpath('//table[@id="ip_list"]//tr[position()>1]')
        ip_list = []
        for tr in all_trs:
            speed = tr.xpath("./td[@class='country'][3]//@title").extract()[0].split('秒')[0]
            ip = tr.xpath("./td[2]/text()").extract()[0]
            port = tr.xpath("./td[3]/text()").extract()[0]
            type = tr.xpath("./td[6]/text()").extract()[0]     
            ip_list.append((ip, port, speed, type))      
        if methodflag==0:
            # 方式1：将ip及port写入txt文件,只读'w'方式
            with open(orgfile,'w',encoding='utf-8') as f:
                ip_list=tqdm(ip_list,desc='存入txt文件',leave=True) # 列表变为进度条
                for ip_info in ip_list:
                    f.writelines(ip_info[0]+':'+ip_info[1]+'\n')
        else:
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

#####################################以上为爬取西刺代理上免费的代理ip（未做有效性判断）###########################################

############################################以下为数据处理，得到有效代理ip######################################################

"""
is_enable函数用来判断获取的ip是否有效
ip_port字符串形势如 "112.87.79.123:9999"(ip:port)
"""
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
        print(ip_port, '有效ip')
        li.append(ip_port) # 返回有效ip列表
    except Exception as e:
        print(ip_port, '无效ip')


# 从txt文件中读取数据处理
def checkip_from_txt(originfile='origin_ip.txt',handlefile='useful_ip.txt',li=[]):  # filepath文件中数据格式必须是："ip：port" 如 112.87.79.123:9999
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


"""
选择处理数据的方法：
methodflag=0代表处理文本数据的方法，对应派去数据时存入文本
methodflag=1代表处理数据库数据方法，对应爬取数据时存入数据库
"""
def select_hand_func(methodflag):
    if methodflag==0:
        checkip_from_txt()
    else:
        checkip_from_sql()

"""
简单合并为集成爬取和处理ip的总主函数
methodflag：爬取及处理ip数据方式，具体取值及代表含义参见上面说明
"""
def get_useful_proxy_ip(methodflag):
    crawl_ips(methodflag) # 爬取西刺代理ip函数 methodflag=0 写入文本，1写入数据
    select_hand_func(methodflag) # 选择处理已爬取ip数据处理方法

if __name__ == '__main__':
    get_useful_proxy_ip(0)
