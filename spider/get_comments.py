# coding=utf-8
import json
import random
import threading
import time

import Queue
import requests
from bs4 import BeautifulSoup

from spider.database import add_comment, get_next_movie_id
from spider.util import refresh_cookie

queue = Queue.Queue(maxsize=70000)
lock = threading.Lock()


def get_res(session, url, trys=3):
    try:
        if trys < 0:
            return
        res = session.get(url)
        return res
    except requests.exceptions.ConnectionError as e:
        return get_res(session, url, trys - 1)


def get_movie_comment():
    with requests.Session() as session:
        while True:
            try:
                m_p = queue.get(block=False)
                movie_id = m_p[0]
                page = m_p[1]
            except Queue.Empty as e:
                return
            n = get_next_movie_id(movie_id)

            print "start get movie: %d, page: %d, 已完成：百分之 %f" % (movie_id, page, n[1] * 100.0 / (n[2] + n[1]))

            for i in range(page, 11):
                random_refresh_cookie(session)
                time.sleep(0.3)
                # print "get movie : %d, page : %d" % (movie_id, i)
                url = get_comment_url(movie_id, i)

                res = get_res(session, url)

                if not res:
                    print "res get error:" + url
                    continue

                if res.status_code != 200:
                    print "Error: url: %s. code: %d" % (url, res.status_code)
                    refresh_cookie(session)
                    continue

                soup = BeautifulSoup(res.text, 'html.parser')

                comments = soup.find_all("div", class_="comment-item")

                if not comments:
                    # comment for this one is over
                    set_comment_ckpt(movie_id, i)
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

                    cid = comment['data-cid']

                    div_avatar = comment.find('div', class_='avatar')
                    avatar_a = div_avatar.find('a')
                    avatar_img = avatar_a.find('img')

                    user_avatar = avatar_img['src']
                    user_name = avatar_a['title']
                    user_location = avatar_a['href']
                    user_id = user_location[30:]
                    user_id = user_id[:-1]

                    span_comment_time = comment.find('span', class_='comment-time')
                    comment_time = span_comment_time['title']

                    span_votes = comment.find('span', class_='votes')
                    votes = span_votes.get_text()

                    lock.acquire()
                    add_comment(cid, movie_id,
                                user_id, user_avatar,
                                user_name, comment_content,
                                rating_num, comment_time, votes)
                    lock.release()

                set_comment_ckpt(movie_id, i)


def init_threading():
    count = 1
    time.sleep(2)
    print "init thread,count: %d" % count
    for i in range(0, count):
        threading.Thread(target=get_movie_comment).start()


def start():
    movie_id, page = get_comment_ckpt()
    print "start at movie_id:%d, page:%d" % (movie_id, page)
    if movie_id == 0:
        movie_id = get_next_movie_id(movie_id)

    if not movie_id:
        return

    first_in = True

    while True:
        if not movie_id:
            return

        if not first_in:
            page = 0
        else:
            first_in = False

        queue.put([movie_id, page])
        # get_movie_comment(session, movie_id, page)

        movie_id, finish_count, last_count = get_next_movie_id(movie_id)
        # print "已经完成数量:%d， 剩余数量:%d， 已完成:百分之%f" % (finish_count, last_count, finish_count * 100.0 / last_count)


def random_refresh_cookie(session):
    if random.randint(0, 30) == 1:
        refresh_cookie(session)


def get_comment_ckpt():
    try:
        with open('comment_checkpoint', 'r') as f:
            content = f.read()
            if not content:
                return 0, 0
            else:
                data = json.loads(content)
                return data['movie_id'], data['page']
    except IOError as e:
        return 0, 0


def set_comment_ckpt(movie_id, page):
    with open('comment_checkpoint', 'w') as f:
        f.write(json.dumps({
            "movie_id": movie_id,
            "page": page
        }))
        f.close()


def get_comment_url(movie_id, page):
    url = "https://movie.douban.com/subject/" + str(movie_id) + "/comments?start=" +\
          str(page * 20) + "&limit=20&sort=new_score&status=P"
    return url


def main():
    threading.Thread(target=init_threading).start()
    start()


if __name__ == '__main__':
    main()
