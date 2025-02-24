import os
import re
import time
import json
import sys
from tqdm import tqdm
import argparse
import requests
from bs4 import BeautifulSoup

pattern_link= re.compile(r'<a href="(.*?)">')
pattern_title = re.compile(r'<span class="title">(.*?)</span>')
pattern_imgsrc = re.compile(r'<img.*src="(.*?)"',re.S)
pattern_rating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
pattern_quote = re.compile(r'<span class="inq">(.*)</span>')
pattern_genre = re.compile(r'<br>([0-9]*)/(.*)</p>',re.S)

pattern_origin = re.compile(r'<span class="pl">制片国家/地区:</span>(.*?)<br/>')
pattren_language = re.compile(r'<span class="pl">语言:</span>(.*?)<br/>')

def index_soup():

    url = "https://www.douban.com"
    head = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0"}
    response = requests.get(url, headers=head)
    
    if not response.ok:
        print(f"url: {response.url}, statu: {response.status_code}")
        return
    
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find_all("title")[0].string.replace("\n","").replace(" ","")

    ## 电影
    movie_list = soup.find("div",attrs={"class":"movie-list list"})
    # print(f"{movie_list}")
    ## 电影信息
    pic_divs = movie_list.find_all("div", attrs={"class":"pic"})
    # print(f"{pic_divs}")
    movie_data = []
    for pic_div in pic_divs:
        movie = {}
        movie["title"] = pic_div.find("img").get("alt").strip()
        movie["hover"] = pic_div.find("img").get("data-origin").strip()
        movie["href"]  = pic_div.find("a", href=True).get("href").strip()
        res = requests.get(movie["href"], headers=head)
        movie_data.append(movie)
        print(f"{movie}")

    ## 电影评分
    rating_divs = movie_list.find_all("div",attrs={"class":"rating"})
    print(f"{rating_divs}")
    movie_ratings = []
    for rating_div in rating_divs:
        if rating_div.find("i"):
            movie_rating = rating_div.find("i").string
        else:
            movie_rating = rating_div.find("span").string
        movie_ratings.append(movie_rating)
        print(f"{movie_rating}")

    ## 书籍
    book_list = soup.find("div",attrs={"class":"book-list list"})
    print(f"{book_list}")
    ## 书籍标题
    pic_divs = book_list.find_all("div", attrs={"class":"pic"})
    print(f"{pic_divs}")
    book_titles = []
    for pic_div in pic_divs:
        book_title = pic_div.find("img").get("alt").strip()
        book_titles.append(book_title)
        print(f"{book_title}")
    ## 书籍作者 TODO:
    author_divs = book_list.find_all("div",attrs={"class":"author"})
    book_authors = []
    for author_div in author_divs:
        pass

def get_hrefs():
    ## 打开HTML，bs4库处理
    with open("豆瓣电影Top250.html",encoding="utf-8") as f:
        html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        hrefs = []
        divs = soup.find_all("div",attrs={"class":"pic"})
        for div in divs:
            href = div.find("a",href=True).get("href").strip()
            title = div.find("img").get("alt").strip()
            hrefs.append({"title":title,"href":href})
    ## 避免重复爬取
    # hrefs = list(set(hrefs))
    print(f"{hrefs}")
    ## 写入JSON数据
    try:
        with open("dubanMovieTop250.json","w", encoding="utf-8") as f:
            json.dump(hrefs, f, ensure_ascii=False, indent=2)
    except MemoryError as e:
        print(f"{e}")

def movie_soup(html):
    soup = BeautifulSoup(html, "html.parser")
    ## 标题
    title = soup.find("title").string.replace("\n", "").replace(" ", "").replace("(豆瓣)","")
    print(f"title:{title}")
    ## 封面
    mainpic = soup.find("div",attrs={"id":"mainpic"}).find("img").get("src").strip()
    print(f"mainpic:{mainpic}")
    ## 评分
    rating = soup.find("strong",property="v:average").string
    print(f"rating:{rating}")
    ## 信息
    info_div = soup.find("div", attrs={"id":"info"})
    ## 类型
    genre_spans = info_div.find_all("span",property="v:genre")
    genre = []
    for genre_span in genre_spans:
        genre.append(genre_span.string)
    print(f"genre:{genre}")
    ## 地区
    origin = pattern_origin.search(str(info_div)).group().replace("<span class=\"pl\">制片国家/地区:</span>","").replace("<br/>","").replace(" ","")
    print(f"origin:{origin}")
    ## 语言
    language = pattren_language.search(str(info_div)).group().replace("<span class=\"pl\">语言:</span>","").replace("<br/>","").replace(" ","")
    print(f"language:{language}")
    ## 时长
    runtime = info_div.find("span",property="v:runtime").get("content").strip()
    print(f"runtime:{runtime}")
    ## 写入数据
    data = {}
    data["title"] = title
    data["image"] = mainpic
    data["rating"] = rating
    data["genre"] = genre
    data["orgin"] = origin
    data["language"] = language
    data["runtime"] = runtime

    return data

def main():

    # with open("哪吒之魔童闹海.html", encoding="utf-8") as f:
    #     html = f.read()
    #     data = movie_soup(html)

    # try:
    #     with open("哪吒之魔童闹海.json", "r", encoding="utf-8") as datafile:
    #         existing_data = json.load(datafile)
    # except (FileNotFoundError, json.JSONDecodeError):
    #     existing_data = []

    # existing_data.append(data)

    # with open("哪吒之魔童闹海.json", "w", encoding="utf-8") as datafile:
    #     json.dump(existing_data, datafile, ensure_ascii=False, indent=2)

    head = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0"}
    
    try:
        with open("dubanMovieTop250.json","r",encoding="utf-8") as file:
            hrefs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        hrefs = []

    data = []
    for href in hrefs:
        try:
            url = href["href"]
            if os.path.exists(f"{href["title"]}.html"):
                print(f"URL - {url} - SKIP!")
                with open(f"{href["title"]}.html", "r", encoding="utf-8") as f:
                    html = f.read()
                    data.append(movie_soup(html))
            else:
                response = requests.get(url, headers=head, timeout=10)
                print(f"URL - {url} - {response.status_code}")
                html = response.text
                with open(f"{href["title"]}.html", "w", encoding="utf-8") as f:
                    f.write(html)
                    data.append(movie_soup(html))
                    time.sleep(2)
            
        except requests.RequestException as re:
            print(f"Requests Error:{re}")
        except KeyboardInterrupt:
            print(f"Quit!")
            sys.exit(0)
        except Exception as err:
            print(f"Error:{err}")
    
    with open("豆瓣电影Top250.json","w",encoding="utf-8") as datafile:
        json.dump(data, datafile, ensure_ascii=False, indent=2)

    # return data
        
if __name__ == '__main__':
    main()
    
