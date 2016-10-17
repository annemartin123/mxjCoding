#-*-coding:utf-8-*-
import pymysql
#import time
#import os

databaseName='jd_commit'#'qfliu_db'

table_childTask='tiemoChildTask'
table_skuTask='jd_tiemo'#'skuTask'
table_sortTask='tiemoSortTask'

sql_childTask="page int(11), link varchar(255), status int(11), firstTime DateTime, lastTime DateTime, primary key(page)"
sql_skuTask = "sku varchar(255), title varchar(255), shopId varchar(255), shopName varchar(255),firstTime DateTime, lastTime DateTime, primary key(sku)"
sql_sortTask = "sku varchar(255), title varchar(255), shopId varchar(255), shopName varchar(255),sort int(11), number int(11), firstTime DateTime, lastTime DateTime,primary key(sku, sort)"

def database_init(database,tableName,field):
    conn = pymysql.connect(host='localhost', user='root', passwd='111111',db='mysql',charset='utf8',connect_timeout=5000)
    cur = conn.cursor()
    sqlStr="select count(*) from information_schema.TABLES WHERE TABLE_NAME='"+tableName+"';"
    cur.execute(sqlStr)
    existNum = int(cur.fetchall()[0][0])
    if existNum!=0:
        cur.execute("use "+database)
        cur.execute("desc "+ tableName)
  #      for ziduan, ziduanType,i,j,k,l in cur.fetchall():
 #           print (ziduan+"--"+ziduanType)
    else:
        cur.execute("use "+database)
        sqlStr="CREATE TABLE "+ tableName + "("+field+")ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        cur.execute(sqlStr)
        conn.commit()
    cur.close()
    conn.close()



if __name__=="__main__":
    database_init(databaseName,table_childTask,sql_childTask)
    database_init(databaseName,table_skuTask,sql_skuTask)
    database_init(databaseName,table_sortTask,sql_sortTask)
