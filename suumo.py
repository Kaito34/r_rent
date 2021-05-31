from bs4 import BeautifulSoup
import requests
import lxml
import pandas as pd
import time

# 神奈川全域 新着順
url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=14&sc=14101&sc=14102&sc=14103&sc=14104&sc=14105&sc=14106&sc=14107&sc=14108&sc=14109&sc=14110&sc=14111&sc=14112&sc=14113&sc=14114&sc=14115&sc=14116&sc=14117&sc=14118&sc=14131&sc=14132&sc=14133&sc=14134&sc=14135&sc=14136&sc=14137&sc=14151&sc=14152&sc=14153&sc=14201&sc=14203&sc=14204&sc=14205&sc=14206&sc=14207&sc=14208&sc=14210&sc=14211&sc=14212&sc=14213&sc=14214&sc=14215&sc=14216&sc=14217&sc=14218&sc=14300&sc=14320&sc=14340&sc=14360&sc=14400&sc=14380&cb=0.0&ct=9999999&mb=0&mt=9999999&et=9999999&cn=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sngz=&po1=09"
# requestで取得
r = requests.get(url)
soup = BeautifulSoup(r.text, 'lxml')

# 最大ページ
for page in range(int(soup.find_all(class_='pagination_set-nav')[0].find_all('li')[-1].text)):
    time.sleep()
    url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=14&sc=14101&sc=14102&sc=14103&sc=14104&sc=14105&sc=14106&sc=14107&sc=14108&sc=14109&sc=14110&sc=14111&sc=14112&sc=14113&sc=14114&sc=14115&sc=14116&sc=14117&sc=14118&sc=14131&sc=14132&sc=14133&sc=14134&sc=14135&sc=14136&sc=14137&sc=14151&sc=14152&sc=14153&sc=14201&sc=14203&sc=14204&sc=14205&sc=14206&sc=14207&sc=14208&sc=14210&sc=14211&sc=14212&sc=14213&sc=14214&sc=14215&sc=14216&sc=14217&sc=14218&sc=14300&sc=14320&sc=14340&sc=14360&sc=14400&sc=14380&cb=0.0&ct=9999999&mb=0&mt=9999999&et=9999999&cn=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sngz=&po1=09&page=2"

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

            info_list = [name, address, near_station, built_year, built_floors, floor,
                         rent_fee, manegement_fee, deposit, gratuity, layout, exclusive_area]
            info_lists.append(info_list)

    df_rent = pd.DataFrame(
        info_lists,
        columns=['name', 'address', 'near_station', 'built_year', 'built_floors', 'floor', 'rent_fee', 'manegement_fee',
                 'deposit', 'gratuity', 'layout', 'exclusive_area'])

    if page == 0:
        df = df_rent.copy()
    else:
        df = pd.concat([df, df_rent])

    if page % 10 == 0:
        df.to_csv('suumo.csv')
        break
