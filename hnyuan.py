import time
import os
import concurrent.futures
import requests
import re
import base64
from datetime import datetime
import threading
from queue import Queue
from pypinyin import lazy_pinyin
from bs4 import BeautifulSoup
import random

# 爬取国内免费代理IP
def crawl_proxies(start_page, end_page):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    proxies = []

    for page in range(start_page, end_page + 1):
        url = f'http://www.kxdaili.com/dailiip/2/{page}.html'
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        # 解析代理IP列表
        for row in soup.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 2:
                try:
                    proxy = cols[0].text.strip() + ':' + cols[1].text.strip()
                    proxies.append(proxy)
                except Exception as e:
                    print(f"Error parsing proxy on page {page}: {e}")

    return proxies


def test_proxy_and_write(proxy, file_path):
    url = 'http://mpp.liveapi.mgtv.com/v1/epg/turnplay/getLivePlayUrlMPP?version=PCweb_1.0&platform=1&buss_id=2000001&channel_id='  # 测试网站
    proxies = {
        'http': 'http://' + proxy,
        'https': 'https://' + proxy
    }
    try:
        response = requests.get(url, proxies=proxies, timeout=10)  # 增加超时时间为10秒
        if response.status_code == 200:
            with open(file_path, 'a', encoding='utf-8') as file:  # 使用 'a' 模式追加写入
                file.write(proxy + '\n')
                return True
    except requests.exceptions.RequestException as e:
        print(f"Error testing proxy {proxy}: {e}")
    return False


# 随机选择代理IP
def get_random_proxy(proxy_pool):
    if proxy_pool:
        return random.choice(proxy_pool)
    else:
        return None


# 构建代理IP池
def build_proxy_pool(proxies, file_path):
    # 清空文件，准备写入新的代理IP
    open(file_path, 'w').close()
    proxy_pool = []
    for proxy in proxies:
        if test_proxy_and_write(proxy, file_path):
            proxy_pool.append(proxy)
    return proxy_pool


# 示例使用
if __name__ == '__main__':
    start_page = 8
    end_page = 10  # 最大页数为1-10
    proxies = crawl_proxies(start_page, end_page)
    file_path = 'proxy_ip.txt'  # 指定一个文件路径来存储可用代理
    proxy_pool = build_proxy_pool(proxies, file_path)  # 构建代理池时，同时写入文件

    # 打印所有有效的代理IP
    for proxy in proxy_pool:
        print(f"有效代理IP: {proxy}")

    if proxy_pool:
        print(f"本次扫描共获取到 {len(proxy_pool)} 个有效的代理IP.")
    if not proxy_pool:
        print("未获取到有效的代理IP.")
        exit()  # 如果没有有效的代理IP，则退出程序

# 从代理池中随机选择一个代理IP
random_proxy = get_random_proxy(proxy_pool)

file_path = 'mgtv.txt'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
}
if random_proxy:
    proxy = f'http://{random_proxy}'  # 正确引用有效的代理IP
else:
    proxy = None  # 如果没有有效的代理IP，则不设置代理
url = 'http://mpp.liveapi.mgtv.com/v1/epg/turnplay/getLivePlayUrlMPP?version=PCweb_1.0&platform=1&buss_id=2000001&channel_id='
channel_dic = {
    '湖南经视': ['280', 'hn01'],
    '湖南都市': ['346', 'hn02'],
    '湖南电视剧': ['484', 'hn03'],
    '湖南电影': ['221', 'hn04'],
    '湖南爱晚': ['261', 'hn05'],
    '湖南国际': ['229', 'hn06'],
    '湖南娱乐': ['344', 'hn07'],
    '快乐购': ['267', 'hn08'],
    '茶频道': ['578', 'hn09'],
    '金鹰纪实': ['316', 'hn10'],
    '金鹰卡通': ['287', 'hn11'],
    '快乐垂钓': ['218', 'hn12'],
    '先锋乒羽': ['329', 'hn13'],
    '长沙新闻': ['269', 'hn14'],
    '长沙政法': ['254', 'hn15'],
    '长沙女性': ['230', 'hn16'],
}

txt_lis = []

for channel in channel_dic:
    if proxy:
        response = requests.get(url=url + str(channel_dic[channel][0]), headers=headers, proxies={'http': proxy})
    else:
        response = requests.get(url=url + str(channel_dic[channel][0]), headers=headers)

    # 检查响应状态码
    if response.status_code == 200:
        # 检查响应体是否为空
        if response.text:
            json_data = response.json()
            txt_url = json_data['data']['url']
            txt_lis.append(f'{channel},{txt_url}\n')
        else:
            print(f"Warning: Empty response body for channel {channel}")
    else:
        print(f"Warning: Request failed for channel {channel} with status code {response.status_code}")

txt_string = ''.join(txt_lis)

with open(file_path, 'w', encoding='utf-8') as file:
    file.write('湖南芒果,#genre#\n')
    file.write(txt_string)
    print(txt_string)
print(f'湖南芒果频道列表已保存至{file_path}！')

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
urls = []
shengshi_names = ["长沙", "娄底", "衡阳", "常德", "贵港", "南宁", "广州", "深圳", "梅州"]
pinyin_names = ["".join(lazy_pinyin(name, errors=lambda x: x)) for name in shengshi_names]
print(f'本次查询{shengshi_names}的酒店频道。')

# 定义运营商的名称和对应的组织名称
operators = {
    "中国电信": "Chinanet",
    "中国联通": "CHINA UNICOM China169 Backbone",
    "中国移动": "China Mobile Communications Corporation"
}
for shengshi in pinyin_names:
    for operator_name, org_name in operators.items():
        url = 'https://fofa.info/result?qbase64='
        search_txt = f'"iptv/live/zh_cn.js" && country="CN" && city="{shengshi}" && org="{org_name}"'  # 构造查询市字符串
        # 将字符串编码为字节流
        bytes_string = search_txt.encode('utf-8')
        # 使用 base64 进行编码
        encoded_search_txt = base64.b64encode(bytes_string).decode('utf-8')
        url += encoded_search_txt
        print(f"正在扫描 {shengshi} {operator_name}地址: ")
        print(f"{url}")
        urls.append(url)


def modify_urls(url):
    modified_urls = []
    ip_start_index = url.find("//") + 2
    ip_end_index = url.find(":", ip_start_index)
    base_url = url[:ip_start_index]  # http:// or https://
    ip_address = url[ip_start_index:ip_end_index]
    port = url[ip_end_index:]
    ip_end = "/iptv/live/1000.json?key=txiptv"
    for i in range(1, 256):
        modified_ip = f"{ip_address[:-1]}{i}"
        modified_url = f"{base_url}{modified_ip}{port}{ip_end}"
        modified_urls.append(modified_url)

    return modified_urls


def is_url_accessible(url):
    try:
        response = requests.get(url, timeout=0.5)
        if response.status_code == 200:
            return url
    except requests.exceptions.RequestException:
        pass
    return None


results = []

for url in urls:
    response = requests.get(url, headers=headers, timeout=15)
    page_content = response.text
    # 查找所有符合指定格式的网址
    pattern = r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"  # 设置匹配的格式，如http://8.8.8.8:8888
    urls_all = re.findall(pattern, page_content)
    urls = set(urls_all)  # 去重得到唯一的URL列表
    x_urls = []
    for url in urls:  # 对urls进行处理，ip第四位修改为1，并去重
        url = url.strip()
        ip_start_index = url.find("//") + 2
        ip_end_index = url.find(":", ip_start_index)
        ip_dot_start = url.find(".") + 1
        ip_dot_second = url.find(".", ip_dot_start) + 1
        ip_dot_three = url.find(".", ip_dot_second) + 1
        base_url = url[:ip_start_index]  # http:// or https://
        ip_address = url[ip_start_index:ip_dot_three]
        port = url[ip_end_index:]
        ip_end = "1"
        modified_ip = f"{ip_address}{ip_end}"
        x_url = f"{base_url}{modified_ip}{port}"
        x_urls.append(x_url)
    urls = set(x_urls)  # 去重得到唯一的URL列表

    valid_urls = []
    # 多线程获取可用url
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = []
        for url in urls:
            url = url.strip()
            modified_urls = modify_urls(url)
            for modified_url in modified_urls:
                futures.append(executor.submit(is_url_accessible, modified_url))

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                valid_urls.append(result)

    for url in valid_urls:
        print(url)

    # 遍历网址列表，获取JSON文件并解析
    for url in valid_urls:
        try:
            # 发送GET请求获取JSON文件，设置超时时间为0.5秒
            ip_start_index = url.find("//") + 2
            ip_end_index = url.find(":", ip_start_index)
            ip_port = url[ip_start_index:ip_end_index + 5]  # 这里获取ip地址和端口
            print(f"获取到有效的酒店源IP地址：{ip_port}")
            response = requests.get(url, timeout=0.5)
            json_data = response.json()

            try:
                # 解析JSON文件，获取name和url字段
                for item in json_data['data']:
                    if isinstance(item, dict):
                        name = item.get('name')
                        chid = str(item.get('chid')).zfill(4)  # 补全 chid 为四位数
                        srcid = item.get('srcid')
                        # 替换频道名称中的特定字符串
                        name = name.replace("中央", "CCTV")
                        name = name.replace("高清", "")
                        name = name.replace("搞清", "")
                        name = name.replace("HD", "")
                        name = name.replace("标清", "")
                        name = name.replace("超高", "")
                        name = name.replace("频道", "")
                        name = name.replace("-", "")
                        name = name.replace(" ", "")
                        name = name.replace("PLUS", "+")
                        name = name.replace("＋", "+")
                        name = name.replace("(", "")
                        name = name.replace(")", "")
                        name = name.replace("L", "")
                        name = name.replace("CMIPTV", "")
                        name = name.replace("cctv", "CCTV")
                        name = re.sub(r"CCTV(\d+)台", r"CCTV\1", name)
                        name = name.replace("CCTV1综合", "CCTV1")
                        name = name.replace("CCTV2财经", "CCTV2")
                        name = name.replace("CCTV3综艺", "CCTV3")
                        name = name.replace("CCTV4国际", "CCTV4")
                        name = name.replace("CCTV4中文国际", "CCTV4")
                        name = name.replace("CCTV4欧洲", "CCTV4")
                        name = name.replace("CCTV5体育", "CCTV5")
                        name = name.replace("CCTV5+体育", "CCTV5+")
                        name = name.replace("CCTV6电影", "CCTV6")
                        name = name.replace("CCTV7军事", "CCTV7")
                        name = name.replace("CCTV7军农", "CCTV7")
                        name = name.replace("CCTV7农业", "CCTV7")
                        name = name.replace("CCTV7国防军事", "CCTV7")
                        name = name.replace("CCTV8电视剧", "CCTV8")
                        name = name.replace("CCTV8纪录", "CCTV9")
                        name = name.replace("CCTV9记录", "CCTV9")
                        name = name.replace("CCTV9纪录", "CCTV9")
                        name = name.replace("CCTV10科教", "CCTV10")
                        name = name.replace("CCTV11戏曲", "CCTV11")
                        name = name.replace("CCTV12社会与法", "CCTV12")
                        name = name.replace("CCTV13新闻", "CCTV13")
                        name = name.replace("CCTV新闻", "CCTV13")
                        name = name.replace("CCTV14少儿", "CCTV14")
                        name = name.replace("央视14少儿", "CCTV14")
                        name = name.replace("CCTV少儿超", "CCTV14")
                        name = name.replace("CCTV15音乐", "CCTV15")
                        name = name.replace("CCTV音乐", "CCTV15")
                        name = name.replace("CCTV16奥林匹克", "CCTV16")
                        name = name.replace("CCTV17农业农村", "CCTV17")
                        name = name.replace("CCTV17军农", "CCTV17")
                        name = name.replace("CCTV17农业", "CCTV17")
                        name = name.replace("CCTV5+体育赛视", "CCTV5+")
                        name = name.replace("CCTV5+赛视", "CCTV5+")
                        name = name.replace("CCTV5+体育赛事", "CCTV5+")
                        name = name.replace("CCTV5+赛事", "CCTV5+")
                        name = name.replace("CCTV5+体育", "CCTV5+")
                        name = name.replace("CCTV5赛事", "CCTV5+")
                        name = name.replace("凤凰中文台", "凤凰中文")
                        name = name.replace("凤凰资讯台", "凤凰资讯")
                        name = name.replace("CCTV4K测试）", "CCTV4")
                        name = name.replace("CCTV164K", "CCTV16")
                        name = name.replace("上海东方卫视", "上海卫视")
                        name = name.replace("东方卫视", "上海卫视")
                        name = name.replace("内蒙卫视", "内蒙古卫视")
                        name = name.replace("福建东南卫视", "东南卫视")
                        name = name.replace("广东南方卫视", "南方卫视")
                        name = name.replace("金鹰卡通卫视", "金鹰卡通")
                        name = name.replace("湖南金鹰卡通", "金鹰卡通")
                        name = name.replace("炫动卡通", "哈哈炫动")
                        name = name.replace("卡酷卡通", "卡酷少儿")
                        name = name.replace("卡酷动画", "卡酷少儿")
                        name = name.replace("BRTVKAKU少儿", "卡酷少儿")
                        name = name.replace("优曼卡通", "优漫卡通")
                        name = name.replace("优曼卡通", "优漫卡通")
                        name = name.replace("嘉佳卡通", "佳嘉卡通")
                        name = name.replace("世界地理", "地理世界")
                        name = name.replace("CCTV世界地理", "地理世界")
                        name = name.replace("BTV北京卫视", "北京卫视")
                        name = name.replace("BTV冬奥纪实", "冬奥纪实")
                        name = name.replace("东奥纪实", "冬奥纪实")
                        name = name.replace("卫视台", "卫视")
                        name = name.replace("湖南电视台", "湖南卫视")
                        name = name.replace("少儿科教", "少儿")
                        name = name.replace("影视剧", "影视")

                        if name and chid and srcid:
                            # 格式化 URL
                            channel_url = ('{name},http://{ip_port}/tsfile/live/{chid}_{'
                                           'srcid}.m3u8?key=txiptv&playlive=1&authid=0').format(
                                name=name,
                                ip_port=ip_port,
                                chid=chid,
                                srcid=srcid
                            )
                            results.append(channel_url)

            except:
                continue
        except:
            continue

channels = []

for result in results:
    line = result.strip()
    if result:
        channel_name, channel_url = result.split(',')
        channels.append((channel_name, channel_url))

with open("iptv.txt", 'w', encoding='utf-8') as file:
    for result in results:
        file.write(result + "\n")
        print(result)

print(f"共获取到频道{len(channels)}个，频道列表文件iptv.txt生成完毕！")


import eventlet

eventlet.monkey_patch()

# 线程安全的队列，用于存储下载任务
task_queue = Queue()

# 线程安全的列表，用于存储结果
results = []
channels = []
error_channels = []

# 从iptv.txt文件提取cctv频道进行检测
with open("iptv.txt", 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line:
            channel_name, channel_url = line.split(',')
            if 'CCTV' in channel_name:
                channels.append((channel_name, channel_url))


# 定义工作线程函数
def worker():
    while True:
        # 从队列中获取一个任务
        channel_name, channel_url = task_queue.get()
        try:
            channel_url_t = channel_url.rstrip(channel_url.split('/')[-1])  # m3u8链接前缀
            lines = requests.get(channel_url).text.strip().split('\n')  # 获取m3u8文件内容
            ts_lists = [line.split('/')[-1] for line in lines if line.startswith('#') == False]  # 获取m3u8文件下视频流后缀
            ts_lists_0 = ts_lists[0].rstrip(ts_lists[0].split('.ts')[-1])  # m3u8链接前缀
            ts_url = channel_url_t + ts_lists[0]  # 拼接单个视频片段下载链接

            # 多获取的视频数据进行5秒钟限制
            with eventlet.Timeout(5, False):
                start_time = time.time()
                content = requests.get(ts_url).content
                end_time = time.time()
                response_time = (end_time - start_time) * 1

            if content:
                with open(ts_lists_0, 'ab') as f:
                    f.write(content)  # 写入文件
                file_size = len(content)
                # print(f"文件大小：{file_size} 字节")
                download_speed = file_size / response_time / 1024
                # print(f"下载速度：{download_speed:.3f} kB/s")
                normalized_speed = min(max(download_speed / 1024, 0.001), 100)  # 将速率从kB/s转换为MB/s并限制在1~100之间
                # print(f"标准化后的速率：{normalized_speed:.3f} MB/s")

                # 删除下载的文件
                os.remove(ts_lists_0)
                result = channel_name, channel_url, f"{normalized_speed:.3f} MB/s"
                results.append(result)
                numberx = (len(results) + len(error_channels)) / len(channels) * 100
                print(
                    f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")
        except:
            error_channel = channel_name, channel_url
            error_channels.append(error_channel)
            numberx = (len(results) + len(error_channels)) / len(channels) * 100
            print(
                f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")
        # 标记任务完成
        task_queue.task_done()


# 创建多个工作线程
num_threads = 10
for _ in range(num_threads):
    t = threading.Thread(target=worker, daemon=True)
    t.start()

# 添加下载任务到队列
for channel in channels:
    task_queue.put(channel)

# 等待所有任务完成
task_queue.join()


def channel_key(channel_name):
    match = re.search(r'\d+', channel_name)
    if match:
        return int(match.group())
    else:
        return float('inf')  # 返回一个无穷大的数字作为关键字


# 对频道进行排序
results.sort(key=lambda x: (x[0], -float(x[2].split()[0])))
results.sort(key=lambda x: channel_key(x[0]))

result_counter = 20  # 每个频道需要的个数

# 写入cctv.txt和.m3u文件
with open("cctv.txt", 'w', encoding='utf-8') as file:
    channel_counters = {}
    file.write('央视频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if 'CCTV' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1

# 线程安全的队列，用于存储下载任务
task_queue = Queue()

# 线程安全的列表，用于存储结果
results = []

channels = []
error_channels = []

with open("iptv.txt", 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line:
            channel_name, channel_url = line.split(',')
            if 'CCTV' not in channel_name:
                channels.append((channel_name, channel_url))

# 定义工作线程函数
def worker():
    while True:
        # 从队列中获取一个任务
        channel_name, channel_url = task_queue.get()
        try:
            channel_url_t = channel_url.rstrip(channel_url.split('/')[-1])  # m3u8链接前缀
            lines = requests.get(channel_url).text.strip().split('\n')  # 获取m3u8文件内容
            ts_lists = [line.split('/')[-1] for line in lines if line.startswith('#') == False]  # 获取m3u8文件下视频流后缀
            ts_lists_0 = ts_lists[0].rstrip(ts_lists[0].split('.ts')[-1])  # m3u8链接前缀
            ts_url = channel_url_t + ts_lists[0]  # 拼接单个视频片段下载链接

            # 多获取的视频数据进行5秒钟限制
            with eventlet.Timeout(5, False):
                start_time = time.time()
                content = requests.get(ts_url).content
                end_time = time.time()
                response_time = (end_time - start_time) * 1

            if content:
                with open(ts_lists_0, 'ab') as f:
                    f.write(content)  # 写入文件
                file_size = len(content)
                # print(f"文件大小：{file_size} 字节")
                download_speed = file_size / response_time / 1024
                # print(f"下载速度：{download_speed:.3f} kB/s")
                normalized_speed = min(max(download_speed / 1024, 0.001), 100)  # 将速率从kB/s转换为MB/s并限制在1~100之间
                # print(f"标准化后的速率：{normalized_speed:.3f} MB/s")

                # 删除下载的文件
                os.remove(ts_lists_0)
                result = channel_name, channel_url, f"{normalized_speed:.3f} MB/s"
                results.append(result)
                numberx = (len(results) + len(error_channels)) / len(channels) * 100
                print(
                    f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")
        except:
            error_channel = channel_name, channel_url
            error_channels.append(error_channel)
            numberx = (len(results) + len(error_channels)) / len(channels) * 100
            print(
                f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")

        # 标记任务完成
        task_queue.task_done()


# 创建多个工作线程
num_threads = 10
for _ in range(num_threads):
    t = threading.Thread(target=worker, daemon=True)
    # t = threading.Thread(target=worker, args=(event,len(channels)))  # 将工作线程设置为守护线程
    t.start()
    # event.set()

# 添加下载任务到队列
for channel in channels:
    task_queue.put(channel)

# 等待所有任务完成
task_queue.join()


def channel_key(channel_name):
    match = re.search(r'\d+', channel_name)
    if match:
        return int(match.group())
    else:
        return float('inf')  # 返回一个无穷大的数字作为关键字


# 对频道进行排序
results.sort(key=lambda x: (x[0], -float(x[2].split()[0])))
# results.sort(key=lambda x: channel_key(x[0]))
# now_today = datetime.date.today()

result_counter = 20  # 每个频道需要的个数

# 生成txt文件
with open("iptvlist.txt", 'w', encoding='utf-8') as file:
    channel_counters = {}
    file.write('卫视频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '卫视' in channel_name or '凤凰' in channel_name or '翡翠' in channel_name or 'CHC' in channel_name or '重温经典' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1

    channel_counters = {}
    file.write('省内频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '湖南' in channel_name or '长沙' in channel_name or '金鹰' in channel_name or '先锋乒羽' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1

    channel_counters = {}
    file.write('其他频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if 'CCTV' not in channel_name and '卫视' not in channel_name and '测试' not in channel_name and '凤凰' not in \
                channel_name and '翡翠' not in channel_name and 'CHC' not in channel_name and '重温经典' not in channel_nameand \
                and '湖南' not in channel_name and '长沙' not in channel_name and '金鹰' not in channel_name and '先锋乒羽' not in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1


# 合并自定义频道文件内容
file_contents = []
file_paths = ["YD-IPTV.txt", "cctv.txt", "iptvlist.txt", "mgtv.txt", "gangaotai.txt", "zdy.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()
        file_contents.append(content)

# 写入合并后的文件
with open("iptv_list.txt", "w", encoding="utf-8") as output:
    output.write('\n'.join(file_contents))

    # 写入更新日期时间
    now = datetime.now()
    output.write(f"更新时间,#genre#\n")
    output.write(f"{now.strftime("%Y-%m-%d")},url\n")
    output.write(f"{now.strftime("%H:%M:%S")},url\n")

os.remove("iptv.txt")
os.remove("cctv.txt")
os.remove("iptvlist.txt")
os.remove("mgtv.txt")
os.remove("gangaotai.txt")

print("任务运行完毕，分类频道列表可查看文件夹内iptv_list.txt文件！")
