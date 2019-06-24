# coding: utf-8
import psycopg2
import pandas as pd
import numpy as np
import time 

import pandas.io.formats.excel
pandas.io.formats.excel.header_style = None

def define_db_rule_sql(name_list):
    db_rule_sql = """select name,rule,t2.createdate,SUBSTRING(rule,1,58) url_head
    from 
    (
    select name,appid from schema.table
    where name in """+str(name_list)+"""
    )t1
    join 
    (select * from 
    (select appid,rule,createdate  from  schema.table 
    ) t0
    ) t2 
    using(appid)
    """
    return db_rule_sql
def get_rule(file_path):
    rule = pd.read_csv(open(file_path),header=None)
    rule.columns = ['rule']
    rule['rule_head']  = rule.rule.str[:58]
    print(file_path+':rule数据读取完成！')
    return rule

def reset_sql(rule_tuple,rule_head_tuple):
    db_rule_sql = """
                select appid,rule from schema.table
                where rule in """+str(rule_tuple)

    rule_head_name_sql = """ 
    select distinct appid,name,rule_head from
        (
        select appid,rule,SUBSTRING(rule,1,58) as rule_head from schema.table
        where SUBSTRING(rule,1,58) in """+str(rule_head_tuple)+"""
        )t0
        join 
        (select appid,name from  schema.table) t1
        using(appid)
    """
    print('sql初始化完成！')
    return db_rule_sql,rule_head_name_sql


def get_db_data(db_rule_sql,rule_head_name_sql):
    conn = psycopg2.connect(database="", user="", password="#Up9w", host="...", port="")
    db_rule =  pd.read_sql_query(db_rule_sql,con = conn)
    rule_name =  pd.read_sql_query(rule_head_name_sql,con = conn)
    print('rule相关数据匹配完成！')
    return db_rule,rule_name

def define_insert_sql(name,rule):
    insert_sql = """select * from  schema.table('"""+str(name)+"""','"""+str(rule)+"""');"""
    return insert_sql

def output_insert_sql(new_rule):
    for index in new_rule.index:
        rule = new_rule.loc[index]['rule']
        name = new_rule.loc[index]['name']
        insert_sql = define_insert_sql(name,rule)
        print(insert_sql)

def output_to_excel(rule_full):
    date_time = time.strftime('%Y%m%d_%H%M',time.localtime(time.time()))
    file_name =date_time+'new_rule_check.xlsx'
    rule_full.to_excel(file_name,index=False)
    print("新rule确认文件保存成功1见：  "+file_name)
    
def get_rule_tuple(data_series):
    rule_list =list(data_series)
    if len(rule_list)<=1:
        rule_list.append(0)
    rule_tuple = tuple(rule_list)
    return rule_tuple


def main():
    # 读取新增的rule
    file_path = 'new_rule.txt'
    rule = get_rule(file_path)
    # 获取元组格式的rule,rulehead
    rule_tuple = get_rule_tuple(rule.rule)
    rule_head_tuple =  get_rule_tuple(rule.rule_head ) 
    # 重置sql语句，读取已在库中的rule和所有新rule的rule_head 对应的name
    db_rule_sql,rule_head_name_sql = reset_sql(rule_tuple,rule_head_tuple)
    db_rule,rule_name = get_db_data(db_rule_sql,rule_head_name_sql)

    rule_full = rule.join(rule_name.set_index('rule_head'),on='rule_head')
    rule_full['isnew'] = rule_full.rule.apply(lambda x: 0 if x in list(db_rule['rule'])  else 1)

    new_rule = rule_full.query('isnew==1')
    # 输出插入rule的sql语句
    output_insert_sql(new_rule)
    # 输出和数据库中的rule对比后的 excel文件
    output_to_excel(rule_full)
    
if __name__ == '__main__':
    main()