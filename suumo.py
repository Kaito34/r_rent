from bs4 import BeautifulSoup
import requests
import lxml
import pandas as pd
import time
from tqdm import tqdm


# 神奈川 横浜市全域 新着順
url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=14&sa=01&sngz=&po1=09"
# requestで取得
r = requests.get(url)
soup = BeautifulSoup(r.text, 'lxml')

# 最大ページ
for page in tqdm(range(int(soup.find_all(class_='pagination_set-nav')[0].find_all('li')[-1].text))):
    time.sleep(3)
    url = f"https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=14&sa=01&sngz=&po1=09&page={page}"

    # requestで取得
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    properties = soup.find_all('div', class_='cassetteitem')

    # 情報をリスト化
    info_lists = []
    for each_property in properties:
        # 賃貸情報
        name = each_property.find_all(class_='cassetteitem_content-title')[0].text
        address = each_property.find_all(class_='cassetteitem_detail-col1')[0].text
        near_station = each_property.find_all(class_='cassetteitem_detail-text')[0].text  # 自然言語処理で最寄り駅などの割り出し
        built_info = each_property.find_all(class_='cassetteitem_detail-col3')[0].text
        built_year = built_info.split('\n')[1]
        built_floors = built_info.split('\n')[2]

        # 複数案内がある場合はそれぞれに対して項目を抽出する
        proposes = each_property.find_all(class_='cassetteitem_other')[0]
        # ある一つの案内について
        for each_propose in proposes.find_all('tbody'):
            # 物件情報
            infos = each_propose.find_all('td')
            floor = infos[2].text.split('\r\n\t\t\t\t\t\t\t\t\t\t\t')[1]
            rent_fee = infos[3].find_all(class_='cassetteitem_price--rent')[0].text
            manegement_fee = infos[3].find_all(class_='cassetteitem_price--administration')[0].text
            deposit = infos[4].find_all(class_='cassetteitem_price--deposit')[0].text
            gratuity = infos[4].find_all(class_='cassetteitem_price--gratuity')[0].text
            layout = infos[5].find_all(class_='cassetteitem_madori')[0].text
            exclusive_area = infos[5].find_all(class_='cassetteitem_menseki')[0].text
            detail_link = infos[8].a['href']

            info_list = [name, address, near_station, built_year, built_floors, floor,
                         rent_fee, manegement_fee, deposit, gratuity, layout, exclusive_area, detail_link]
            info_lists.append(info_list)

    df_rent = pd.DataFrame(
        info_lists,
        columns=['name', 'address', 'near_station', 'built_year', 'built_floors', 'floor', 'rent_fee', 'manegement_fee',
                 'deposit', 'gratuity', 'layout', 'exclusive_area', 'detail_link'])

    try:
        df = pd.read_csv('suumo.csv')
        df = pd.concat([df, df_rent])
    except:
        df = df_rent.copy()

    if page % 10 == 0:
        df.to_csv('suumo.csv', index=False)
