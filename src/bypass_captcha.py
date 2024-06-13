import time
import requests
import base64


class Solve:
    def __init__(self, api, captcha):
        self.session = requests.session()
        self.captcha = captcha
        self.api = api
        self.url_post = 'http://api.captcha.guru/in.php'
        self.url_get = 'http://api.captcha.guru/res.php'

    def do_request_for_solve_captcha(self):
        with open(self.captcha, 'rb') as file:
            captcha_in_base64 = base64.b64encode(file.read()).decode()

        data = {
            'textinstructions': 'yandex',
            'click': 'oth',
            'key': self.api,
            'method': 'base64',
            'body': captcha_in_base64,
        }

        with self.session.post(url=self.url_post, data=data) as response:
            return response.text

    def get_coordinates(self):
        post_requests_for_solve_captcha = str(Solve.do_request_for_solve_captcha(self))
        time.sleep(15)
        data = {
            'key': self.api,
            'action': 'get',
            'id': post_requests_for_solve_captcha.split('|')[1],
            'json': 1
        }

        with self.session.get(url=self.url_get, params=data) as response:
            coordinates_name: list = ['x', 'y']
            list_of_coordinates: list = []
            try:
                for coordinates in response.json()['request'].split(':')[1].split(';'):
                    coordinates_dict = dict(zip(coordinates_name, [int(coordinate.split('=')[1]) for coordinate in coordinates.split(',')]))
                    list_of_coordinates.append(coordinates_dict)
                return list_of_coordinates
            except IndexError:
                self.catch_exceptions(response.text)

    @staticmethod
    def catch_exceptions(exception):
        if exception == 'ERROR_ZERO_BALANCE':
            print('На балансе не достаточно средств')

        elif exception == 'ERROR_CAPTCHA_UNSOLVABLE':
            print('Сервис не смог решить капчу')

        elif exception == 'CAPCHA_NOT_READY':
            print('Капча еще не решена')

        else:
            print(exception)

    def feed_back(self, id_of_captcha):
        pass
