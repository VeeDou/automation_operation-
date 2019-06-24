# coding: utf-8
# #### 1.数据分布
# #### 2.数据重复
# #### 3.移动平均异常

# bokeh.__version__  =   '0.12.16'
# bokeh.__version__  =   '1.1.0'


import psycopg2
import pandas as pd
import numpy as np

import pandas.io.formats.excel
pandas.io.formats.excel.header_style = None

from bokeh.plotting import figure, show,output_notebook
from bokeh.layouts import column, gridplot
from bokeh.models import Circle, ColumnDataSource, Div, Grid, Line, LinearAxis, Plot, Range1d,HoverTool,BasicTickFormatter
from bokeh.document import Document
from bokeh.embed import file_html
from bokeh.util.browser import view
from bokeh.resources import INLINE


import time

def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]


## 数据分布的sql
def reset_sql(date_start,rank_monthid,rank_upper_limit,growth_lower_limit,growth_upper_limit):
    sql_dict = {}
    date_distribute_sql = '''select days_cnt,count(*) as days_cnt_cnt from 
    (
        select t0.appid,t0.days_cnt,t1.rank from 
        (
            select appid,count(*) days_cnt from schema.table
            where date_id>='''+str(date_start)+'''
            and date_type='D'
            GROUP BY appid
        )t0
        join 
        (
            select appid,rank from schema.table 
            where date_id ='''+str(rank_monthid)+'''
            and rank <= '''+str(rank_upper_limit)+'''
        ) t1
        using(appid)
    ) t2
    group by days_cnt  
    order by days_cnt desc '''

    ## 数据天数异常的sql
    days_exception_sql = '''
        with cte as 
        (
        select appid,days_cnt,name,rank from 
        (
            select t0.appid,t0.days_cnt,t1.rank,name from 
            (
                select appid,count(*) days_cnt from schema.table
                where date_id>='''+str(date_start)+'''
                and date_type='D'
                GROUP BY appid
            )t0
            join 
            (
                select appid,rank from schema.table 
                where date_id ='''+str(rank_monthid)+'''
                and rank <=  '''+str(rank_upper_limit)+'''
            ) t1
            using(appid)
            join 
            (
                select appid,name from schema.table 
            ) t3
            using(appid)
        ) t2
    )
    select * from cte 
    where days_cnt < (select max(days_cnt) from cte)
    order by rank asc,days_cnt desc
    '''
    ## 数据重复的sql
    data_repeat_sql = '''
    select date_id ,count(*) from 
    (
    select date_id,appid,date_id_cnt from 
    (
    select date_id,appid,count(*) date_id_cnt from schema.table
    where date_id>= '''+str(date_start)+'''
    and date_type='D'
    GROUP BY appid,date_id
    )t0
    where date_id_cnt>1
    ) t1 
    group by date_id
    ''' 

    # uv下降异常
    uv_down_exception_sql = '''
    SELECT A.*,
        b.name 
    FROM
        ( SELECT * FROM schema.table 
        WHERE RANK <= 2000 
        AND growth between  '''+str(growth_lower_limit)+''' and '''+str(growth_upper_limit)+''' 

        AND date_id >= '''+str(date_start)+'''
      )
    A JOIN schema.table b ON b.appid = A.appid -- order by growth
    ORDER BY rank,date_id ;
    '''

    sql_dict['date_distribute_sql'] = date_distribute_sql
    sql_dict['days_exception_sql'] = days_exception_sql
    sql_dict['data_repeat_sql'] = data_repeat_sql
    sql_dict['uv_down_exception_sql'] = uv_down_exception_sql

    return sql_dict

def initial_lt_ol_sql(appids):
    
    lt_online_sql = """
    select t0.*,t1.uv_lt,t2.rank from 
    (
    select appid,date_id,uv as uv_ol,name 
    from schema.table 
    where  date_type = 'D'
    and appid in  """+ str(appids)+ """
    ) t0
     join (select appid,date_id,uv as uv_lt from schema.table)  t1
     using(appid,date_id)
    join (select appid,rank from schema.table where date_id = 201904)  t2
    using(appid)
    order by appid,date_id
    """

    return lt_online_sql

def initial_max_rule_date_sql(appids):
    max_rule_date_sql = """
    select name,max_date,xx_id as appid
    from 
    (
    select t0.name,t1.max_date,xx_id,appid from 
    (
    select appid,xx_id,name  
    from schema.table 
    where  xx_id in """+ str(appids)+ """
    ) t0
     join 
         (select appid,substring(max(createdate)::text,1,16) max_date from schema.table
            group by appid
         )  t1
     using(appid)
     )t2
    """
    return max_rule_date_sql

def formate_data_visual(lt_online):
    # 按字典组装，方便排序和作图
    group = lt_online.groupby('name')
    group_dict = {}
    for x in group:
    #     print(x[1])
        k = x[1]['rank'].iloc[0]
        v = x[1]
        group_dict[k] = v

    # 排序 取数
    sorted_group_dict = sorted( group_dict.items(),reverse =False )[:]
    return sorted_group_dict


def intergrate_lt_data(sql_dict):
    data_dict = {}
    ## 跑sql 取数
    conn = psycopg2.connect() # 马赛克
    conn_crawler = psycopg2.connect() # 马赛克
    
    date_distribute=  pd.read_sql_query(sql_dict['date_distribute_sql'],con = conn)
    days_exception = pd.read_sql_query(sql_dict['days_exception_sql'],con = conn)
    data_repeat = pd.read_sql_query(sql_dict['data_repeat_sql'],con = conn)
    uv_down_exception = pd.read_sql_query(sql_dict['uv_down_exception_sql'],con = conn) 


    appid_list = list(uv_down_exception['appid'])

    if len(appid_list)<=1:
        return None 
#     elif len(appid_list)==0:
#         appids = "('0')"
    else:
        appids = tuple(appid_list)
        # print(appids)
        # print(uv_down_exception_sql)

        lt_online_sql = initial_lt_ol_sql(appids)
        max_rule_date_sql = initial_max_rule_date_sql(appids)

        lt_online =  pd.read_sql_query(lt_online_sql,con = conn)
        max_rule_date =  pd.read_sql_query(max_rule_date_sql,con = conn_crawler)

        lt_online['date_id_format'] = pd.to_datetime(lt_online.date_id,format="%Y%m%d")     
        conn.close()

        lt_online = lt_online.join(max_rule_date.set_index(['name','appid']),on = ['name','appid'])
        lt_online_brief = lt_online[['date_id_format','uv_ol','uv_lt','rank','name','max_date']]

        data_dict['lt_online_brief'] = lt_online_brief
        data_dict['date_distribute'] = date_distribute
        data_dict['data_repeat'] = data_repeat
        data_dict['days_exception'] = days_exception
        data_dict['uv_down_exception'] = uv_down_exception

        return data_dict 

def out_put_data_info(rank_monthid,rank_upper_limit,date_start,data_dict):
    print("0.最大天数：%d"%max(data_dict['date_distribute']['days_cnt']))
    print('1、'+str(rank_monthid)+"排名 Top"+str(rank_upper_limit)+'小程序数据天数正常比例：'+str(round(data_dict['date_distribute'].iloc[0]['days_cnt_cnt']/int(rank_upper_limit),4)*100)+'%'+'\n'+'起始时间：'+str(date_start)+'\n')
    print('2、天数异常top'+ str(int(rank_upper_limit)/2) +' \n'+str(data_dict['days_exception'].query('rank<='+str(int(rank_upper_limit)/2)))+'\n')
    if len(data_dict['data_repeat']) == 0:
        print("3、数据重复:没有数据重复 \n")
    else:
        print('3、数据重复：\n'+str(data_dict['data_repeat'])+'\n')



    try:
        # 输出异常天数的小程序及其对应的天数，按rank升序拍列
        date_time = time.strftime('%Y%m%d_%H%M',time.localtime(time.time()))
        file_name =date_time+'_days_exception.xlsx'
        data_dict['days_exception'].to_excel(file_name,index=None)

        uv_down_exception_name_appid = data_dict['uv_down_exception'][['name','appid']].drop_duplicates()
        uv_down_exception_name_appid.to_excel('数据审核表'+date_time+'.xlsx',index=False)

        print("异常天数小程序保存成功:见文件  "+file_name)
    except Exception as e:
        print(e)
        print("异常天数小程序保存失败！！")


## 画图
# 定义悬浮组件和对应的字段格式
def define_hover():
    hover = HoverTool(tooltips=[
        ("index", "$index"),
        ("date_id", "@x{%F}"),  # must specify desired format here
        ("uv", "$y{F}")]
        ,formatters=dict(x='datetime'),
        # display a tooltip whenever the cursor is vertically in line with a glyph
        mode='vline')
    return hover


def intergrate_data(lt_online):
    # 按字典组装，方便排序和作图
    group_top = lt_online.groupby('name')
    group_dict_top = {}
    for x in group_top:
    #     print(x[1])
        k = x[1]['rank'].iloc[0]
        v = x[1]
        group_dict_top[k] = v

    # 排序 取数
    sorted_group_dict_top = sorted( group_dict_top.items(),reverse =False )[:]
    return sorted_group_dict_top



def make_plot(data):
    # 设置图标悬浮工具及数据格式
    hover = define_hover()
    # 定义 长宽、X轴数据类型、悬浮工具、y轴范围、标题
    x = data.date_id_format
    y1 = data.uv_ol
    y2 = data.uv_lt
    
    title1 = str(data['rank'].iloc[0])+ "  "+data.name.iloc[0] 
#     print(data.max_date.iloc[0])
    title2 = str(data['rank'].iloc[0])+ "  "+data.name.iloc[0] + "  最新rule："+data.max_date.iloc[0]
    
    p1 = figure(plot_width=400, plot_height=250, x_axis_type="datetime",tools=[hover],y_range= (0,max(y1)),title=title1)
    p1.yaxis.formatter = BasicTickFormatter(use_scientific=False)
    p1.line(x,y1, color='green')

    p2 = figure(plot_width=400, plot_height=250, x_axis_type="datetime",tools=[hover],y_range= (0,max(y2)),title=title2)
    p2.yaxis.formatter = BasicTickFormatter(use_scientific=False)
    p2.line(x,y2, color='orange')

    return p1,p2

def dco_intergrate(sorted_group_dict_top):
    # 构建图表数据结构。 按照每行两个图（1个线上，1个线下）的结构去存储。
    plot_list = []
    for x in sorted_group_dict_top:
    #     print(x)
        data = x[1]
        p1,p2 = make_plot(data)
        plot_list.append([p1,p2])
    

    grid = gridplot(plot_list, toolbar_location=None)
    div = Div(text="""
    <h1>Data review tools</h1>
    <p>快速审阅数据的整体情况。</p>
    <p>左边是线上数据，右边是原始数据。</p>
    """)
    
    

    doc = Document()
    doc.add_root(column(div,grid, sizing_mode="scale_width"))
    return doc

def html_intergrate(doc):
    doc.validate()
    filename = "周数据审核图.html"
    with open(filename, "w",encoding='utf-8') as f:
        f.write(file_html(doc, INLINE, "周数据审核V2"))
    print("线上&原始数据输出见： %s" % filename)
    view(filename)





def main():
    #  按照参数重置sql
    date_start = 20190601
    rank_monthid = 201904
    rank_upper_limit = 500
    growth_lower_limit = -0.7
    growth_upper_limit = -0.5

    # 重置sql
    sql_dict = reset_sql(date_start,rank_monthid,rank_upper_limit,growth_lower_limit,growth_upper_limit)
    # 整合原始数据（原始+线上+rule最新日期）
    data_dict = intergrate_lt_data(sql_dict)
    if data_dict!=None:
        # 将数据基础情况输出到命令行
        out_put_data_info(rank_monthid,rank_upper_limit,date_start,data_dict)
        # 将数据按照rank排名
        sorted_group_dict_top = intergrate_data(data_dict['lt_online_brief'] )
        # 将数据输出（我也不知道怎么用，直接套的模板）
        doc = dco_intergrate(sorted_group_dict_top)
        # 整合html内容，并保存为html文件
        html_intergrate(doc)
    else:
        print('无异常数据！')
if __name__ == '__main__':
    main()