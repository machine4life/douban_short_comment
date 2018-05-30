# coding=utf-8
import json
import random
import time

import requests

from spider.database import add_movie
from spider.util import refresh_cookie


def start(session):
    movie_type, interval, page = get_movie_ckpt()

    print "Start at: type[%d], interval[%d], page[%d]" % (movie_type, interval, page)

    first_in_interval = True
    first_in_page = True
    for m_type in range(movie_type, 32):
        if m_type == 9 or m_type == 21:
            continue

        if not first_in_interval:
            interval = 0
        else:
            first_in_interval = False

        for i in range(interval, 100, 10):

            if not first_in_page:
                page = 0
            else:
                first_in_page = False

            while True:
                time.sleep(0.3)
                c_url = get_json_url(m_type, i, page)
                data = session.get(c_url)
                if data.status_code != 200:
                    print "Error: url: %s. code: %d" % (c_url,  data.status_code)
                    refresh_cookie(session)
                    continue
                else:
                    res = json.loads(data.text)

                    if not res:
                        break

                    for item in res:
                        movie_id = item['id']
                        title = item['title']
                        types = item['types']
                        actors = item['actors']
                        if len(item['rating']) == 2:
                            rating = int(item['rating'][1]) / 10
                        else:
                            rating = 0
                        score = float(item['score'])
                        if "release_date" in item:
                            release_date = item['release_date']
                        else:
                            release_date = '1970-01-01'
                        regions = item['regions']
                        url = item['url']
                        cover_url = item['cover_url']
                        add_movie(movie_id, title, types, actors, rating, score, release_date, regions, url, cover_url)

                    print "current at type[%d], interval[%d], page[%d]" % (m_type, i, page)
                    set_movie_ckpt(m_type, i, page)
                random_refresh_cookie(session)
                page += 1


def random_refresh_cookie(session):
    if random.randint(0, 13) == 1:
        refresh_cookie(session)


def get_movie_ckpt():
    try:
        with open('movie_checkpoint', 'r') as f:
            content = f.read()
            if not content:
                return 1, 0, 0
            data = json.loads(content)
            if data:
                return data['movie_type'], data['interval'], data['page']
            else:
                return 1, 0, 0
    except IOError as e:
        return 1, 0, 0


def set_movie_ckpt(movie_type, interval=0, page=0):
    """
    保存movie 检查点
    :param movie_type:
    :param interval: 0 表示 0-10，最大为90
    :param page:
    :return:
    """
    with open('movie_checkpoint', 'w') as f:
        f.write(json.dumps({
            "movie_type": movie_type,
            "interval": interval,
            "page": page
        }))
        f.close()


def get_json_url(movie_type, interval, page):
    return "https://movie.douban.com/j/chart/top_list?type=" + str(movie_type) \
           + "&interval_id=" + str(interval) + "%3A" + str(interval - 10) + \
           "&action=&start=" + str(page * 20) + "&limit=20"


def main():
    with requests.Session() as session:
        refresh_cookie(session)
        start(session)


if __name__ == '__main__':
    main()
