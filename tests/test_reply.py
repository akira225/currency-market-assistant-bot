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
USD:<i><u> Покупка</u> - 111.16
          <u>Продажа</u> - 132.67</i>
"""
            expected_reply2 = """Ответ на ваш запрос:

<b>Sberbank:</b>
EUR:<i><u> Покупка</u> - 119.03
          <u>Продажа</u> - 143.25</i>
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
CNY:<i><u> Покупка</u> - 16.66
          <u>Продажа</u> - 26.11</i>
"""
            expected_reply2 = """Ответ на ваш запрос:

<b>Vtb:</b>
GBP:<i><u> Покупка</u> - 131.95
          <u>Продажа</u> - 182.85</i>
<b>Vtb:</b>
EUR:<i><u> Покупка</u> - 120
          <u>Продажа</u> - 159.8</i>
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
<i><u>Доллар сша</u>:  Покупка - </i>111.16
<i>Продажа - </i>132.67
<i><u>Евро</u>:  Покупка - </i>119.03
<i>Продажа - </i>143.25

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
            message2 = "курс юаня"
            reply2 = util.construct_reply(message2)
            expected_reply1 = """Ответ на ваш запрос:

 <b>Фунт стерлингов Соединенного королевства</b> - <i>151.52 RUB</i>
 <b>Доллар США</b> - <i>115.2 RUB</i>
 <b>Евро</b> - <i>127.23 RUB</i>
 <b>Китайский юань</b> - <i>18.22 RUB</i>
100 <b>Японских иен</b> - <i>99.45 RUB</i>
"""
            expected_reply2 = """Ответ на ваш запрос:

 <b>Китайский юань</b> - <i>18.22 RUB</i> (-0.25)
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
