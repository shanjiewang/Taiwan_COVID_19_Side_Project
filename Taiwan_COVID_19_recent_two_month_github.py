from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import matplotlib.pyplot as plt
import time
import os
import requests
import bs4
import numpy as np
import pandas as pd

# 抓今天日期
today = datetime.now()
today_name = datetime.strftime(today, '%Y-%m-%d')

# 爬取官方網站數據


def Crawler_datas_fn():
    url = 'https://covid-19.nchc.org.tw/city_confirmed.php?downloadall=yes'
    driver_path = Service('D:/chromedriver.exe')
    driver = webdriver.Chrome(service=driver_path)
    driver.get(url)

    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    time.sleep(2)
    driver.find_elements(
        By.CSS_SELECTOR, '#myTable02_wrapper .dt-buttons .dt-button')[2].click()

    # 等待下載及掃毒
    time.sleep(10)
    print('下載csv完成')

    # 移動及更改檔名 若有移動檔案位置記得改new_fn
    old_fn = r'C:/Users/USER/Downloads/vaccineCityLevel.csv'
    new_fn = r'C:/Users/USER/git-repos/python3-junior-nogithub/Taiwan_COVID_19_Project/Csvs/Taiwan_COVID_19_'+today_name+'.csv'
    try:
        os.rename(old_fn, new_fn)
        print('移動更名成功')
    except Exception as err:
        # 檢查檔案是否存在
        if os.path.isfile(r'C:/Users/USER/git-repos/python3-junior-nogithub/Taiwan_COVID_19_Project/Csvs/Taiwan_COVID_19_'+today_name+'.csv'):
            print('原檔案已存在\n下載檔未移動')
            try:
                os.remove(old_fn)
            except OSError as e:
                print('下載檔刪除失敗', e)
            else:
                print('下載檔刪除成功')
        else:
            print('檔案不存在或移動更名失敗')

    driver.close()

# 轉換成本月及上個月的月份


def Change_months_fn(today_name):
    global today_new, today_old, month_new, month_old
    today_new = today_name[0:7]
    year_new = today_new.split('-')[0]
    month_new = today_new.split('-')[1]
    # 如果本月是1月 上個月的年份要-1
    if month_new == '01':
        month_old = '12'
        year_old = int(year_new)-1
    else:
        year_old = year_new
        month_old = int(month_new)-1
        if month_old < 10:
            month_old = '0'+str(month_old)
    today_old = str(year_old)+'-'+str(month_old)
    print(today_new)  # 本月份
    print(today_old)   # 上個月份

# 讀取數據


def Read_data_fn():
    fn = 'data_csvs/Taiwan_COVID_19_'+today_name+'.csv'
    df = pd.read_csv(fn)
    # 找出每行的列是否有空值
    print(pd.isnull(df).sum(axis=1))  # 按行方向印出內容是否空值 因此axis=1
    df.dropna(axis=0, how='any')     # 刪除列 因此axis=0
    print(df)

    # 抓取本月及前一個月的數據
    # str.contains找到某標題行包含特定字串的列
    df_new = df.loc[df['個案公佈日'].str.contains(today_new)]
    df_old = df.loc[df['個案公佈日'].str.contains(today_old)]
    print(df_new)
    print(df_old)

    County_dict_fn(df_new, df_old)

# 爬取縣市網站內容 用字典方式排列縣市順序


def County_dict_fn(df_new, df_old):
    url = 'http://www.isha.org.tw/tools/2012web_s_tools_02a_01%E7%B8%A3%E5%B8%82%E5%88%A5%E4%BB%A3%E7%A2%BC%E8%A1%A8.asp'
    html = requests.get(url)
    html.encoding = 'utf-8'
    obj_soup = bs4.BeautifulSoup(html.text, 'lxml')

    obj_td2 = obj_soup.find_all('td')
    # print(obj_td2)

    td2_list = []
    for td2 in obj_td2:
        txts = td2.text
        if txts == '桃園縣':
            txts = '桃園市'
        td2_list.append(txts.strip())

    # list可以透過slice轉成dict
    taiwan_county_dict = dict(zip(td2_list[0::2], td2_list[1::2]))
    print(taiwan_county_dict, '\n')

    # sorted排序後會轉list 所以需再轉dict
    taiwan_county_dict = dict(sorted(taiwan_county_dict.items()))
    # print(taiwan_county_dict,'\n')
    taiwan_county_list = list(taiwan_county_dict.values())

    Create_plt_df_fn(taiwan_county_list, df_new, df_old)
    # print(taiwan_county_list)

# 抓取畫圖要用的欄位 並轉換成需要的格式


def Create_plt_df_fn(taiwan_county_list, df_new, df_old):

    county_num_list = []

    def Taiwan_County_Fn(df_):
        df_1 = df_.loc[df_['縣市'] == t_obj]
        len_ = len(df_1)
        return len_

    for t_i, t_obj in enumerate(taiwan_county_list):
        nums_new = Taiwan_County_Fn(df_new)   # 本月各縣市確診人數
        nums_old = Taiwan_County_Fn(df_old)   # 前一個月月各縣市確診人數
        county_num_list.append([t_obj, nums_old, nums_new])
    print(county_num_list)

    # 轉換成畫圖用的df格式
    df_county_num = pd.DataFrame(county_num_list, columns=[
                                 'County', today_old, today_new])
    print(df_county_num)

    Plt_fn(df_county_num)

# 畫出台灣各縣市近兩個月COVID19確診人數柱狀圖


def Plt_fn(df_county_num):
    # 顯示中文
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False

    # 設定圖片大小
    plt.figure(dpi=120, figsize=(16, 10))

    # 設定x軸柱狀位置
    x_position = np.arange(len(df_county_num['County']))
    x_width = 0.25  # 柱狀間格寬度

    # 開始畫柱狀圖
    plt.bar(x_position+x_width/2,
            df_county_num[today_new], label=today_new+'月', width=0.25)
    plt.bar(x_position-x_width/2,
            df_county_num[today_old], label=today_old+'月', width=0.25)
    plt.xticks(x_position, df_county_num['County'],
               rotation=45, fontsize=18)  # 設定關於x軸的物件
    plt.yticks(fontsize=18)
    plt.legend(loc='best', fontsize=18)  # 設定圖例位置

    # 柱狀圖頂端顯示數值
    for a, b in zip(x_position+x_width/2, df_county_num[today_new]):
        plt.text(a, b+0.05, '%.0f' % b, ha='center', va='bottom', fontsize=20)
    for a, b in zip(x_position-x_width/2, df_county_num[today_old]):
        plt.text(a, b+0.05, '%.0f' % b, ha='center', va='bottom', fontsize=10)

    plt.title('台灣各縣市近兩個月COVID19確診人數', fontsize=35)
    plt.xlabel('-- 縣市 --', fontsize=18)
    plt.ylabel('-- 人數 --', fontsize=18)
    plt.show()


if __name__ == '__main__':
    Crawler_datas_fn()
    Change_months_fn(today_name)
    Read_data_fn()

print('執行完成')
