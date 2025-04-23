import csv
import requests
from lxml import etree
from pyecharts.globals import CurrentConfig, NotebookType
CurrentConfig.NOTEBOOK_TYPE = NotebookType.JUPYTER_NOTEBOOK
from pyecharts.charts import Line
import pandas as pd
import numpy as np
from pyecharts import options as opts
import os

generate_html = os.path.dirname(os.path.abspath(__file__)) + '\\temperatures.html'

#第一步，爬取数据，并用xpath进行简单的数据过滤
#请求网址
def future_weather():
     try:
        url='https://weather.cma.cn/web/weather/58946'
    #模拟浏览器<请求头>
        headers={
            'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
        }
        response=requests.get(url=url,headers=headers) #爬取到的数据返回至参数response
        resp_html = etree.HTML(response.text) #利用HTML函数将html文本内容解析成html对象
        resp_list=resp_html.xpath("//div[@class='row hb days ']")#利用xpath对标签的索引来进行文本定位
        for item in resp_list:
            data=item.xpath("//div[@class='day-item']/text() ")
            temper_high= item.xpath("//div[@class='high']/text() ")#注意要加上text（）函数转化为可阅读的文本
            temper_low=item.xpath("//div[@class='low']/text() ")
        #     print(data,temper_high,temper_low)
        # print(response.text)
    #第二步，创建字典来接收数据
        time=list()
        dayweather=list()
        daywind=list()
        nightweather=list()
        nightwind=list()
        for i in range(7):#将data中的数据分类并提取出来，创建序列来接收
            time.append(data[0+(i*8)]+data[1+(i*8)])
            dayweather.append(data[2 + (i * 8)])
            daywind.append(data[3+(i*8)]+data[4+(i*8)])
            nightweather.append(data[5 + (i * 8)])
            nightwind.append(data[6+(i*8)]+data[7+(i*8)])

        dict={ #创建字典，值为序列
            '时间':time,
            '日间天气':dayweather,
            '日间；风向/风力':daywind,
            '夜间天气':nightweather,
            '夜间；风向/风力':nightwind,
            '最高温': temper_high,
            '最低温': temper_low
            }
        # for key,value in dict.items():
        #     print(key,'--',value)
        f=open('data.csv',mode='w',newline='')#创建csv文件，模式写入，因为换行符的多样，所以csv文件中使用newline参数总是安全的
        csv_writer=csv.DictWriter(f,fieldnames=[    #表头内容
            '时间',
            '日间天气',
            '日间：风向/风力',
            '夜间天气',
            '夜间：风向/风力',
            '最高温',
            '最低温',
        ])
        csv_writer.writeheader()#创建表头
        item=list()
        for i in range(7): #循环将字典中的序列一一赋值给item
            item={'时间':dict['时间'][i],'日间天气':dict['日间天气'][i],'日间：风向/风力':dict['日间；风向/风力'][i],'夜间天气':dict['夜间天气'][i],'夜间：风向/风力':dict['夜间；风向/风力'][i],'最高温':dict['最高温'][i],'最低温':dict['最低温'][i]}
            csv_writer.writerow(item) #每行写入item
     except requests.exceptions.ConnectionError as e:
         print("网络请求发生异常,请检查网络连接...\n若依然无法运行,请检查'url'变量...\n", e)
         exit()
def weather_view():

    df = pd.read_csv('./data.csv', encoding='ANSI')
    info = df.iloc[:, 0]
    week_name_list = list(df.iloc[:, 0])
    high_temperature = [int(item.replace('℃', '')) for item in list(df.iloc[:, 5])]
    low_temperature = [int(item.replace('℃', '')) for item in list(df.iloc[:, 6])]
    try:
        (
            Line()
            .add_xaxis(xaxis_data=week_name_list)
            .add_yaxis(
                series_name="最高气温",
                y_axis=high_temperature,
                markpoint_opts=opts.MarkPointOpts(
                    data=[
                        opts.MarkPointItem(type_="max", name="最大值"),
                        opts.MarkPointItem(type_="min", name="最小值"),
                    ]
                ),
                markline_opts=opts.MarkLineOpts(
                    data=[opts.MarkLineItem(type_="average", name="平均值")]
                ),
            )
            .add_yaxis(
                series_name="最低气温",
                y_axis=low_temperature,
                markpoint_opts=opts.MarkPointOpts(
                    data=[opts.MarkPointItem(value=-2, name="周最低", x=1, y=-1.5)]
                ),
                markline_opts=opts.MarkLineOpts(
                    data=[
                        opts.MarkLineItem(type_="average", name="平均值"),
                        opts.MarkLineItem(symbol="none", x="90%", y="max"),
                        opts.MarkLineItem(symbol="circle", type_="max", name="最高点"),
                    ]
                ),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="未来一周气温变化", subtitle=""),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                toolbox_opts=opts.ToolboxOpts(is_show=True),
                xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            )
            .render(generate_html) #将html文件路径存到generate_html
        )
    except FileNotFoundError:
        print("请检查当前路径的future_weather_forecast.py文件下的(generate_html)是否完整")
        exit()
