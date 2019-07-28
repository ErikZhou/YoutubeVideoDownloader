import os
import time

import requests
import re
from tqdm import tqdm

import urllib3
from PIL import Image
from lxml import etree
from selenium import webdriver

from YoutubeVideoDownloader.util.YDMHTTPDemo3 import YDMHttp

abspath = os.getcwd()
# 警用requests中的警告
urllib3.disable_warnings()

# 下载文件
def downloadFile(url,path, name):
    resp = requests.get(url=url,stream=True, verify=False)
	#stream=True的作用是仅让响应头被下载，连接保持打开状态，
    content_size = int(resp.headers['Content-Length'])/1024		#确定整个安装包的大小
    with open(path + '/' + name, "wb") as f:
        print("整个文件大小是是：",content_size / 1024,'M')
        for data in tqdm(iterable=resp.iter_content(1024),total=content_size,unit='k',desc=name):
	#调用iter_content，一块一块的遍历要下载的内容，搭配stream=True，此时才开始真正的下载
	#iterable：可迭代的进度条 total：总的迭代次数 desc：进度条的前缀
            f.write(data)

#g_tk算法
def get_g_tk(p_skey):
    hashes = 5381
    for letter in p_skey:
        hashes += (hashes << 5) + ord(letter)  # ord()是用来返回字符的ascii码
    return (str)(hashes & 0x7fffffff)

# 创建文件夹
def mkdir(path):
    # 引入模块
    import os
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)
        print(path + ' 创建成功')
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print(path + ' 目录已存在')
    return True

# 滑动到页面最低端
def scrollToBottom(driver, frame_name):
    driver.switch_to.frame(frame_name)
    source1 = driver.page_source
    driver.switch_to.parent_frame()
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)");
    time.sleep(4)
    driver.switch_to.frame(frame_name)
    source2 = driver.page_source
    while source1 != source2:
        source1 = source2
        driver.switch_to.parent_frame()
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)");
        time.sleep(4)
        driver.switch_to.frame(frame_name)
        source2 = driver.page_source

# 判断数据是否爬取
def check_spider_history(type, url):
    if os.path.exists(abspath + '/documentations/history/' + type + '.txt') == False:
        return False
    histories = get_spider_history(type)
    if url + '\n' in histories:
        print(type + ' -> ' + url + ' 已爬取')
        return True
    else:
        print(type + ' -> ' + url + ' 未爬取')
        return False
    return url in histories

# 读取数据爬取的历史
def get_spider_history(type):
    with open(abspath + '/documentations/history/' + type + '.txt', 'r') as f:
        list = []
        while True:
            line = f.readline()  # 整行读取数据
            if not line:
                break
            list.append(line)
    return list

# 写入数据爬取的历史
def write_spider_history(type, url):
    with open(abspath + '/documentations/history/' + type + '.txt', 'a') as f:
        f.write(url)
        f.write('\n')
        print(type + ' -> ' + url + ' 写入成功')
    f.close()

# 更新视频解析网站的哈希值
def update_parsevideo_hash():
    html = get_one_page('https://pocket.mynatapp.cc')
    pattern = '[\s\S]*?var hash = "([\s\S]*?)"[\s\S]*?'
    old_hash = ''
    for tmp_hash in parse_one_page(html, pattern):
        old_hash = tmp_hash
    html = get_one_page('https://www.parsevideo.com/')
    pattern = '[\s\S]*?var hash = "([\s\S]*?)"[\s\S]*?'
    new_hash = ''
    for tmp_hash in parse_one_page(html, pattern):
        new_hash = tmp_hash
    html = get_one_page('https://pocket.mynatapp.cc')
    html = html.replace('var hash = "' + old_hash + '";', 'var hash = "' + new_hash + '";')
    with open('../../../Web/PocketFilm/views/index.html', 'w') as f:
        f.write(html)

# 解决视频解析时的验证码问题
def solve_parsevideo_captche(url='https://pocket.mynatapp.cc/#https://v.youku.com/v_show/id_XMzc5OTM0OTAyMA==.html'):
    driver = get_driver(1)
    driver.maximize_window()
    driver.get(url)
    html = driver.page_source
    if 'style="margin-bottom: 15px;display: none"' in html:
        driver.find_element_by_id('url_submit_button').click()
        time.sleep(2)
        element = driver.find_element_by_id('captcha_img')
        capture(driver, element)
        code = captcha()
        driver.find_element_by_id('captcha_code').send_keys(code)
        driver.find_element_by_id('captcha_sbumit').click()
        time.sleep(2)
        driver.refresh()
    else:
        print('当前不用输入验证码')
    driver.quit()

# 裁剪指定元素
def capture(driver, element, image_path=abspath + '/image', image_name='captcha'):
    """
    截图,指定元素图片
    :param element: 元素对象
    :return: 无
    """
    """图片路径"""
    timestrmap = time.strftime('%Y%m%d_%H.%M.%S')
    imgPath = os.path.join(image_path, '%s.png' % image_name)

    """截图，获取元素坐标"""
    driver.save_screenshot(imgPath)
    left = element.location['x'] + 66
    top = element.location['y'] + 417
    elementWidth = left + element.size['width'] + 60
    elementHeight = top + element.size['height'] + 20

    picture = Image.open(imgPath)
    picture = picture.crop((left, top, elementWidth, elementHeight))
    timestrmap = time.strftime('%Y%m%d_%H.%M.%S')
    imgPath = os.path.join(image_path, '%s.png' % image_name)
    picture.save(imgPath)
    print('元素图标保存位置 -> ' + image_path + '/' + image_name)

# 识别验证码
def captcha(image_path=abspath + '/image/captcha.png'):
    # 用户名
    username = 'Grayson_WP'
    # 密码
    password = 'weipeng185261'
    # 软件ＩＤ，开发者分成必要参数。登录开发者后台【我的软件】获得！
    appid = 7961
    # 软件密钥，开发者分成必要参数。登录开发者后台【我的软件】获得！
    appkey = 'f8c23d784f261f08f028ada4c07fa36b'
    # 图片文件
    filename = image_path
    # 验证码类型，# 例：1004表示4位字母数字，不同类型收费不同。请准确填写，否则影响识别率。在此查询所有类型 http://www.yundama.com/price.html
    codetype = 1004
    # 超时时间，秒
    timeout = 60
    # 检查
    if (username == 'username'):
        return None
        print('请设置好相关参数再测试')
    else:
        # 初始化
        yundama = YDMHttp(username, password, appid, appkey)
        # 登陆云打码
        uid = yundama.login();
        print('uid: %s' % uid)
        # 查询余额
        balance = yundama.balance();
        print('balance: %s' % balance)
        # 开始识别，图片路径，验证码类型ID，超时时间（秒），识别结果
        cid, result = yundama.decode(filename, codetype, timeout);
        print('cid: %s, result: %s' % (cid, result))
        return result

# 获取一个页面的源代码
def get_one_page(url, encode='utf-8'):
    if encode == None:
        encode = 'utf-8'
    response = get_response(url)
    response.encoding = encode
    if response.status_code == 200:
        return response.text
    return None

# 根据 url 获取响应数据
def get_response(url):
    ua_header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    }
    return requests.get(url, headers=ua_header,verify=False)

# 解析一个页面的信息
def parse_one_page(html, pattern):
    pattern = re.compile(pattern)
    try:
        items = re.findall(pattern, html)
        for item in items:
            yield item
    except:
        yield ()

# 通过xpath解析一个页面的信息
def parse_one_page_with_xpath(html, xpath_pattern):
    return etree.HTML(html)

# 获取视频解析后的地址
def get_movie_parse_url(url):
    driver = get_driver()
    driver.get(url)
    data = driver.execute_script('return parent.now')
    return data

# 获取 web 驱动
def get_driver(type=0):
    # PhantomJS
    if type == 0:
        driver = webdriver.PhantomJS(
            executable_path=abspath + '/phantomjs/bin/phantomjs')
            # executable_path='/usr/local/software/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
    # Chrome
    if type == 1:
        # 加启动配置
        options = webdriver.ChromeOptions()
        # 隐藏Chrome浏览器
        # options.add_argument('--headless')
        # 禁用GPU
        # options.add_argument('--disable-gpu')
        # 开启实验性功能参数
        # options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option("prefs", {
            "download.default_directory": "/Users/weipeng/Personal/Projects/YoutubeVideoDownloader/YoutubeVideoDownloader/",
            "download.prompt_for_download": True,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        # 打开Chrome浏览器
        driver = webdriver.Chrome(abspath + '/webdriver/chromedriver/chromedriver', chrome_options=options)
    # 设置超时时间
    # driver.set_page_load_timeout(60)
    # driver.set_script_timeout(60)
    return driver

# 获取数组中的第一个元素
def get_first_item(arr):
    count = 0
    for item in arr:
        if count == 0:
            return item
        count += 1