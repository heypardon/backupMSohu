#coding:utf-8

import sys
import urllib
import re
import os
import time
import urllib2
import cookielib
import random

'''
Created on 2016-3-16
@author: ph
function: 每60秒备份一次http://m.sohu.com这个页面，并按时间分隔保存在/tmp/backup目录下，如/tmp/backup/201603161120
        /tmp/backup/201603161120/这个目录的结构如下：
            index.html #html内容
            image/ #存放图片
            js/ #存放js
            css/ #存放css
        
''' 


#取HTML中Image的正则表达式
img_regex = re.compile('''<img src="([^"]+?)" .*?/>''')

#取HTML中js的正则表达式（先取配所有script元素，再从每个script元素中取出js的地址）
script_regex = re.compile('''<script[^>].*?>.*?</script>''')
js_regex = re.compile('''.+?src="(\S+)"''')

#取HTML中css的正则表达式
css_regex = re.compile('''<link .*?href="(.*?.css)".*?/>''')

def openurl(url):
    """
    打开网页
    """
    cookie_support= urllib2.HTTPCookieProcessor(cookielib.CookieJar())
    opener = urllib2.build_opener(cookie_support,urllib2.HTTPHandler)
    urllib2.install_opener(opener)
    user_agents = [
                'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
                'Opera/9.25 (Windows NT 5.1; U; en)',
                'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
                'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
                'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
                'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
                "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
                "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",

                ] 
   
    agent = random.choice(user_agents)
    opener.addheaders = [("User-agent",agent),("Accept","*/*"),('Referer','http://www.google.com')]
    try:
        res = opener.open(url)
    except Exception,e:
        raise Exception
    else:
        return res

#做一次备份
def backup(url, directory):
    
    content = openurl(url).read()    
    
    #三个list容器分别装入找到的image，js,css地址
    img_result = re.findall(img_regex,content)
    img_result = list(set(img_result))
        
    script_result = re.findall(script_regex,content)
    js_result = []
    for i in script_result:
        js_result.extend(re.findall(js_regex,i))
    js_result = list(set(js_result))
    
    css_result = re.findall(css_regex,content)
    css_result = list(set(css_result))    

    #格式化时间，同时也便于根据时间创建文件名
    title = time.strftime("%Y%m%d%H%M",time.localtime(time.time()))
        
    #创建类似/tmp/backup/201603161120的文件夹
    new_path = os.path.join(directory, title)
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    else:
        return
        
    #分别将html,js,css写入到相应文件中
    
    index_path = os.path.join(new_path,"index.html")
    if not os.path.exists(index_path):
        index_opener = open(index_path, 'w')
        index_opener.write(content)
        index_opener.close()
        
    images = os.path.join(new_path,'images')
    if not os.path.isdir(images):
        os.makedirs(images)
    for url_image in img_result:
        name_image = url_image[(url_image.rfind('/')+1):]
        image_path = os.path.join(images, name_image)
        conn = urllib.urlopen(url_image)
        image_opener = open(image_path, 'wb')
        image_opener.write(conn.read())
        image_opener.close()
            
    js = os.path.join(new_path,'js')
    if not os.path.isdir(js):
        os.makedirs(js)
    for url_js in js_result:
        name_js = url_js[(url_js.rfind('/')+1):]
        js_path = os.path.join(js, name_js)
        conn = urllib.urlopen(url_js)
        js_opener = open(js_path, 'w')
        js_opener.write(conn.read())
        js_opener.close()       
    
    css = os.path.join(new_path,'css')
    if not os.path.isdir(css):
        os.makedirs(css)
    for url_css in css_result:
        name_css = url_css[(url_css.rfind('/')+1):]
        css_path = os.path.join(css,name_css)
        conn = urllib.urlopen(url_css)
        css_opener = open(css_path, 'w')
        css_opener.write(conn.read())
        css_opener.close()       

#根据间隔时间，url和备份目录这三个参数执行backup()进行备份
def excuteBackup(interval = 60, url = "http://m.sohu.com", directory = "/tmp/backup"):
    if not os.path.exists(directory):
        os.makedirs(directory)   
    while 1:
        backup(url, directory)
        print time.strftime("%Y%m%d%H%M",time.localtime(time.time()))+"备份成功"
        time.sleep(interval)


if __name__ == '__main__':
    interval = 60
    url = "http://m.sohu.com"
    directory = "/tmp/backup"
    
    for i in range(len(sys.argv)):
        if sys.argv[i] == "-d":
            interval = int(sys.argv[i+1])
        if sys.argv[i] == "-u":
            url = sys.argv[i+1]
        if sys.argv[i] == "-o":
            directory = sys.argv[i+1]
        
    excuteBackup(interval, url, directory)
