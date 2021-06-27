import requests
import json
import datetime
import re
from data import *
from bs4 import BeautifulSoup


def get_cb_data(currency="usd"):
    currency = currency.upper()
    central_bank_url = "https://www.cbr-xml-daily.ru/daily_json.js"
    full_json_data = json.loads(requests.get(central_bank_url).text)
    currency_data = full_json_data.get("Valute")
    return currency_data[currency]


def web_scrap(city="moskva", bank="sberbank"):
    url = "https://" + city + ".bankiros.ru/bank/" + bank + "/currency"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    r = requests.get(url, headers=headers)
    r.encoding = "utf-8"
    text = r.text
    soup = BeautifulSoup(text, 'html.parser')
    lines = soup.find_all("tr", class_="productBank turn")
    table = list()
    for line in lines:
        line_parsed = list()
        for record in line:
            line_parsed.append(str(record.contents[0].contents[0]).lower())
        table.append(line_parsed)
    return table


def get_cb_data_date(date, currency="usd"):
    url = "https://cbr.ru/currency_base/daily/?UniDbQuery.Posted=True&UniDbQuery.To=" + date
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    r = requests.get(url, headers=headers)
    # r.encoding = "utf-8"
    text = r.text
    soup = BeautifulSoup(text, 'html.parser')
    lines = soup.find_all("tr")
    del lines[0]
    table = list()
    for line in lines:
        line = line.find_all("td")
        line_parsed = list()
        for record in line:
            line_parsed.append(str(record.contents[0]).lower().replace(",", "."))
        table.append(line_parsed)
    for line in table:
        if line[1] == currency:
            return line
    return None


def validate_date(date_str):
    date_constraint = datetime.date(1992, 7, 1)
    date_today = datetime.date.today()
    tmp = date_str.split(".")
    date_provided = datetime.date(int(tmp[-1]), int(tmp[1]), int(tmp[0]))
    if date_provided < date_constraint or date_provided > date_today:
        return False
    else:
        return True


def construct_reply(text):
    banks_provided = list()
    region_provided = None
    currencies_provided = list()
    currencies_provided_eng = list()
    date_provided = re.search(
        r"(?<!\d)(?:0?[1-9]|[12][0-9]|3[01]).(?:0?[1-9]|1[0-2]).(?:19[0-9][0-9]|20[012][0-9])(?!\d)", text)
    if date_provided is not None:
        date_provided = date_provided[0]
    for cur in currencies_rus:
        if text.find(cur) > -1:
            currencies_provided.append(cur)
    if len(currencies_provided) < 1:
        for cur in currencies_eng:
            if text.find(cur) > -1:
                currencies_provided_eng.append(cur)
    for city in cities_rus:
        if text.find(city) > -1:
            region_provided = cities_dict[city]
            break
    if region_provided is None:
        for city in cities_eng:
            if text.find(city) > -1:
                region_provided = city
                break
    for bank in banks_rus:
        if text.find(bank) > -1:
            banks_provided.append(banks_dict[bank])
    if len(banks_provided) < 1:
        for bank in banks_eng:
            if text.find(bank) > -1:
                banks_provided.append(bank)
    msg_response = "Ответ на ваш запрос:\n\n"
    if region_provided is None and (text.find("в городе") > -1 or text.find("курс") > -1 and text.find(" в ") > -1):
        msg_response = msg_response + "Указанный город не поддерживается"
        return msg_response
    if len(banks_provided) < 1 and region_provided is None and len(currencies_provided) < 1 and len(
            currencies_provided_eng) < 1 and date_provided is None:
        if text.find("курс") > -1 or text.find("валют") > -1 or text.find("сводк") > -1 or text.find("kurs") > -1:
            for currency in currencies_eng:
                data = get_cb_data(currency)
                if data is not None:
                    msg_response = msg_response + (str(data["Nominal"]) if data["Nominal"] > 1 else "") + " <b>" + \
                                   data["Name"] + "</b> - <i>" + str(round(data["Value"], 2)) + " RUB</i>\n"
        else:
            msg_response = msg_response + "<b>Неправильный запрос</b>\n\n" + \
                           "Для получения информации используйте одну из следующих команд:\n<i>/help\n/помощь</i>"
    if len(banks_provided) < 1 and region_provided is None and len(currencies_provided) < 1 and len(
            currencies_provided_eng) < 1 and date_provided is not None:
        if not validate_date(date_provided):
            msg_response = msg_response + "Некорректная дата"
            return msg_response
        if text.find("курс") > -1 or text.find("валют") > -1 or text.find("сводк") > -1 or text.find(
                "kurs") > -1 or text.find("data") > -1 or text.find("данные") > -1:
            msg_response = msg_response + "<i>" + date_provided + ":</i>\n"
            for currency in currencies_eng:
                data = get_cb_data_date(date_provided, currency)
                if data is not None:
                    msg_response = msg_response + (data[2] if int(data[2]) > 1 else "") + " <b>" + \
                                   data[3].capitalize() + "</b> - " + str(round(float(data[-1]), 2)) + " RUB\n"
        else:
            msg_response = msg_response + "<b>Неправильный запрос</b>\n\n" + \
                           "Для получения информации используйте одну из следующих команд:\n<i>/help\n/помощь</i>"
    if len(banks_provided) > 0 and region_provided is not None and (
            len(currencies_provided) > 0 or len(currencies_provided_eng) > 0):
        local_response = ""
        if len(currencies_provided) < 1:
            for cur in currencies_provided_eng:
                currencies_provided.append(currencies_dict_reverse[cur])
        for currency in currencies_provided:
            for bank in banks_provided:
                data = web_scrap(region_provided, bank)
                for line in data:
                    if line[0].find(currency) > -1:
                        local_response = local_response + "<b>" + bank.capitalize() + ":</b>\n" + \
                                         currencies_dict[currency].upper() + ":<i><u> Покупка</u> - " + line[1] + \
                                         "\n          <u>Продажа</u> - " + line[2] + "</i>\n"
        if len(local_response) > 0:
            msg_response = msg_response + local_response
        else:
            msg_response = msg_response + "Выбранные банки не поддерживают запрошенные валюты"

    if len(banks_provided) < 1 and region_provided is None and (
            len(currencies_provided) > 0 or len(currencies_provided_eng) > 0) and date_provided is None:
        if len(currencies_provided) > 0:
            for currency in currencies_provided:
                currencies_provided_eng.append(currencies_dict[currency])
        for currency in currencies_provided_eng:
            data = get_cb_data(currency)
            if data is not None:
                diff = data["Value"] - data["Previous"]
                msg_response = msg_response + (str(data["Nominal"]) if data["Nominal"] > 1 else "") + " <b>" + \
                               data["Name"] + "</b> - <i>" + str(round(data["Value"], 2)) + " RUB</i>" + \
                               " (" + ("+" if diff > 0 else "") + str(round(diff, 2)) + ")\n"
    if len(banks_provided) < 1 and region_provided is None and (
            len(currencies_provided) > 0 or len(currencies_provided_eng) > 0) and date_provided is not None:
        if not validate_date(date_provided):
            msg_response = msg_response + "Некорректная дата"
            return msg_response
        if len(currencies_provided) > 0:
            for currency in currencies_provided:
                currencies_provided_eng.append(currencies_dict[currency])
        msg_response = msg_response + date_provided + ":\n"
        for currency in currencies_provided_eng:
            data = get_cb_data_date(date_provided, currency)
            if data is not None:
                msg_response = msg_response + "<b>" + data[3].capitalize() + "</b> -  <i>" + str(
                    round(float(data[-1]), 2)) + " RUB</i>\n"

    if region_provided is not None and len(banks_provided) < 1 and len(currencies_provided) < 1 and len(
            currencies_provided_eng) < 1:
        msg_response = msg_response + "<b>Неправильный запрос</b>\n\n" + \
                       "Для получения информации используйте одну из следующих команд:\n<i>/help\n/помощь</i>"
    if region_provided is None and len(banks_provided) > 0 and len(currencies_provided) < 1 and len(
            currencies_provided_eng) < 1:
        if len(banks_provided) == 1:
            msg_response = msg_response + "<b>" + banks_provided[0].capitalize() + ":</b>\n"
            data = web_scrap("moskva", banks_provided[0])
            for line in data:
                msg_response = msg_response + "<i><u>" + line[0].capitalize() + "</u>:  Покупка - </i>" + line[1] + \
                               "\n<i>Продажа - </i>" + line[2] + "\n"
        else:
            msg_response = msg_response + "<b>Неправильный запрос</b>\n\n" + \
                           "Для получения информации используйте одну из следующих команд:\n<i>/help\n/помощь</i>"
    if region_provided is not None and len(banks_provided) > 0 and len(currencies_provided) < 1 and len(
            currencies_provided_eng) < 1:
        for bank in banks_provided:
            msg_response = msg_response + "<b>" + bank.capitalize() + ":</b>\n"
            data = web_scrap(region_provided, bank)
            for line in data:
                msg_response = msg_response + "<i><u>" + line[0].capitalize() + "</u>:  Покупка - </i>" + line[1] + \
                               "\n<i>Продажа - </i>" + line[2] + "\n"
            msg_response = msg_response + "\n"
    if region_provided is None and len(banks_provided) > 0 and (
            len(currencies_provided) > 0 or len(currencies_provided_eng) > 0):
        if len(currencies_provided_eng) > 0:
            for cur in currencies_provided_eng:
                currencies_provided.append(currencies_dict_reverse[cur])
        for currency in currencies_provided:
            msg_response = msg_response + "<u>" + currencies_dict[currency].upper() + "</u>:\n"
            for bank in banks_provided:
                msg_response = msg_response + "<b>" + bank.capitalize() + ":</b>  "
                data = web_scrap("moskva", bank)
                local_response = ""
                for line in data:
                    if line[0].find(currency) > -1:
                        local_response = "<i>Покупка - </i>" + line[1] + "\n<i>Продажа - </i>" + line[2] + "\n"
                if len(local_response) < 1:
                    msg_response = msg_response + "\n Данный банк не поддерживает выбранную валюту\n"
                else:
                    msg_response = msg_response + local_response
            msg_response = msg_response + "\n"
    if region_provided is not None and len(banks_provided) < 1 and (
            len(currencies_provided) > 0 or len(currencies_provided_eng) > 0):
        if len(currencies_provided_eng) > 0:
            for cur in currencies_provided_eng:
                currencies_provided.append(currencies_dict_reverse[cur])
        for currency in currencies_provided:
            msg_response = msg_response + "<u><b>" + currencies_dict[currency].upper() + ":</b></u>\n"
            max_buy = 0.0
            min_sell = 999.9
            record_list = list()
            for bank in banks_eng:
                data = web_scrap(region_provided, bank)
                for line in data:
                    if line[0].find(currency) > - 1:
                        line.append(bank)
                        record_list.append(line)
                        if float(line[1]) > max_buy:
                            max_buy = float(line[1])
                        if float(line[2]) < min_sell:
                            min_sell = float(line[2])
            local_response = ""
            for record in record_list:
                local_response = local_response + record[-1].capitalize() + ":  <i>Покупка - </i>" + \
                                 (("<b>" + record[1] + "</b>") if float(record[1]) == max_buy else record[
                                     1]) + "\n" + "<i>Продажа - </i>" + \
                                 (("<b>" + record[2] + "</b>") if float(record[2]) == min_sell else record[2]) + "\n"
            if len(local_response) > 0:
                msg_response = msg_response + local_response + "\n"
            else:
                msg_response = msg_response + "Не найдена информация о запрашиваемой валюте в данном регионе\n"

    return msg_response
