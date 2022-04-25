from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from datetime import datetime
from datetime import timedelta
import pandas as pd
import bs4
import requests
import os
import time
import matplotlib.pyplot as plt
# 解決python爬蟲requests.exceptions.SSLError: HTTPSConnectionPool(host='XXX', port=443)問題
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 抓今天日期
today = datetime.now()
today_name = datetime.strftime(today, '%Y-%m-%d')
how_days = 30
print(today_name)

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
    old_fn=r'C:/Users/USER/Downloads/vaccineCityLevel.csv'
    new_fn=r'C:/Users/USER/git-repos/python3-junior-nogithub/Taiwan_COVID_19_Side_Project/Csvs/Taiwan_COVID_19_'+today_name+'.csv'
    try:
        os.rename(old_fn,new_fn)
        print('移動更名成功')
    except Exception as err:
        # 檢查檔案是否存在
        if os.path.isfile(new_fn):
            print('原檔案已存在\n下載檔未移動')
            try:
                os.remove(old_fn)
            except OSError as e:
                print('下載檔刪除失敗',e)
            else:
                print('下載檔刪除成功')
        else:
            print('檔案不存在、路徑不正確或移動更名失敗')

    driver.close()

# 製作近30天的日期


def Change_months_fn():
    ago_list = []

    today = datetime.now()
    print('今天-1日期:', today)
    ago_30 = today-timedelta(days=how_days)
    print('30天前日期:', ago_30)

    # 印出時間字串 range可以控制日期範圍
    for t in range(0, how_days-1):
        ago_days = ago_30+timedelta(t)  # 從30天前一天一天累加至今天
        ago_days = datetime.strftime(ago_days, '%Y-%m-%d')   # 將時間格式轉成字串
        ago_list.append(ago_days)
    print(ago_list)
    Crawler_CitysAreas_fn(ago_list)

# 爬取北中南東台灣分類縣市及六都縣市 轉換成需要的樣子 練習簡單處理字串


def Crawler_CitysAreas_fn(ago_list):
    # ----北中南東台灣----
    url = 'https://www.ndc.gov.tw/nc_77_4402'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
    response = requests.get(url, headers=headers)
    obj_soup = bs4.BeautifulSoup(response.text, 'lxml')

    c_list_1, c_list_2, citys_list, citys_dict = [], [], [], []
    change_list = ['、', '及', '與']  # 印出網頁內容後得知的內容 把這些字串轉成可以分隔用的符號*
    remove_list = ['\r\n\t', '。', '包括']  # 把不要的字串變空值

    get_citys = obj_soup.find('div', 'introduce').find_all('li')[-1]
    for city in get_citys:
        # 如果內容是bs4.element.NavigableString型態的話 表示不是標籤
        if type(city) == bs4.element.NavigableString:
            for r in remove_list:
                city = city.replace(r, '')
            for c in change_list:
                city = city.replace(c, '*')
            city = city.replace('臺', '台')
            city = city.replace('部區域', '台灣')
            c_list_1.append(city)
        else:
            print()
            # print(type(city),'是標籤所以不取')
    # print(c_list_1)

    for citys in c_list_1:
        this_areas = citys.split('：')[0]
        this_citys = citys.split('：')[1]
        # print(this_citys)
        c_list_2.append(this_citys)
        for t in c_list_2:
            this_city = t.split('*')
        citys_dict.append([this_areas, this_city])
        # citys_list.append(this_city)  # 給找df的縣市備用

    citys_dict = dict(citys_dict)
    # print(citys_list)  # 只有縣市
    print(citys_dict)  # 有北中南東台灣鍵的縣市

    # ----六都----
    sixs_url = 'https://www.president.gov.tw/Page/106'
    sixs_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
    sixs_response = requests.get(
        sixs_url, headers=sixs_headers, verify=False)  # verify=False取消控制台輸出
    sixs_soup = bs4.BeautifulSoup(sixs_response.text, 'lxml')

    sixs_citys_list = []

    get_sixs_citys = sixs_soup.find_all('div', 'big2 counties center')[0]
    # print(get_sixs_citys.text.strip())
    for get_six in get_sixs_citys:
        # 如果抓下來的文字在a標籤內 就使用type判斷bs4.element.Tag
        if type(get_six) == bs4.element.Tag:
            txts = get_six.text.strip()
            txts = txts.replace('臺', '台')
            sixs_citys_list.append(txts)
    # print(sixs_citys_list)
    sixs_citys_dict = {'六都': sixs_citys_list}
    # print(sixs_citys_dict)
    citys_dict_new = citys_dict.copy()
    citys_dict_new.update(sixs_citys_dict)   # 合併字典
    print(citys_dict_new)
    Read_datas_fn(citys_dict_new, ago_list)


# 讀取數據
def Read_datas_fn(citys_dict_new, ago_list):
    fn = 'Csvs/Taiwan_COVID_19_'+today_name+'.csv'
    df = pd.read_csv(fn)
    # 找出每行的列是否有空值
    print(pd.isnull(df).sum(axis=1))  # 按行方向印出內容是否空值 因此axis=1
    df.dropna(axis=0, how='any')     # 刪除列 因此axis=0
    print(df)
    # 用for跑which_可依序一次畫好圖
    for keys, values in citys_dict_new.items():
        Create_plt_df_fn(keys, values, df, ago_list, citys_dict_new)


def Create_plt_df_fn(keys, values, df, ago_list, citys_dict_new):
    nums_list = [list() for n in range(len(ago_list))]
    for i, ago in enumerate(ago_list):
        city_nums = df.loc[df['個案公佈日'] == ago]   # 先搜尋需要的日期縮小範圍
        print(i, ':', ago)
        df_columns = values
        df_columns = list(df_columns)
        for v in values:
            nums = city_nums.loc[city_nums['縣市'] == v]    # 再搜尋符合which_字典鍵的值
            # print(len(nums))                            # 並len計算確診數
            nums_list[i].append(len(nums))              # 每個日期各縣市確診數為一個list
    print(nums_list)
    print(df_columns)

    # 建立成畫圖用的df
    trends_nums_df = pd.DataFrame(
        nums_list, columns=df_columns, index=ago_list)
    print(trends_nums_df)

    # 從字串轉成日期格式 以免太多擠在一起
    to_date_index = trends_nums_df.index
    to_date_index = pd.to_datetime(to_date_index)
    Plt_which_fn(keys, to_date_index, trends_nums_df, citys_dict_new)


def Plt_which_fn(keys, to_date_index, trends_nums_df, citys_dict_new):
    # 顯示中文
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False

    fig = plt.figure(dpi=100, figsize=(12, 8))
    # 依序畫出每個圖
    for oo in citys_dict_new[keys]:
        plt.plot(to_date_index, trends_nums_df[oo], '-*', label=oo)
    plt.title(keys+'各縣市近'+str(how_days)+'天疫情走勢圖', fontsize=30)
    plt.xticks(fontsize=13, rotation=20)
    plt.yticks(fontsize=13)
    plt.legend(loc='best', fontsize=13)
    plt.show()


if __name__ == '__main__':
    Crawler_datas_fn()
    Change_months_fn()

print('執行完成')
