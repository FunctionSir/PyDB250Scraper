#!/bin/python3
"""
Author: FunctionSir
License: AGPLv3
Date: 2024-03-11 20:18:57
LastEditTime: 2024-03-20 19:29:15
LastEditors: FunctionSir
Description: Get Douban TOP 250 and save to a TSV file.
FilePath: /PyDB250Scraper/doubantop250.py
"""

import requests
from time import sleep
from lxml import etree

"""
### README ###
Output will be a TSV file.
Option MODE is mode to open the file.
Use "w" to overwrite, use "a" to append.
Option GAP is secs to sleep between two requests.
"""

# BASIC CONFIG #
OUTPUT = "/home/funcsir/output.tsv"
MODE = "w"
VERBOSE = False
DEBUG = False
GAP = 0
BEGIN = 0
END = 10

# BASIC CONSTANTS #
BASE = 25
URL_BASE = "https://movie.douban.com/top250?start="

# UAS FROM JB51.NET #
UA = [
    "User-Agent,Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
    "User-Agent,Mozilla/5.0 (Windows NT 6.1; rv,2.0.1) Gecko/20100101 Firefox/4.0.1",
    "User-Agent,Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "User-Agent,Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "User-Agent,Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "User-Agent,Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/20.0.019; Profile/MIDP-2.1 Configuration/CLDC-1.1) AppleWebKit/525 (KHTML, like Gecko) BrowserNG/7.1.18124"
]


# MOVIE CLASS #
class Movie:
    def __init__(self) -> None:
        self.title = ""
        self.other = ""
        self.directors = ""
        self.actors = ""
        self.year = ""
        self.country = ""
        self.category = ""
        self.rating = ""


# LIST TO STRING #
def list_to_str(l: list, sp: str) -> str:
    r = ""
    for i in range(0, len(l)):
        if (i+1 < len(l)):
            r += l[i].strip()+sp
        else:
            r += l[i].strip()
    return r


# BATCH STRIP #
def batch_strip(l: list) -> list:
    for i in range(0, len(l)):
        l[i] = l[i].strip()
    return l


# BATCH BRACKETS TIDY #
def batch_brackets_tidy(l: list) -> list:
    for i in range(0, len(l)):
        l[i] = l[i].replace('（', '(')
        l[i] = l[i].replace('）', ')')
    return l


# PROCESSOR OF TITLE AND OTHER #
def title_other_processor(l: list, sp: str) -> str:
    r = ""
    tmpList = []
    for i in l:
        tmp = i
        while (len(tmp) >= 1 and (tmp[0] == '\xa0' or tmp[0] == ' ' or tmp[0] == '/')):
            tmp = tmp[1:]
        if (len(sp)):
            splited = tmp.split(sp)
            for e in splited:
                while (len(e) >= 1 and (e[0] == '\xa0' or e[0] == ' ' or e[0] == '/')):
                    e = e[1:]
                while (len(e) >= 1 and e[-1] == ' '):
                    e = e[:-1]
                tmpList.append(e)
        else:
            tmpList.append(tmp)
    r = list_to_str(tmpList, "/")
    return r


# PROCESSOR OF BD #
def bd_processor(l: list) -> tuple[str, str, str, str, str]:
    rDirectors = ""
    rActors = ""
    rYear = ""
    rCountry = ""
    rCategory = ""
    tmpA = l[0].strip()
    tmpB = l[1].strip()
    splitedFirst = tmpA.split("\xa0\xa0\xa0")
    splitedSecond = tmpB.split("\xa0/\xa0")
    tDirectors = batch_strip(splitedFirst[0].split("导演: ")[1].split("/"))
    if len(splitedFirst) == 1 or len(splitedFirst[1].split("主演: ")) == 1:
        tActors = ["..."]
    else:
        tActors = batch_strip(splitedFirst[1].split("主演: ")[1].split("/"))
    rDirectors = list_to_str(tDirectors, "/")
    rActors = list_to_str(tActors, "/")
    rYear = splitedSecond[0]
    rCountry = list_to_str(splitedSecond[1].split(" "), "/")
    rCategory = list_to_str(splitedSecond[2].split(" "), "/")
    return (rDirectors, rActors, rYear, rCountry, rCategory)


# MAKE TSV LINE #
def mk_tsv_line(m: Movie) -> str:
    r = ""
    r += m.title+"\t"
    r += m.other+"\t"
    r += m.directors+"\t"
    r += m.actors+"\t"
    r += m.year+"\t"
    r += m.country+"\t"
    r += m.category+"\t"
    r += m.rating+"\n"
    return r


# TSV LINE LIST #
tsvLines = []

# FIRST LINE OF THE TSV FILE #
tsvLines.append(
    "title\tother\tdirectors\tactors\tyear\tcountry\tcategory\trating\n")

# CHECK OUTPUT FILE PATH #
if (len(OUTPUT) < 1):
    print("! YOU SHOULD CONFIG THE PATH OF THE OUTPUT FILE FIRST !")
    exit(1)

# MAIN LOOP #
for i in range(BEGIN, END+1):
    url = URL_BASE+str(i*BASE)
    ua = UA[i % len(UA)]
    headers = {"User-Agent": ua}
    resp = requests.get(url, headers=headers)
    html = etree.HTML(resp.text)

    if VERBOSE:
        print("Requested URL: "+url)
        print("Used UA: "+ua)
        print("Got HTTP Status Code: "+str(resp.status_code))

    # PROCESS EACH ENTRY #
    resultInfo = html.xpath("//div[@class='info']")
    for r in resultInfo:
        movie = Movie()
        resultTitle = r.xpath(
            "./div[@class='hd']/descendant::span[@class='title']/text()")
        resultOther = r.xpath(
            "./div[@class='hd']/descendant::span[@class='other']/text()")
        resultBd = r.xpath(
            "./div[@class='bd']/descendant::p[@class='']/text()")
        resultRating = r.xpath(
            "./div[@class='bd']/div[@class='star']/descendant::span[@class='rating_num']/text()")
        # PROCESS TITLE #
        movie.title = title_other_processor(resultTitle, "")
        # PROCESS OTHER #
        movie.other = title_other_processor(resultOther, "/")
        # PROCESS BD#
        processedBd = bd_processor(resultBd)
        movie.directors = processedBd[0]
        movie.actors = processedBd[1]
        movie.year = list_to_str(batch_brackets_tidy(
            batch_strip(processedBd[2].split("/"))), "/")
        movie.country = processedBd[3]
        movie.category = processedBd[4]
        # PROCESS RATING #
        movie.rating = resultRating[0]
        # MAKE TSV LINE AND APPEND TO LINE LIST #
        tsvLines.append(mk_tsv_line(movie))

    # DEBUG SWITCH PROCESSOR #
    if DEBUG:
        input("Press Enter to continue...")
    else:
        sleep(GAP)

# OPEN FILE AND WRITE TSV LINES TO FILE #
file = open(OUTPUT, MODE)
file.writelines(tsvLines)

# DONE NOTICE #
print("Done!")
