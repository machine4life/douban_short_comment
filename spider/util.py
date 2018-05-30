# coding=utf-8
import random
import string

from spider.util_fetch import make_random_useragent

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"
headers = {'User-Agent': user_agent, "Upgrade-Insecure-Requests": str(1),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, sdch",
                "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
                "Cache-Control": "no-cache"}


def refresh_cookie(session):
    session.headers.clear()
    session.cookies.clear()
    session.headers = {
        "User-Agent": make_random_useragent("pc"),
        "Host": "movie.douban.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Accept-Language": "zh-CN, zh; q=0.8, en; q=0.6",
        "Cookie": "bid=%s" % "".join(random.sample(string.ascii_letters + string.digits, 11))
    }

    # data = session.get("https://accounts.douban.com/login")
    #
    # if data.status_code != 200:
    #     print "获取新cookie失败: " + str(data.status_code)
    # else:
    #     print "重新获取 cookie 成功"

    # session.headers['Host'] = "movie.douban.com"

    return 200


def sort_by_value(all_data):
    a = sorted(all_data.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
    return a
