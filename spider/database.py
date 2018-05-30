# coding=utf-8

import MySQLdb


def get_conn():
    conn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='douban', charset='utf8mb4')
    return conn


def add_movie(movie_id, title,
              types=[], actors=[],
              rating=5, score=0.0,
              release_date='1970-01-01',
              regions=[], url='', cover_url=''):
    if is_movie_exist(movie_id):
        return True

    if len(release_date) == 4:
        release_date += "-01-01"
    elif len(release_date) == 0:
        release_date = '1970-01-01'

    conn = get_conn()
    cursor = conn.cursor()
    sql = 'insert into movie (`id`, `title`, `types`, `actors`, `rating`,' \
          ' `score`, `release_date`, `regions`, `url`, `cover_url`)' \
          ' values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    data = [movie_id, title, ','.join(types), ','.join(actors),
            rating, score, release_date, ','.join(regions),
            url, cover_url]
    n = cursor.execute(sql, data)
    cursor.close()
    conn.autocommit(cursor)


def is_movie_exist(movie_id):
    conn = get_conn()
    cursor = conn.cursor()
    sql = 'select * from movie where id = %s'
    parmas = [movie_id]
    n = cursor.execute(sql, parmas)
    data = cursor.fetchall()
    cursor.close()
    if data:
        return True
    else:
        return False


def get_next_movie_id(movie_id):
    conn = get_conn()
    cursor = conn.cursor()
    sql = 'select * from movie where id > %s limit 1'
    params = [movie_id]
    n = cursor.execute(sql, params)
    data = cursor.fetchall()

    small_sql = "select count(*) from movie where id <= %s"
    n = cursor.execute(small_sql, params)
    small_data = cursor.fetchall()

    big_sql = "select count(*) from movie where id > %s"
    n = cursor.execute(big_sql, params)
    big_data = cursor.fetchall()

    cursor.close()
    if data:
        return data[0][0], small_data[0][0], big_data[0][0]
    else:
        return None, small_data[0][0], big_data[0][0]


def add_comment(comment_id=0, movie_id=0,
                user_id='', avatar='', user_name='',
                comment='', rating=1, comment_time='1970-01-01', votes=0):
    conn = get_conn()
    if is_comment_exist(comment_id, conn):
        return True
    cursor = conn.cursor()
    sql = 'insert into movie_comment (`id`, `movie_id`, `user_id`, `avatar`, `user_name`,' \
          ' `comment`, `rating`, `comment_time`, `votes`)' \
          ' values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
    data = [comment_id, movie_id, user_id, avatar,
            user_name, comment, rating, comment_time,
            votes]
    n = cursor.execute(sql, data)
    conn.autocommit(cursor)
    cursor.close()


def is_comment_exist(comment_id, conn=None):
    comment_id = int(comment_id)
    if not conn:
        conn = get_conn()
    cursor = conn.cursor()
    sql = 'select * from movie_comment where id = %s'
    parmas = [comment_id]
    n = cursor.execute(sql, parmas)
    data = cursor.fetchall()
    cursor.close()
    if data:
        return True
    else:
        return False


def get_comments(start, limit):
    conn = get_conn()
    cursor = conn.cursor()
    sql = 'select * from movie_comment order by id desc limit %s,%s'
    params = [start, limit]
    n = cursor.execute(sql, params)
    comment_data = cursor.fetchall()
    comments = []
    for item in comment_data:
        comments.append([item[5], item[6]])
    cursor.close()
    return comments


def get_bad_comments(start, limit):
    sql = 'select * from movie_comment where rating < 3 order by id desc limit %s,%s'
    return get_origin_comments(start, limit, sql)


def get_middle_comments(start, limit):
    sql = 'select * from movie_comment where rating = 3 order by id desc limit %s,%s'
    return get_origin_comments(start, limit, sql)


def get_good_comments(start, limit):
    sql = 'select * from movie_comment where rating > 3 order by id desc limit %s,%s'
    return get_origin_comments(start, limit, sql)


def get_origin_comments(start, limit, sql):
    conn = get_conn()
    cursor = conn.cursor()
    params = [start, limit]
    n = cursor.execute(sql, params)
    comment_data = cursor.fetchall()
    comments = []
    for item in comment_data:
        comments.append([item[5], item[6]])
    cursor.close()
    return comments


def test():
    print get_next_movie_id(1291976)


if __name__ == '__main__':
    test()
