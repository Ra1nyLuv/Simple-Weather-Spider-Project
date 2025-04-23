import schedule
import os
from bs4 import BeautifulSoup
import requests
import re
from time import localtime, sleep
import pyttsx3
import future_weather_forecast

#       获取爬取的初步实时数据, 还需传入process_data()函数进行数据处理
def get_data():

    try:
    #       申请获取网址数据
        response = requests.get(url)
        response.encoding = "utf-8"

        soup = BeautifulSoup(response.text, 'html.parser')
        data1 = soup.find_all('span')
        data2 = soup.find_all('div')

        data = str(data1) + str(data2)

        return str(data)

    except requests.exceptions.ConnectionError as e:
        print("网络请求发生异常,请检查网络连接...\n若依然无法运行,请检查'url'变量...\n", e)
        exit()


#       整合处理数据, 并根据传入的数据生成天气报告的文本, 再将其传入write_file()函数
def process_data():
    data = get_data()
    result = dict()
    result['湿度'] = None
    result['风向'] = None
    result['空气质量'] = None
    result['紫外线'] = None
    result['平均温度'] = None
    result['最低温'] = None
    result['最高温'] = None
    result['天气状况'] = None

    s1 = re.compile(r'\d+%')
    for i in s1.findall(data):
        result['湿度'] = i

    s2 = re.compile(r'\w{1,2}风')
    for i in s2.findall(data):
        result['风向'] = i

    s3 = re.compile(r'空气：+\w +\d{1,2}')
    for i in s3.findall(data):
        result['空气质量'] = i

    s4 = re.compile(r'紫外线 \w{1,2}')
    for i in s4.findall(data):
        result['紫外线'] = i

    s5 = re.compile(r'平均温度：\d{1,2} ~ \d{1,2}°C')
    for i in s5.findall(data):
        result['平均温度'] = i

    s6 = re.compile(r'最低温（\d{1,2}°）')
    for i in s6.findall(data):
        result['最低温'] = i

    s7 = re.compile(r'最高温（\d{1,2}°）')
    for i in s7.findall(data):
        result['最高温'] = i

    s8 = re.search(r'<dd class="txt">(.*?)</dd>', data)
    temp = re.findall(r'[\u4e00-\u9fa5]+', str(s8))

    if temp[0] != temp[1]:
        result['天气状况'] = temp[0]+'转'+ temp[1]
    else:
        result['天气状况'] = temp[0]

    result['日期'] = f"{localtime().tm_year}年{localtime().tm_mon}月{localtime().tm_mday}日{localtime().tm_hour}时{localtime().tm_min}分"

    result_text_ls = ["您好，我是您的天气小助手(●_●)\n",
                      "您的今日天气报告已生成:\n\n\n",
                      f"现在是{result['日期']}, \n" if '日期' in result and result['日期'] is not None else "",
                      f"今天的天气状况为{result['天气状况']},\n" if '天气状况' in result and result['天气状况'] is not None else "",
                      f"{result['空气质量']},  湿度为{result['湿度']},\n" if '空气质量' in result and result['湿度'] is not None else "",
                      f"风向为{result['风向']}, \n" if '风向' in result and result['风向'] is not None else "",
                      f"紫外线强度{result['紫外线'][4:7]}, \n" if '紫外线' in result and result['紫外线'] is not None else "",
                      f"\n今日{result['平均温度']}, \n{result['最高温']}，{result['最低温']}.\n\n" if '平均温度' in result and '最高温' in result and '最低温' in result
                                                                                                     and result['平均温度'] is not None and result['最高温'] is not None and result['最低温'] is not None else ""]


    #       根据天气状况添加一些小贴士
    if "晴" in result['天气状况']:
        result_text_ls.append("今天天气晴朗，适合户外活动.\n")
        if (eval(re.sub('[^0-9-]', '', ''.join(map(str,result['最高温']))))) >= 28:
            result_text_ls.append("天气炎热，请注意防暑,做好防晒.")
    elif "雨" in result['天气状况']:
        result_text_ls.append("今天有雨,尽量减少户外出行.\n")
        if "大雨" in result['天气状况']:
            result_text_ls.append("降雨强度较大，尽量避免外出，确保安全.")
        else:
            result_text_ls.append("外出时请小心滑倒.")
    elif "雪" in result['天气状况']:
        result_text_ls.append("今天可能会有雪，注意保暖.\n外出时请小心行走，避免滑倒.")
    else:
        result_text_ls.append("今天天气变化多端，请注意身体，小心感冒.")

    result_text_ls.append("\n\n希望您度过美好的一天^-^")

    return result_text_ls

#       将处理好的数据文本传入后,写入文件并设置朗读功能
def write_file():
    future_weather_forecast.future_weather()
    future_weather_forecast.weather_view()
    result_text_ls = process_data()

    #       朗读每日天气报告的文本
    def read_report():
        if set_read == True:
            weather = pyttsx3.init()

            text = str(result_text_ls)
            text = str.replace(text, '\\n', '')
            text = str.replace(text, '_', '')

            weather.say(text)
            weather.runAndWait()

    try:
        with open(report_path, "w", encoding='utf-8') as file:
            for i in result_text_ls:
                file.write(i)

            file.write('\n\n')
            os.startfile(report_path)

        # 将可视化网址写入天气报告
            file.write('--若要查看接下来一周的气温变化趋势,\n请打开下面路径文件或复制进入浏览器查看生成的气温变化折线图:\n')
            file.write(generate_html)

        print('\n--您的报告已生成, 请到桌面查看^^_')

        print("""\ntips:若要查看其他城市的天气, \n\t将'url'网址最后的/putian/ 改为需要查看的城市名的英文拼写即可
  \t\t如'https://www.tianqi24.com/fuzhou/'.""")

        read_report()

    except FileNotFoundError as e:
        print("目标文件路径不存在, 请修改'report_path'后重试...\n", e)
        exit()


#        可设定每天某个时间自动执行一次
def execute_on_time(due_time):
    schedule.every().day.at(due_time).do(get_started)

    while True:
        schedule.run_pending()
        sleep(1)
#       启动
def get_started():
    if set_run_time == False:
        write_file()
    else:
        execute_on_time(due_time)



# 以下为定义的全局变量

#       写入的目标文件路径, 设为为主机的桌面路径
report_path = os.path.join(os.path.expanduser("~"), 'Desktop') + 'Daily_Weather_Report.txt'

#       爬取天气数据的目标网址
url = "https://www.tianqi24.com/fuzhou/"
#          !!!若要查看其他城市的天气, 将'url'网址最后的/putian/ 改为需要查看的城市名的英文拼写即可!!!
#          如:   'https://www.tianqi24.com/fuzhou/'.

#       生成的可视化文件的路径
generate_html = future_weather_forecast.generate_html

#       若要使用朗读功能,将set_read设置为True即可.
set_read = False

#       若要使用定时功能,将set_run_time设置为True即可.
set_run_time = False

#       若要调整指定执行时间, 请在将"set_run_time"设为True后,修改due_time, 格式为'hh:mm'(24h制).
due_time = '07:00'

#       !!!启动!!!
get_started()