import json


class Movie():

    def __init__(self, title="", url="", id='0'):
        self.title = title
        self.url = url
        self.id = str(id)

    def __str__(self):
        return json.dumps({
            "title": self.title,
            "url": self.url,
            "id": self.id
        })

    def load(self, json_data):
        data = json.loads(json_data)
        self.title = data['title']
        self.url = data['url']
        self.id = data['id']

    def save(self):
        f = open('movies', 'a')
        try:
            f.write(self.__str__() + "\n")
        except IndexError as e:
            pass
        except ValueError as e:
            pass
        finally:
            f.close()