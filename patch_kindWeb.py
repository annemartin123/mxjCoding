#-*-coding:utf-8-*-
#coding-gbk
import pymysql
import time

databaseName = 'jd_commit'#'qfliu_db'

table_childTask='childTask'
table_skuTask='productSku'#'skuTask'
table_sortTask='sortTask'

sql_childTask="page int(11), link varchar(255), status int(11),  firstTime DateTime, lastTime DateTime, kind varchar(255), website varchar(255),primary key(page)"
sql_skuTask = "sku varchar(255), title varchar(255), shopId varchar(255), shopName varchar(255),  firstTime DateTime, lastTime DateTime, kind varchar(255), website varchar(255),primary key(sku)"
sql_sortTask = "sku varchar(255), title varchar(255), shopId varchar(255), shopName varchar(255),  sort int(11), number int(11), firstTime DateTime, lastTime DateTime,kind varchar(255), website varchar(255),primary key(sku, sort)"

patch_Task = "kind varchar(255) website varchar(255)"

def patch(databaseName,tableName, fieldName, fieldType, kindName):
    conn = pymysql.connect(host='localhost', user='root', passwd='111111',db='mysql',charset='utf8',connect_timeout=5000)
    cur = conn.cursor()
    sqlStr = "ALTER TABLE "+ databaseName+"." +tableName +" ADD "+fieldName + " "+fieldType+";"
    print (sqlStr)
    cur.execute(sqlStr)
    conn.commit()

    fieldNameValue = kindName
    try:
        sqlStr = "SET SQL_SAFE_UPDATES=0;update "+ databaseName+"."+tableName+" set "+fieldName +"='"+fieldNameValue+"';SET SQL_SAFE_UPDATES=1;"
        print (sqlStr)
        cur.execute(sqlStr)
        conn.commit()
    except Exception as e:
        print (e)
        sqlStr0="show full processlist;"
        sqlStr1="select * from information_schema.INNODB_TRX\G;"
        sqlStr2="select @@autocommit;"
        myInfoList = cur.execute(sqlStr2)
        myCommit = cur.execute(sqlStr1)
        print (myInfoList)
        print (myCommit)
    finally:
        cur.close()
        conn.close()

def database_patchKindWeb(database,tableName,fields, field):
    conn = pymysql.connect(host='localhost', user='root', passwd='111111',db='mysql',charset='utf8',connect_timeout=5000)
    cur = conn.cursor()
    sqlStr="select count(*) from information_schema.TABLES WHERE TABLE_NAME='"+tableName+"';"
    cur.execute(sqlStr)
    existNum = int(cur.fetchall()[0][0])
    kindExistOk = False
    webExistOk = False
    if existNum!=0:
        cur.execute("use "+database)
        cur.execute("desc "+ tableName)
        myStrList = field.split(' ')
        for ziduan, ziduanType,i,j,k,l in cur.fetchall():
            print (ziduan+"--"+ziduanType)
            if (ziduan == myStrList[0]):
               kindExistOk = True
            if (ziduan == myStrList[2]):
                webExistOk = True
        if kindExistOk == False:
            patch(database,tableName, myStrList[0],myStrList[1],"tiemo")
        if webExistOk == False:
            patch(database,tableName, myStrList[2],myStrList[3],"JingDong")
    else:
        cur.execute("use "+database)
        sqlStr="CREATE TABLE "+ tableName + "("+fields+")ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        cur.execute(sqlStr)
        conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    database_patchKindWeb(databaseName, table_childTask,sql_childTask, patch_Task)
    database_patchKindWeb(databaseName, table_sortTask,sql_sortTask, patch_Task)
    database_patchKindWeb(databaseName, table_skuTask, sql_skuTask, patch_Task)

