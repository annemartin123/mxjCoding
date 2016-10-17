#-*-coding:utf-8-*-
import pymysql
import time
import os
from selenium import webdriver
from bs4 import BeautifulSoup

mainPage = "http://list.jd.com"

skuTaskStr = "sku, title, shopId, shopName, firstTime, lastTime, kind, website"

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

def data_insertSkuDatabase(databaseName,tableName,mySqlList):
    conn = pymysql.connect(host='localhost', user='root', passwd='111111',db='mysql',charset='utf8',connect_timeout=5000)
    cur = conn.cursor()
    temp=""
    i=1
    for mySqlStrList in mySqlList:
        temp+="'%s'"% mySqlStrList
        if i<len(mySqlList):
            temp+=","
        i+=1
   # print (temp)
    try:
        sqlStr="insert into %s.%s(%s) values(%s);" % (databaseName,tableName,skuTaskStr,temp)
 #       print (sqlStr)
        cur.execute(sqlStr)
        conn.commit()
    except pymysql.IntegrityError as e:
 #       print (e)
        timeStr=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime())
        sqlStr="update %s.%s set lastTime='%s' where sku=%s;" % (databaseName,tableName,timeStr,mySqlList[0])
 #       print (sqlStr)
        cur.execute(sqlStr)
        conn.commit()
    finally:
        cur.close()
        conn.close()

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
    print (totalPage)
    return totalPage

if __name__=="__main__":
    seedLink = 'https://list.jd.com/list.html?cat=9987,830,867'
    dabaseName= 'jd_commit'#'qfliu_db'
    tableName_sku = 'productSku'#'skuTask'
    
    if os.name =="posix":
        driver=webdriver.Chrome(executable_path='/Users/m/Desktop/gongju/chromedriver')
    elif os.name =="nt":
        driver=webdriver.Chrome(executable_path=r'D:\web_driver\chrome_2.0\chromedriver.exe')

    myLink = seedLink
    totalPageNum = get_totalPageNum(driver,seedLink)

    timeStr=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime())
    print (timeStr)
    page=1
    while(page<=int(totalPageNum)):

        fileList=[]
        fileList=scrapy_sku(driver, myLink)
 
 #   f=open('test.txt','w',encoding='utf8')
 #   iNum=1
 #   for myList in fileList:
 #       print (str(iNum))
 #       f.write(str(iNum))
 #       f.write('\n')
 #       iNum=iNum+1
 #       for i in myList:
 #           f.write(i)
 #           f.write('\n')
 #   f.close()

        for myList in fileList:
            timeStr=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime())
 #           print (timeStr)
            kindName = "tiemo"
            websiteName = "JingDong"
            myList.append(timeStr)
            myList.append(timeStr)
            myList.append(kindName)
            myList.append(websiteName)
            data_insertSkuDatabase(dabaseName, tableName_sku, myList)

        if page<int(totalPageNum):
            myLink = get_nextPage(driver,myLink)
            #print (myLink)
        print (float(page)/(float(int(totalPageNum))))
        print ('\n')
        page+=1

    timeStr=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime())
    print (timeStr)
