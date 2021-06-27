import unittest
from unittest.mock import patch
import util


class TestReply(unittest.TestCase):

    def test_reply_city_bank_currency(self):
        with patch('util.requests.get') as mocked_get:
            mocked_get.return_value.encoding = "utf-8"
            html = open("moskva_sberbank.html", "r", encoding="utf-8")
            text = html.read()
            html.close()
            mocked_get.return_value.text = text
            message1 = "курс доллара в сбербанке в москве"
            reply1 = util.construct_reply(message1)
            message2 = "курс евро в сбербанке в москве"
            reply2 = util.construct_reply(message2)
            mocked_get.assert_called()
            expected_reply1 = """Ответ на ваш запрос:

<b>Sberbank:</b>
USD:<i><u> Покупка</u> - 70.36
          <u>Продажа</u> - 74.09</i>
"""
            expected_reply2 = """Ответ на ваш запрос:

<b>Sberbank:</b>
EUR:<i><u> Покупка</u> - 84.18
          <u>Продажа</u> - 88.19</i>
"""
            self.assertEqual(reply1, expected_reply1)
            self.assertEqual(reply2, expected_reply2)

    def test_reply_city_bank_currency2(self):
        with patch('util.requests.get') as mocked_get:
            mocked_get.return_value.encoding = "utf-8"
            html = open("spb_vtb.html", "r", encoding="utf-8")
            text = html.read()
            html.close()
            mocked_get.return_value.text = text
            message1 = "spb vtb cny"
            reply1 = util.construct_reply(message1)
            message2 = "петербург банк втб курс фунта и евро"
            reply2 = util.construct_reply(message2)
            mocked_get.assert_called()
            expected_reply1 = """Ответ на ваш запрос:

<b>Vtb:</b>
CNY:<i><u> Покупка</u> - 10.84
          <u>Продажа</u> - 11.52</i>
"""
            expected_reply2 = """Ответ на ваш запрос:

<b>Vtb:</b>
GBP:<i><u> Покупка</u> - 97.35
          <u>Продажа</u> - 103.5</i>
<b>Vtb:</b>
EUR:<i><u> Покупка</u> - 84.35
          <u>Продажа</u> - 88</i>
"""
            self.assertEqual(reply1, expected_reply1)
            self.assertEqual(reply2, expected_reply2)

    def test_reply_city_bank(self):
        with patch('util.requests.get') as mocked_get:
            mocked_get.return_value.encoding = "utf-8"
            html = open("moskva_sberbank.html", "r", encoding="utf-8")
            text = html.read()
            html.close()
            mocked_get.return_value.text = text
            message = "курсы валют в сбербанке москва"
            reply = util.construct_reply(message)
            mocked_get.assert_called()
            expected_reply = """Ответ на ваш запрос:

<b>Sberbank:</b>
<i><u>Доллар сша</u>:  Покупка - </i>70.36
<i>Продажа - </i>74.09
<i><u>Евро</u>:  Покупка - </i>84.18
<i>Продажа - </i>88.19
<i><u>Фунт стерлингов</u>:  Покупка - </i>96.11
<i>Продажа - </i>104.44
<i><u>Белорусский рубль</u>:  Покупка - </i>26
<i>Продажа - </i>32.26
<i><u>Казахстанский тенге</u>:  Покупка - </i>11.84
<i>Продажа - </i>23.39
<i><u>Швейцарский франк</u>:  Покупка - </i>75.68
<i>Продажа - </i>81.86
<i><u>Японская йена</u>:  Покупка - </i>62.4
<i>Продажа - </i>67.98

"""
            self.assertEqual(reply, expected_reply)

    def test_reply_cb_requests(self):
        with patch('util.requests.get') as mocked_get:
            json = open("cb.json", "r", encoding="utf-8")
            text = json.read()
            json.close()
            mocked_get.return_value.text = text
            message1 = "курс"
            reply1 = util.construct_reply(message1)
            mocked_get.assert_called()
            message2 = "курс иены"
            reply2 = util.construct_reply(message2)
            expected_reply1 = """Ответ на ваш запрос:

 <b>Фунт стерлингов Соединенного королевства</b> - <i>100.37 RUB</i>
 <b>Доллар США</b> - <i>72.17 RUB</i>
 <b>Евро</b> - <i>86.19 RUB</i>
 <b>Китайский юань</b> - <i>11.18 RUB</i>
100 <b>Японских иен</b> - <i>65.17 RUB</i>
"""
            expected_reply2 = """Ответ на ваш запрос:

100 <b>Японских иен</b> - <i>65.17 RUB</i> (-0.07)
"""

            self.assertEqual(reply1, expected_reply1)
            self.assertEqual(reply2, expected_reply2)

    def test_reply_incorrect_city(self):
        message1 = "курс доллара в мухосранске"
        reply1 = util.construct_reply(message1)
        message2 = "курс евро в городе липецк"
        reply2 = util.construct_reply(message2)
        expected_reply1 = """Ответ на ваш запрос:

Указанный город не поддерживается"""
        expected_reply2 = """Ответ на ваш запрос:

Указанный город не поддерживается"""

        self.assertEqual(reply1, expected_reply1)
        self.assertEqual(reply2, expected_reply2)

    def test_reply_cb_by_date(self):  # relies on central bank api
        message1 = "фунт стерлингов 01.01.1930"
        reply1 = util.construct_reply(message1)
        message2 = "курс 20.08.2029"
        reply2 = util.construct_reply(message2)
        message3 = "курс 05.05.2012"
        reply3 = util.construct_reply(message3)
        expected_reply1 = """Ответ на ваш запрос:

Некорректная дата"""
        expected_reply2 = """Ответ на ваш запрос:

Некорректная дата"""
        expected_reply3 = """Ответ на ваш запрос:

<i>05.05.2012:</i>
 <b>Фунт стерлингов соединенного королевства</b> - 47.87 RUB
 <b>Доллар сша</b> - 29.59 RUB
 <b>Евро</b> - 38.92 RUB
10 <b>Китайских юаней</b> - 46.93 RUB
100 <b>Японских иен</b> - 36.91 RUB
"""

        self.assertEqual(reply1, expected_reply1)
        self.assertEqual(reply2, expected_reply2)
        self.assertEqual(reply3, expected_reply3)
