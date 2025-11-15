import requests
from bs4 import BeautifulSoup
import re

def ouhe_hot_list():
    url = "http://ouhe.aiball365.com/"
    response = requests.get(url, proxies={"http": None},timeout=5)
    html = response.text
    print(html)
    # 提取热门的数据
    # html 的超链接规则: 
    # + class 中包含 hotmatch-detail-item 字段
    # + href 中包含  /match?id=任意字符&amp;i=任意字符
    # + 经过 soup 解析的正则需要改为: /match?id=任意字符&i=任意字符
    class_pattern = re.compile(r".*\bhotmatch-detail-item\b.*")
    href_pattern = re.compile(r"/match\?id=([^&]+)&i=([^&]+)")

    soup = BeautifulSoup(html, "html.parser")

    match_ids_set = set()

    for a_tag in soup.find_all("a", href=True, class_=class_pattern):
        href = a_tag["href"]
        match = href_pattern.search(href)
        if match:
            matchid = match.group(1)
            match_ids_set.add(matchid)  # 使用 set 自动去重

    return list(match_ids_set)

# bet365 亚盘数据
def ouhe_bet365_asia(matchid: str):
    bet365_cid = "38"
    return ouhe_asia(matchid, bet365_cid)

# williamhill 亚盘数据
def ouhe_williamhill_asia(matchid: str):
    williamhill_cid = "26"
    return ouhe_asia(matchid, williamhill_cid)

def ouhe_asia(matchid: str, cid: str):

    pass

def ouhe_bet365_euro(matchid: str):
    bet365_cid = "38"
    return ouhe_euro(matchid, bet365_cid)

def ouhe_williamhill_euro(matchid: str):
    williamhill_cid = "26"
    return ouhe_euro(matchid, williamhill_cid)

def ouhe_euro(matchid: str, cid: str):
    pass
# def ouhe_asia_odds(matchid: str):
# cid
# : 
# 38
# cname
# : 
# "Bet365"
# initBet
# : 
# "一球"
# initKelly0
# : 
# "0.90"
# initKelly3
# : 
# "1.00"
# initOddsDown
# : 
# "1.78"
# initOddsUp
# : 
# "2.03"
# initReturnRates
# : 
# "94.84"
# nowBet
# : 
# "一球/球半"
# nowKelly0
# : 
# "0.97"
# nowKelly3
# : 
# "0.93"
# nowOddsDown
# : 
# "1.98"
# nowOddsUp
# : 
# "1.83"
# nowReturnRates
# : 
# "95.10"
# prob0
# : 
# "48.03%"
# prob3
# : 
# "51.97%"
# OuHeAisaOdds