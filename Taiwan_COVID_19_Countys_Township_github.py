from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from datetime import datetime
from datetime import timedelta
import numpy as np
import pandas as pd
import requests
import bs4
import re
import time
import os
import matplotlib.pyplot as plt

# 抓今天日期
today = datetime.now()
today_name = datetime.strftime(today, '%Y-%m-%d')

# 先設定好想畫得縣市圖
north = ['台北市', '新北市']   # 輸入想尋找的縣市

# 轉換成本月及上個月的月份


def Change_months_fn(today_name):
    global today_new, today_old, month_new, month_old, year_new
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

# 爬取台灣各縣市 依照縣市代碼用字典順序排列


def Get_countys_dict_Fn():
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
    # print(taiwan_county_dict,'\n')

    # sorted排序後會轉list 所以需再轉dict
    # sorted排序後會轉list 所以需再轉dict
    taiwan_county_dict = dict(sorted(taiwan_county_dict.items()))
    # print(taiwan_county_dict,'\n')

    taiwan_county_list = list(taiwan_county_dict.values())
    print(taiwan_county_list)
    print()

# 爬取台灣各縣市行政區域 縣市與鄉鎮結合


def Get_townships_dict_Fn():
    url = 'https://c2e.ezbox.idv.tw/zipcode.php'
    html = requests.get(url)
    obj_soup = bs4.BeautifulSoup(html.text, 'lxml')
    obj_soup.encoding = 'utf-8'

    remove_list = ['\n\n\n\n', '\n\n\n', '\n\n', '\u3000']
    city_list, area_list, area_list_new, county_list = [], [], [], []
    count = 0

    tag_1 = obj_soup.find_all('div', 'pure-g')[1].find_all('div', 'pure-u-1')
    # print(tag_1)

    # 刪除空字串
    def remove_len_0(lists):
        for l in lists:
            if len(l) == 0:
                lists.remove(l)
            # print(l)

    # print(tag_1)
    for t_1 in tag_1:
        citys = t_1.find('div', 'city')
        areas = t_1.find('div', 'area')

        count += 1  # 給編號確認這網頁亂78遭的結構
        citys_txt = citys.text.strip()
        citys_txt = citys_txt.replace('臺', '台')
        areas_txt = areas.text.strip()
        areas_txt = re.sub(r'[0-9]+', '', areas_txt)  # 用正規表達式消除數字
        # 將不要的字串取代成空字串
        for r in remove_list:
            areas_txt = areas_txt.replace(r, '')

    #     print(count,':',citys_txt)
    #     print(count,':',areas_txt)
    #     print()

        # 依照縣市的數量 讓鄉鎮按照順序加入陣列 兩個list數量才會一樣方便操作
        city_list.append(citys_txt)
        area_list.append(areas_txt)

        remove_len_0(city_list)
        remove_len_0(area_list)

    # print('縣市:',city_list)

    # print('縣市:',len(city_list))
    # print('鄉鎮:',area_list)
    # print('鄉鎮:',len(area_list))

    for index, obj in enumerate(area_list):
        # print(obj)
        area_ = obj.split('\n')

        for a in area_:
            # 找出各縣市連在一起的兩個鄉鎮錯誤名稱
            if len(a) == 6:
                print(index, a)
                f3 = a[0:3]
                b3 = a[3:6]

                # 將分開後的鄉鎮依序加到該縣市list
                area_.append(f3)
                area_.append(b3)
                # 移除錯誤項目
                area_.remove(a)
        # print(area_)

        area_list_new.append(area_)
        # 單list當鍵 雙list當值 轉list不要給索引值啦 直接變dict就好
        area_dict = dict(zip(city_list, area_list_new))  # dict(zip(鍵,值))
    print(area_dict)
    Read_datas_fn(area_dict)

# 讀取數據


def Read_datas_fn(area_dict):
    fn = 'Csvs/Taiwan_COVID_19_'+today_name+'.csv'
    df = pd.read_csv(fn)
    # 找出每行的列是否有空值
    print(pd.isnull(df).sum(axis=1))  # 按行方向印出內容是否空值 因此axis=1
    df.dropna(axis=0, how='any')     # 刪除列 因此axis=0
    print(df)

    # 慢慢縮小尋找的值 .str.contains()包含哪些字串
    df_new = df.loc[df['個案公佈日'].str.contains(today_new)]  # 2022年4月
    df_old = df.loc[df['個案公佈日'].str.contains(today_old)]  # 2022年3月

    # 先有各區人數表格 才能畫圖
    def County_Area_Fn(df_):
        df_ = df_.loc[df_['鄉鎮'] == a_obj]
        len_ = len(df_)
        return len_

    # 依照數量一次創建多個list放入一個大list
    nums_area_list = [list() for n in range(len(north))]
    print(nums_area_list)
    for key, value in area_dict.items():
        print(key)
        for n_index, n_obj in enumerate(north):
            # 如果字典中有符合north的縣市 就取出2022年4月的df裡所有符合north縣市的欄位
            if key == north[n_index]:
                df_area_new = df_new.loc[df['縣市'] == north[n_index]]
                df_area_old = df_old.loc[df['縣市'] == north[n_index]]
                print(north[n_index], ':', value)

                for a_i, a_obj in enumerate(value):
                    # 透過County_Area_Fn函數取出north縣市的各行政區域確診人數
                    nums_area_new = County_Area_Fn(df_area_new)
                    nums_area_old = County_Area_Fn(df_area_old)
                    print(nums_area_new)
                    nums_area_list[n_index].append(
                        [a_obj, nums_area_old, nums_area_new])  # 列出north的縣市 一次一縣市
            # print(nums_area_list)
                df_nums_area = pd.DataFrame(nums_area_list[n_index], columns=[
                                            '行政區', today_old+'月', today_new+'月'])  # 將上面一次一縣市的list轉df
                print('-'*50)
                print(df_nums_area)
                Plot_pic_fn(n_obj, value, df_nums_area)
            else:
                pass

# 畫圖 n_obj給圖的標題


def Plot_pic_fn(n_obj, value, df_nums_area):
    # 顯示中文
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False

    plt.figure(dpi=100, figsize=(20, 12))

    # 設定x軸柱狀位置
    x_position = np.arange(len(value))
    x_width = 0.25  # 柱狀寬度

    plt.bar(x_position+(x_width/2),
            df_nums_area[today_new+'月'], label=today_new+'月', width=0.25)
    plt.bar(x_position-(x_width/2),
            df_nums_area[today_old+'月'], label=today_old+'月', width=0.25)

    plt.title(year_new+'年'+n_obj+'近兩個月各行政區確診人數', fontsize=50)

    if len(value) > 20:
        plt.xticks(x_position, value, fontsize=18, rotation=50)
        plt.yticks(fontsize=15)
        plt.legend(loc='best', fontsize=15)
        plt.xlabel('-- 鄉鎮 --', fontsize=18)
        plt.ylabel('-- 人數 --', fontsize=18)
        # 柱狀圖頂端顯示數值
        for a, b in zip(x_position+(x_width/2), df_nums_area[today_new+'月']):
            plt.text(a, b+0.05, '%.0f' %
                     b, ha='center', va='bottom', fontsize=16)
        for a, b in zip(x_position-(x_width/2), df_nums_area[today_old+'月']):
            plt.text(a, b+0.05, '%.0f' %
                     b, ha='center', va='bottom', fontsize=12)
    else:
        plt.xticks(x_position, value, fontsize=25, rotation=25)
        plt.yticks(fontsize=20)
        plt.legend(loc='best', fontsize=15)
        plt.xlabel('-- 鄉鎮 --', fontsize=20)
        plt.ylabel('-- 人數 --', fontsize=20)
        # 柱狀圖頂端顯示數值
        for a, b in zip(x_position+(x_width/2), df_nums_area[today_new+'月']):
            plt.text(a, b+0.05, '%.0f' %
                     b, ha='center', va='bottom', fontsize=23)
        for a, b in zip(x_position-(x_width/2), df_nums_area[today_old+'月']):
            plt.text(a, b+0.05, '%.0f' %
                     b, ha='center', va='bottom', fontsize=15)
    plt.show()


if __name__ == '__main__':
    Change_months_fn(today_name)
    Crawler_datas_fn()
    Get_countys_dict_Fn()
    Get_townships_dict_Fn()

print('執行完成')
