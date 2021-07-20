import datetime
import logging
import re
from typing import List, Union, Dict

import pyshorteners
import requests
from bs4 import BeautifulSoup

from helpful import mail_menager, file

logging.basicConfig(handlers=[logging.FileHandler(filename="test/logic.log",
                                                  encoding='utf-8', mode='w')],
                    format="%(asctime)s %(name)s:%(funcName)s:%(levelname)s:%(message)s->%(thread)d",
                    datefmt="%F %T",
                    level=logging.INFO)
logging.getLogger("urllib3").setLevel(logging.INFO)
log = logging.getLogger("MailSend")


class Parser:
    GlobalStatusRequest: bool = False  # Переменная которая решает отправку данных на сервер
    DataSendList: Dict[str, List] = {"https://www.pepper.ru/": [], "https://playisgame.com/halyava/": []}

    def __init__(self) -> None:
        self.cropUrl = pyshorteners.Shortener()  # Экземпляр класса по сокращению ссылок
        self.Mail = mail_menager.SMTP_Manager(nameFileConfig="config.txt")

    def SendDataClient(self) -> None:
        self.Mail.SendMessage(titleMail="Отчет о Халяве в интрнете", HtmlSend=self._createData())

        text = f"Send to:{self.Mail.FromSendMail}\t{datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}"
        log.info(text)
        print(text)
        Parser._clear()

    def _createData(self) -> str:
        tmpData = Parser.DataSendList
        res: str = "<html><body>"  # Заголовок
        for keys in tmpData.keys():
            if tmpData[keys]:
                res += f"<h2>{keys}</h2>"
                for index, item in enumerate(tmpData[keys]):
                    res += f"<a href='{self.cropUrl.tinyurl.short(item[1])}'>{index}) {item[0][:120]}\n</a><br>"

        res += "</body></html>"
        return res

    @classmethod
    def _clear(cls):
        Parser.GlobalStatusRequest = False
        for key in cls.DataSendList.keys():
            cls.DataSendList[key].clear()


class Pepper:
    """ Сайт с акциями и халявой    """

    def __init__(self, StartPage: int = 1, EndPage: int = 3, *, SetReFilter: str = "") -> None:
        """
        :param StartPage: От страницы
        :param EndPage: До страницы
        :param SetReFilter: Поиск ключевого слова в акции
        """
        super().__init__()
        self.headersAntiBoot = {
            "Accept": "*/*",
            # F12 -> Network -> www.pepper.ru -> Request Headers -> user-agent
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            # F12 -> Network -> www.pepper.ru -> Request Headers -> cookie
            "cookie": "f_v=%2238adad00-81b2-11eb-b426-0242ac110002%22; _ga=GA1.2.684564031.1615388804; browser_push_permission_requested=1615388864; show_my_tab=0; hide_price_comparison=false; time_frame=%220%22; sort_by=%22relevance%22; q=%22%5Cu044f%5Cu043d%5Cu0434%5Cu0435%5Cu043a%5Cu0441+%5Cu043f%5Cu043b%5Cu044e%5Cu0441%22; hide_local=%220%22; hide_clearance=false; hide_deleted=false; hide_moderated=true; view_layout_horizontal=%221-1%22; hide_expired=%221%22; tg=true; navi=%7B%22threadTypeId-2%22%3A%22discussed%22%2C%22homepage%22%3A%22hot%22%2C%22threadTypeId-3%22%3A%22new%22%2C%22group-freebies%22%3A%22hot%22%7D; discussions_widget_selected_option=%22popular%22; pepper_session=%22dRK6RDVxlCTt0NY2JmPH1JEnqhFfshqwuwYdY58m%22; xsrf_t=%22OvynsXlHlTvIE4OZ4UY3R4U2yfAdDoNq84SUOF1I%22; u_l=0; location=%7B%22thread_location%22%3A%5B%221%22%5D%2C%22hide_local%22%3A%221%22%7D"
        }
        self.File = file.CsvFile("data/pepper.csv")
        self.ListStock: List[List] = self.__getAllStock(StartPage, EndPage, SetReFilter)
        self.__saveData()

    def __getAllStock(self, StartPage: int, EndPage: int, SetReFilter: str) -> List[List]:
        ListStock: Union[List, List[List]] = []
        for page in range(StartPage, EndPage):
            urlPage = f"https://www.pepper.ru/?page={page}/"
            req = requests.get(urlPage, headers=self.headersAntiBoot).text
            soup = BeautifulSoup(req, 'html.parser')

            if not SetReFilter:
                HeadStocks = soup.find_all('a', class_='cept-tt thread-link linkPlain thread-title--list')

            else:
                HeadStocks = soup.find_all('a', class_='cept-tt thread-link linkPlain thread-title--list',
                                           text=re.compile(SetReFilter))

            list(ListStock.append([itemStock.get("title"), itemStock.get("href")]) for itemStock in HeadStocks)
        return ListStock

    def __saveData(self):
        if self.File.readFileAndFindDifferences(self.ListStock,
                                                funIter=Parser.DataSendList["https://www.pepper.ru/"].append):
            self.File.writeFile(self.ListStock, header=("Имя акции", "Ссылка"))
            Parser.GlobalStatusRequest = True


class Playisgame:
    """ Сайт с акциями и раздачами игр   """

    def __init__(self) -> None:
        super().__init__()
        self.headersAntiBoot = {
            "Accept": "*/*",
            # F12 -> Network -> www.pepper.ru -> Request Headers -> user-agent
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        }
        self.File = file.CsvFile("data/playisgame.csv")
        self.ListStock = self.__getAllStock()
        self.__saveData()

    def __getAllStock(self) -> List[List]:
        ListStock: Union[List, List[List]] = []
        urlPage = f"https://playisgame.com/halyava/"
        req = requests.get(urlPage, headers=self.headersAntiBoot).text
        soup = BeautifulSoup(req, 'html.parser')
        HeadStocks = soup.find_all("div", class_="pp-post-wrap pp-grid-item-wrap")
        list(ListStock.append([itemStock.find('h2', class_='pp-post-title').find_next().text,
                               itemStock.find('h2', class_='pp-post-title').find_next().get("href")]) for itemStock in
             HeadStocks)
        return ListStock

    def __saveData(self):
        if self.File.readFileAndFindDifferences(self.ListStock,
                                                funIter=Parser.DataSendList["https://playisgame.com/halyava/"].append):
            self.File.writeFile(self.ListStock, header=("Имя акции", "Ссылка"))
            Parser.GlobalStatusRequest = True


def mainLogic():
    Mail = mail_menager.SMTP_Manager(nameFileConfig="config.txt")
    Mail.SendMessage(titleMail="Отчет о Халяве в интрнете", HtmlSend="<h1>Server Run</h1>")
    print("-\tServer Run\t-")
    LiveProgram: bool = True
    HorseSend = mail_menager.HoursWaiting([11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
    SendLogical = Parser()

    while LiveProgram:

        # Парсеры
        Pepper(1, 3)
        Playisgame()

        # Если данные где-то обновились то отправлять уведомление на мою почту
        if Parser.GlobalStatusRequest:
            SendLogical.SendDataClient()
        else:
            HorseSend.WaitRightHour()  # Ждать указаного часа


if __name__ == '__main__':
    mainLogic()
