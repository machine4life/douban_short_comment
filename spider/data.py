# encoding=utf-8
import json
import random
import time

import requests
from bs4 import BeautifulSoup

from comment import Comment
from movie import Movie
from spider.util_fetch import make_random_useragent

movies = []

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"
headers = {'User-Agent': user_agent, "Upgrade-Insecure-Requests": str(1),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, sdch",
                "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
                "Cache-Control": "no-cache"}


def main():

    if login() == 200:
        print "login success"
    else:
        print "login error"
        return

    # read movie page checkpoint
    get_movie_checkpoint()
    # get movies
    # if len(movies) < 300:
    #     get_movies(movie_checkpoint)

    # read move comment checkpoint
    movie_index, page = get_comment_checkpoint()
    # get movie comments
    get_comments(movie_index, page)


def login(load=True):
    session.headers.clear()
    session.cookies.clear()
    session.headers = {
        "User-Agent": make_random_useragent("pc"),
        "Host": "accounts.douban.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Accept-Language": "zh-CN, zh; q=0.8, en; q=0.6",
        # "Cookie": "bid=%s" % "".join(random.sample(string.ascii_letters + string.digits, 11))
    }

    data = session.get("https://accounts.douban.com/login")

    if data.status_code != 200:
        print "获取新cookie失败: " + str(data.status_code)
    else:
        print "重新获取 cookie 成功"

    session.headers['Host'] = "movie.douban.com"

    return 200

    # load cookie
    # if load:
    #     try:
    #         with open('login_cookie', 'r') as f:
    #             json_cookie = f.read()
    #     except IOError as e:
    #         json_cookie = {}
    #
    #     if json_cookie:
    #         session.cookies = requests.utils.cookiejar_from_dict(json.loads(json_cookie))
    #         return 200
    #
    # url = "https://accounts.douban.com/login"
    # res = session.get(url, headers=headers)
    # soup = BeautifulSoup(res.text, "html.parser")
    # img = soup.find("img", id="captcha_image")
    # ele_input = soup.find("input", attrs={"name": "captcha-id"})
    #
    # login_url = "https://accounts.douban.com/login"
    # phone, password = "18810278575", "Xiang2491147"
    # data = {
    #     "source": "movie",
    #     "redir": "https://movie.douban.com",
    #     "form_email": phone,
    #     "form_password": password
    # }
    #
    # if img:
    #     print "captcha-id: %s" % ele_input['value']
    #     print "have code verify, url:"
    #     print img['src']
    #     verify_code = raw_input("input verify code:")
    #     data['captcha-solution'] = verify_code
    #     data['captcha-id'] = ele_input['value']
    #
    # login_data = session.post(url=login_url, data=data, headers=headers)
    #
    # data_cookie = requests.utils.dict_from_cookiejar(session.cookies)
    # print data_cookie

    # try:
    #     with open('login_cookie', 'w') as f:
    #         f.write(json.dumps(data_cookie))
    # except IOError as e:
    #     pass
    #
    # return login_data.status_code


def get_movies(index):

    limit = 20
    for i in range(index, 15):
        print "index : %d" % int(index)
        set_movie_checkpoint(i)
        page_start = int(index) * 20
        json_url = "https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&sort=recommend&page_limit=" + str(limit) + "&page_start=" + str(page_start)

        res = session.get(json_url, headers=headers)
        data = json.loads(res.text)
        subjects = data['subjects']

        for m in subjects:
            movie = Movie(m['title'], m['url'], m['id'])
            save_movie(movie)

        time.sleep(0.5)
        index += 1


def get_comment_html(url, trys):
    if trys == 0:
        return None

    data = session.get(url)

    if random.randint(0, 10) == 1:
        # 更换 cookie
        login()

    if data.status_code != 200:
        print "要被封了，快清除cookie重试:" + str(data.status_code)
        print session.headers
        print session.cookies
        session.cookies.clear()
        login(False)
        return get_comment_html(url, trys-1)
    else:
        return data


def get_comments(movie_index, page):

    print "start form movie index %d. page %d. movie count : %d" % (movie_index, page, len(movies))

    first_in = True

    for i in range(movie_index, len(movies)):
        movie = movies[movie_index]

        if first_in:
            first_in = False
        else:
            page = 0

        for p in range(page, 11):
            print "waiting for index:%d, page: %d" % (i, p)
            time.sleep(0.5)
            start = p * 20
            url = "https://movie.douban.com/subject/" + movie.id + "/comments?start=" + str(start) + "&limit=20&sort=new_score&status=P"
            data = get_comment_html(url, 3)

            if data is None:
                print "啊啊啊啊，又被封了"
                return

            soup = BeautifulSoup(data.text, 'html.parser')

            comments = soup.find_all("div", class_="comment-item")

            if not comments:
                # comment for this one is over
                set_comment_check_point(i+1, 0)
                break

            for comment in comments:
                rating = comment.find("span", class_="rating")
                if not rating:
                    continue
                rating_class = rating['class']
                rating_num = 1
                if "allstar10" in rating_class:
                    rating_num = 1
                if "allstar20" in rating_class:
                    rating_num = 2
                if "allstar30" in rating_class:
                    rating_num = 3
                if "allstar40" in rating_class:
                    rating_num = 4
                if "allstar50" in rating_class:
                    rating_num = 5

                comment_p = comment.find('p')
                comment_content = comment_p.get_text()

                c = Comment(movie.id, movie.title, int(rating_num), comment_content)
                c.save()

            set_comment_check_point(i, p)


def get_movie_checkpoint():
    # load movie
    try:
        with open('movies', 'r') as f:
            for line in f:
                m = Movie()
                m.load(line)
                movies.append(m)
            f.close()
            return
    except IOError as e:
        pass

    # get checkpoint
    try:
        with open('movie_checkpoint', 'r') as f:
            index = f.read()
            print "movie checkpoint : " + str(index)
            if not index:
                index = 0
            return int(index)
    except IOError as e:
        print "no movie checkpoint fount, start from page 0"
        return 0


def set_movie_checkpoint(index):
    with open('movie_checkpoint', 'w') as f:
        f.write(str(index))


def save_movie(movie):
    if movie.id not in movies:
        movies[movie.id] = movie
        movie.save()


def get_comment_checkpoint():
    try:
        with open("comment_checkpoint", 'r') as f:
            c = json.loads(f.read())
            return c['movie_index'], c['page']
    except IOError as e:
        return 0, 0
    except ValueError as e:
        return 0, 0


def set_comment_check_point(movie_index, page):
    with open('comment_checkpoint', 'w') as f:
        f.write(json.dumps({
            "movie_index": movie_index,
            "page": page
        }))


if __name__ == '__main__':
    with requests.Session() as session:
        main()
