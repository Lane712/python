import os,sys,time,json,re
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tqdm import tqdm

# 编译正则表达式
PATTERN_ORIGIN = re.compile(r'<span class="pl">[\s]+制片国家/地区:[\s]+</span>\n(.*?)\n')
PATTERN_LANGUAGE = re.compile(r'<span class="pl">[\s]+语言:[\s]+</span>\n(.*?)\n')

def fetch_page(url):
    """抓取网页内容"""
    UA = UserAgent(os=['Windows','Linux'])
    HEADERS = {"User-Agent": UA.random}
    response = requests.get(url, headers=HEADERS)
    if response.ok:
        return response
    else:
        raise ConnectionError(f"Failed to fetch URL: {url}, status: {response.status_code}")

def prettify_html(html, title=None):
    """格式化并保存HTML文件"""
    soup = BeautifulSoup(html, "lxml")
    if not title:
        title = re.sub(r"\s+","", soup.find("title").string)
    new_html = soup.prettify()
    with open(f"./movie_htmls/{title}.html","w",encoding="utf-8") as file:
        file.write(new_html)

    return new_html

def parse_homepage(html):
    """解析豆瓣首页"""
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("title").string.strip().replace("豆瓣", "").strip()
    print(f"Page Title: {title}")

    # 解析电影信息（未补充）
    # movie_list = soup.find("div", attrs={"class": "movie-list list"})
    # ...

    return {}

def get_hrefs_from_html():
    """从 HTML 文件解析出电影链接"""
    hrefs = []
    with open("豆瓣电影Top250.html",encoding="utf-8") as f:
        html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        divs = soup.find_all("div",attrs={"class":"pic"})
        for div in divs:
            href = div.find("a",href=True).get("href").strip()
            title = div.find("img").get("alt").strip()
            hrefs.append({"title":title, "href":href})
    ## 写入JSON数据
    try:
        with open("豆瓣电影Top250.json","w", encoding="utf-8") as f:
            json.dump(hrefs, f, ensure_ascii=False, indent=2)
    except (MemoryError, json.JSONDecodeError) as e:
        print(f"JSON write error:{e}")

    return hrefs

def read_hrefs_from_json(filename="豆瓣电影Top250.json"):
    """从 JSON 文件读取电影链接"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def parse_movie_details(html):
    """解析电影详情页"""
    html = html.replace("<br/>","") # 删除特定字符
    soup = BeautifulSoup(html, "lxml")

    # 提取关键信息
    title = soup.find("title").string.replace(" (豆瓣)", "").strip()
    mainpic = soup.find("div", {"id": "mainpic"}).find("img")["src"].strip()
    rating = soup.find("strong", {"property": "v:average"}).string.strip()

    # 提取类型
    genres = []
    for span in soup.find_all("span", {"property": "v:genre"}):
        genres.append(re.sub(r"\s+","", span.string))

    ## 信息
    info_div = soup.find("div", attrs={"id":"info"})
    ## 地区
    origin = re.sub(r'<span class="pl">[\s]+制片国家/地区:[\s]+</span>[\s]+',"",PATTERN_ORIGIN.search(str(info_div)).group()).replace("\n","").replace(" ","")
    ## 语言
    language = re.sub(r'<span class="pl">[\s]+语言:[\s]+</span>[\s]+',"",PATTERN_LANGUAGE.search(str(info_div)).group()).replace("\n","").replace(" ","")

    # 提取时长
    runtime = soup.find("span", {"property": "v:runtime"})["content"].strip()

    # 提取简介
    summary_info= soup.find("div", attrs={"id":"link-report-intra"}).find("span", attrs={"class":"all hidden"})
    if summary_info is not None:
        summary = re.sub(r"\s+","", summary_info.string)
    else:
        summary_info = soup.find("div", attrs={"id":"link-report-intra"}).find("span", property ="v:summary")
        if summary_info is not None:
            ## r"\s" 匹配空白字符、换行符、制表符
            summary = re.sub(r"\s+","", summary_info.string)
            
    # 返回电影信息对象
    return {
        "title": title,
        "image": mainpic,
        "rating": rating,
        "genre": genres,
        "origin": origin,
        "language": language,
        "runtime": runtime,
        "summary": summary
    }

def update_movies_data(movies):
    try:
        # 读取数据
        with open("movies.json", "r", encoding="utf-8") as f:
            all_movies = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_movies = []
    # 合并数据
    for movie in movies:
        all_movies.append(movie)
    # 存储数据
    with open("movies.json", "w", encoding="utf-8") as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=2)

def main():
    # 读取电影链接
    hrefs = read_hrefs_from_json()

    if not os.path.exists("./movies.json"):
        with open("./movies.json","W",encoding="utf-8") as f:
            pass

    # 排除已处理的电影链接
    try:
        with open("movies.json", "r", encoding="utf-8") as f:
            processed_movies = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        processed_movies = []
    processed_urls = [movie['url'] for movie in processed_movies]

    # 移除已处理的链接
    fetched_hrefs = []
    for href in hrefs:
        if href['href'] not in processed_urls:
            fetched_hrefs.append(href)
            
    # 确保存放 HTML 的文件存在
    if not os.path.isdir("./movie_htmls"):
        os.makedirs("./movie_htmls")

    # 进度条显示
    with tqdm(total=len(fetched_hrefs), desc="FETCH MOVIE") as pbar:
        # 初始化数据存储
        fetched_movies = []
        # 遍历链接并解析详情页
        for href in fetched_hrefs:
            url = href["href"]
            title = href["title"]

            try:
                # 获取 HTML
                if os.path.exists(f"./movie_htmls/{title}.html"):
                    with open(f"./movie_htmls/{title}.html","r",encoding="utf-8") as file:
                        html = file.read()
                else:
                    time.sleep(3) # 请求延迟
                    res = fetch_page(url)
                    html = res.text
                    pbar.set_postfix(f"{res.status_code}")
                    # print(f"{res.headers}", file=sys.stderr) # 打印其他信息
                    # pbar.refresh()  # 手动刷新进度条
                    html = prettify_html(html, title)
            
                # 解析 HTML
                movie_data = parse_movie_details(html)
                movie_data['url'] = url
                fetched_movies.append(movie_data)
                pbar.update(1)
                
            except KeyboardInterrupt:
                update_movies_data(fetched_movies)
                pbar.close()
                print(f"Quit! Add {len(fetched_movies)} movies data.")
                sys.exit(0)
            except Exception as e:
                print(f"Error processing {url}: {str(e)}")
        pbar.close()

    # 存储数据
    update_movies_data(fetched_movies)

    print(f"Done! Add {len(fetched_movies)} movies data.")

if __name__ == '__main__':
    main()    main()
