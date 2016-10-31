#-*-coding:utf-8-*-
import pymysql
import time
import os
from selenium import webdriver
from bs4 import BeautifulSoup
import json
import httplib2
import urllib.request

mainPage = "http://list.jd.com"#used to joined in link

allKindId=["9987,830,867","9987,830,866","9987,830,13661","9987,830,13658","670,671,5146"]#"tiemo""shoujike""shujuxian""yidongdianyuan""pingbanpeijian"
website="https://www.jd.com/"# save to database

def getProxy():
    jsonListP=[]
    cmd = 1 #get proxy
    tempdata =''
    jsonListP.append(cmd)
    jsonListP.append(tempdata)
    json_str = json.dumps(jsonListP)
    print (json_str)
    connect = httplib2.Http()
    myPIp = []
    while True:
        resp, content = connect.request('http://118.187.53.58/spider_server/debug/jd_classify_sku_test.php','post',body=json_str)
        if content!=b'':
            temp = str(content, encoding='utf-8')
            myPIp = json.loads(temp)
 #           print (myPIp)
            break

    myProxy={}
    for myIp in myPIp:
        temp=myIp['ip']+ ":"+myIp['port']
        myProxy[myIp['http_type']]= temp
 #       print (myProxy)
        return myIp
    return myPIp

def scrapy_sku(driver,page):
    sqlList=[]
    
    driver.get(page)
    time.sleep(1)
    driver.refresh()
    driver.implicitly_wait(6)
    driver.maximize_window()
    
    html = BeautifulSoup(driver.page_source, "html.parser")
    goods = driver.find_elements_by_css_selector('.gl-item')
    for j, good in enumerate(goods):
        html = BeautifulSoup(good.get_attribute('innerHTML'), "html.parser")
 
        real_sku=[]
        child_sku = html.find_all('img')
        for i in child_sku:
            my_sku = i.get('data-sku')
            if my_sku!=None:
                real_sku.append(my_sku)

        real_title=[]
        child_title=html.find_all('a')
        for i in child_title:
            my_title = i.get('title')
            if (my_title != None) and (len(real_title)<len(real_sku)):
                real_title.append(my_title)

        real_shopId=[]
        child_div = html.find_all('div')
        for i in child_div:
            my_shopId = i.get('jdzy_shop_id')
            if my_shopId!=None:
                real_shopId.append(my_shopId)
        if len(real_shopId)==1:
            shopId = real_shopId[0]

        real_shopName=[]
        child_div = html.find_all('div')
        for i in child_div:
            my_shopName = i.get('data-shop_name')
            if my_shopName!=None:
                real_shopName.append(my_shopName)
        if len(real_shopName)==1:
            shopName = real_shopName[0]

        for index in range(len(real_sku)):
            my_sqlList=[]
            my_sqlList.append(real_sku[index])
            my_sqlList.append(real_title[index])
            my_sqlList.append(shopId)
            my_sqlList.append(shopName)
            sqlList.append(my_sqlList)
    return sqlList

def save_Sku(skuList):
    jsonList=[]
    cmd = 0 #give sku
    jsonList.append(cmd)
    jsonList.append(skuList)
    json_str = json.dumps(jsonList)
    f=open('test.txt','w',encoding='utf8')
    f.write(json_str)
    f.close()
    
    connect = httplib2.Http()
    resp, content = connect.request('http://118.187.53.58/spider_server/debug/jd_classify_sku_test.php','post',body=json_str)
    print (resp)
    print (content)

def get_nextPage(driver,link):
    driver.get(link)
    html = BeautifulSoup(driver.page_source, "html.parser")
    page = mainPage + html.find(attrs={'class',"pn-next"})["href"]
 #   print (page)
    return page

def get_totalPageNum(driver,link):
    driver.get(link)
    html = BeautifulSoup(driver.page_source, "html.parser")
    page = html.find(attrs={'class',"fp-text"})
    totalPage = page.i.string
    return totalPage

def getDriver_byProxy(proxy):
    ip_portStr = proxy['ip']+":"+proxy['port']

    mservice_args=[
        '--ignore-ssl-errors=true',
        '--ssl-protocol=any',
        '--proxy=%s' % (ip_portStr),
        '--proxy-type=%s' % (proxy['http_type']),
        ]
    print (mservice_args)

    if os.name == "posix":
        chromedriverPath='/Users/m/Desktop/gongju/chromedriver'
        os.environ["webdriver.chrome.driver"]=chromedriverPath
    elif os.name == "nt":
        chromedriverPath = r'D:\web_driver\chrome_2.0\chromedriver.exe'
        
    driver=webdriver.Chrome(executable_path=chromedriverPath, service_args=mservice_args)
    return driver

def back_Proxy(myIp):
    jsonListP=[]
    cmd = 2#used proxy
    tempdata =[]
    tempdata.append(myIp)
    jsonListP.append(cmd)
    jsonListP.append(tempdata)
    json_str = json.dumps(jsonListP)
    print (json_str)
    connect = httplib2.Http()
    resp, content = connect.request('http://118.187.53.58/spider_server/debug/jd_classify_sku_test.php','post',body=json_str)
    print (resp)
    print (content)

def generate_oneKindSku(kindId):
    seedLink = 'https://list.jd.com/list.html?cat='+kindId
    print (seedLink)
    skuListClient=[]
    myProxy = getProxy()
    print (myProxy)

    driver = getDriver_byProxy(myProxy)
    myLink = seedLink
    totalPageNum = get_totalPageNum(driver,myLink)
    print (totalPageNum)

    timeStr=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime())
    print (timeStr)
    page=1
    while(page<=int(totalPageNum)):

        fileList=[]
        fileList=scrapy_sku(driver, myLink)
        print (len(fileList))
         
        mykindId = kindId
        for myList in fileList:
            myDict = {}
            myDict['sku']=myList[0]
            myDict['title']=myList[1]
            myDict['shopId']=myList[2]
            myDict['shopName']=myList[3]
            myDict['kind'] = mykindId
            myDict['website'] = website
            timeStr=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime())
            myDict['firstTime']=timeStr
            myDict['lastTime'] = timeStr
            skuListClient.append(myDict)
        save_Sku(skuListClient)
        
        if page<int(totalPageNum):
            myLink = get_nextPage(driver,myLink)
            print (myLink)
            back_Proxy(myProxy)
            driver.quit()
            myProxy = getProxy()
            print (myProxy)
            driver = getDriver_byProxy(myProxy)
        elif page == int(totalPageNum):
            back_Proxy(myProxy)
            driver.quit()
            
        print ("efficiency:%.3f" % (float(page)/float(totalPageNum)))
        print (str(page)+"/"+str(totalPageNum))
        page+=1

    timeStr=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime())
    print (timeStr)

if __name__=="__main__":
    for key in allKindId:
        generate_oneKindSku(key)
