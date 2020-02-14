import requests
import random
import json

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
获取单个代理ip方法
参见网上开源项目：https://github.com/jiangxianli/ProxyIpLib#%E5%85%8D%E8%B4%B9%E4%BB%A3%E7%90%86ip%E5%BA%93
https://www.freeip.top/?page=1
"""
def get_proxyip(url='https://www.freeip.top/api/proxy_ip'):
    rep=requests.get(url, headers=getheaders())
    rep.encoding=rep.apparent_encoding
    html=rep.text
    data=json.loads(html)
    ip=data['data']['ip']
    port=data['data']['port']
    ip_port=ip+':'+port
    print('ip:port : ', ip_port)
    proxies = {
    "http": "http://" + ip_port,
    "https": "http://" + ip_port,
    }
    return proxies

if __name__ == "__main__":
    result=get_proxyip()