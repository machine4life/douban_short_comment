import json


class Comment():
    def __init__(self, movie_id=0, title="", rating=1, comment=""):
        self.movie_id = movie_id
        self.title = title
        self.rating = rating
        self.comment = comment

    def __str__(self):
        return json.dumps({
            "rating": self.rating,
            "comment": self.comment,
            "movie_id": self.movie_id,
            "title": self.title
        })

    def load(self, json_data):
        data = json.loads(json_data)
        self.rating = data['rating']
        self.comment = data['comment']
        self.movie_id = data['movie_id']
        self.title = data['title']

    def save(self):
        f = open('comment', 'a')
        try:
            f.write(self.__str__() + "\n")
        except IndexError as e:
            pass
        except ValueError as e:
            pass
        finally:
            f.close()