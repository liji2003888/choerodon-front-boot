#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymysql
import os
import yaml
import traceback
import sys
import getopt
reload(sys)
sys.setdefaultencoding('utf8')
# return menu id
def returnTableId(table, content, equaldata):
    sql = "select id from {table} where {content} = '{equaldata}'".format(table=table,content=content, equaldata=equaldata)
    cursor.execute(sql)
    Id = cursor.fetchone()
    return Id
# judge menu exist
def judgeTrue(table, *args):
    if len(args) == 4:
      sql = "select id from {table} where {content}='{equaldata}' and {contentTwo}='{equaldataTwo}'".format(
        table=table,
        content=args[0],
        equaldata=args[1],
        contentTwo=args[2],
        equaldataTwo=args[3])
    else:
      sql = "select id from {table} where {content}='{equaldata}'".format(
        table=table,
        content=args[0],
        equaldata=args[1])
    cursor.execute(sql)
    count = cursor.execute(sql)
    # print count
    if count == 0:
        return True
    else:
        return False
# return menu level
def returnLevel(data):
    dataMenu = data["menu"]
    centerLevel = []
    for service in dataMenu.keys():
        for level in levelArray:
            for saveLevel in dataMenu[service].keys():
                if saveLevel == level:
                    centerLevel.append(saveLevel)
    return centerLevel
# insert iam_menu
def insertMenuTable(table, data):
    try:
        dataMenu = data["menu"]
        dataLanguageChinese = data["language"]["Chinese"]
        for root in dataMenu:
                centerLevel = []
                for level in levelArray:
                  for service in dataMenu[root]:
                      if service == level:
                          centerLevel.append(service)
                for levelYaml in centerLevel:
                  if judgeTrue(table, 'code', root, 'level', levelYaml):
                      sql = "insert into {table} (code, name, level, parent_id, type, is_default, icon, sort) values ('{code}', '{name}', '{level}', 0, 'root', 1, '{icon}', '{sort}')".format(
                          table=table,
                          code=root,
                          name=dataLanguageChinese[root],
                          level=levelYaml,
                          icon=dataMenu[root]["icon"],
                          sort=dataMenu[root]["sort"])
                      cursor.execute(sql)
                  else:
                      sql = "update {table} set code='{code}', name='{name}', level='{level}', icon='{icon}'"
                      if attrs and ('sort' in attrs):
                          sql = sql + ", sort='{sort}'";
                      sql = (sql + " where code='{code}' and level='{level}'").format(
                            table=table,
                            code=root,
                            name=dataLanguageChinese[root],
                            level=levelYaml,
                            icon=dataMenu[root]["icon"],
                            sort=dataMenu[root]["sort"])
                      cursor.execute(sql)
        for service in dataMenu:
            centerLevel = []
            for level in levelArray:
                for saveLevel in dataMenu[service].keys():
                    if saveLevel == level:
                        centerLevel.append(saveLevel)
            for level in centerLevel:
                for menuList in dataMenu[service][level]:
                    sql = "select id from iam_menu where code='{service}' and level='{level}'".format(
                    service=service,
                    level=level)
                    count = cursor.execute(sql)
                    serviceId = cursor.fetchone()
                    if dataMenu[service][level][menuList]:
                        if judgeTrue(table, 'code', menuList):
                            if serviceId and ('id' in serviceId):
                                sql = "insert into {table} (code, name, level, parent_id, type, is_default, icon, route, sort) values ('{code}', '{name}', '{level}', '{parent_id}', 'menu', 1, '{icon}', '{route}', '{sort}')".format(
                                    table=table,
                                    code=menuList,
                                    name=dataLanguageChinese[menuList],
                                    level=level,
                                    parent_id=serviceId["id"],
                                    icon=dataMenu[service][level][menuList]["icon"],
                                    route=dataMenu[service][level][menuList]["Routes"],
                                    sort=dataMenu[service][level][menuList]["sort"])
                                cursor.execute(sql)
                        else:
                            if serviceId and ('id' in serviceId):
                                sql = "update {table} set code='{code}', name='{name}', level='{level}', icon='{icon}', route='{route}'"
                                if attrs and ('sort' in attrs):
                                    sql = sql + ", sort='{sort}'";
                                if attrs and ('parent_id' in attrs):
                                    sql = sql + ", parent_id='{parent_id}'";
                                sql = (sql + " where code='{code}' and level='{level}'").format(
                                    table=table,
                                    code=menuList,
                                    name=dataLanguageChinese[menuList],
                                    level=level,
                                    parent_id=serviceId["id"],
                                    icon=dataMenu[service][level][menuList]["icon"],
                                    route=dataMenu[service][level][menuList]["Routes"],
                                    sort=dataMenu[service][level][menuList]["sort"])
                                cursor.execute(sql)
    except:
        dealFault()
# insert iam_menu_permission
def insertMenuPermission(table, data):
    try:
        dataMenu = data["menu"]
        dataLanguageChinese = data["language"]["Chinese"]
        for service in dataMenu.keys():
            centerLevel = []
            for level in levelArray:
                for saveLevel in dataMenu[service].keys():
                    if saveLevel == level:
                        centerLevel.append(saveLevel)
            for level in centerLevel:
                for menuList in dataMenu[service][level].keys():
                    menuId = returnTableId('iam_menu', 'code', menuList)
                    sql = "delete from {table} where menu_id={menuId}".format(table=table,menuId=menuId["id"])
                    cursor.execute(sql)
                    for permission in dataMenu[service][level][menuList]["permission"]:
                        # permissionId = returnTableId('iam_permission', 'code', permission)
                        if menuId:
                            sql = "select id from iam_menu_permission where menu_id={menuId} and permission_code='{permission_code}'".format(menuId=menuId["id"],permission_code=permission)
                            cursor.execute(sql)
                            count = cursor.execute(sql)
                            if count == 0:
                                sql = "insert into {table} (menu_id, permission_code) values ('{menuId}','{permission_code}')".format(table=table,menuId=menuId["id"],permission_code=permission)
                                cursor.execute(sql)
    except:
        dealFault()
# insert iam_menu_tl
def insertMenuTlTable(table, data):
    try:
        dataService = data["menu"]
        for service in dataService.keys():
            centerLevel = []
            for level in levelArray:
                for saveLevel in dataService[service].keys():
                    if saveLevel == level:
                        centerLevel.append(saveLevel)
            for level in centerLevel:
                for menuList in dataService[service][level].keys():
                    dataLanguageEnglish = data["language"]["English"]
                    dataLanguageChinese = data["language"]["Chinese"]
                    menuId = returnTableId('iam_menu', 'code',  menuList)
                    if menuId:
                        sql = "select id from {table} where id={menuId}".format(table=table,menuId=menuId["id"])
                        cursor.execute(sql)
                        count = cursor.execute(sql)
                        if count == 0:
                            sql = "insert into {table} (lang,id,name) values ('en_US','{id}','{Name}')".format(table=table,id=menuId["id"], Name=dataLanguageEnglish[menuList])
                            cursor.execute(sql)
                            sql = "insert into {table} (lang,id,name) values ('zh_CN','{id}','{Name}')".format(table=table,id=menuId["id"], Name=dataLanguageChinese[menuList])
                            cursor.execute(sql)
                        else:
                            sql = "update {table} set lang='en_US',id='{id}',name='{Name}' where id={id} and lang='en_US'".format(
                                    table=table,id=menuId["id"], Name=dataLanguageEnglish[menuList])
                            cursor.execute(sql)
                            sql = "update {table} set lang='zh_CN',id='{id}',name='{Name}' where id={id} and lang='zh_CN'".format(
                                    table=table,id=menuId["id"], Name=dataLanguageChinese[menuList])
                            cursor.execute(sql)
    except:
        dealFault()
def dealFault():
    traceback.print_exc()
    db.rollback()
def close():
    cursor.close()
    db.close()
if __name__ == '__main__':
    levelArray = ["site", "organization", "project", "user"]
    baseDirs = os.path.abspath(os.path.join(os.path.dirname("__file__")))
    wholeConfig = '{baseDirs}/config.yml'.format(baseDirs=baseDirs);
    ymlFile = open(wholeConfig)
    contentConfig = yaml.load(ymlFile)
    host=os.environ.get('DB_HOST')
    port=os.environ.get('DB_PORT')
    user=os.environ.get('DB_USER')
    passwd=os.environ.get('DB_PASS')
    attrs=os.environ.get('UP_ATTRS')
    try:
        options,args = getopt.getopt(sys.argv[1:],"p:i:u:s:a:", ["ip=","port=","user=","secret=","attrs="])
    except getopt.GetoptError:
        sys.exit()
    for name,value in options:
        if name in ("-i","--ip"):
            host=value
        if name in ("-p","--port"):
            port=value
        if name in ("-u","--user"):
            user=value
        if name in ("-s","--secret"):
            passwd=value
        if name in ("-a","--attrs"):
            attrs=value
    config = {
        'host': host,
        'port': int(port),
        'user': user,
        'passwd': passwd,
        'charset':'utf8',
        'cursorclass':pymysql.cursors.DictCursor
        }
    db = pymysql.connect(**config)
    db.autocommit(1)
    cursor = db.cursor()
    DB_NAME = os.getenv("DB_NAME", "iam_service")
    db.select_db(DB_NAME)
    insertMenuTable('iam_menu', contentConfig)
    insertMenuTlTable('iam_menu_tl', contentConfig)
    insertMenuPermission('iam_menu_permission', contentConfig)
    ymlFile.close()