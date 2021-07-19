from typing import List, Union

import requests
from bs4 import BeautifulSoup

from helpful import file


# DEBUG: bool = True
# logging.basicConfig(handlers=[logging.FileHandler(filename="test/logic.log",
#                                                   encoding='utf-8', mode='w')],
#                     format="%(asctime)s %(name)s:%(funcName)s:%(levelname)s:%(message)s->%(thread)d",
#                     datefmt="%F %T",
#                     level=logging.DEBUG)
# logging.getLogger("urllib3").setLevel(logging.INFO)
# log = logging.getLogger("Pepper")

class Parser:
    headersAntiBoot = {
        "Accept": "*/*",
        # F12 -> Network -> www.pepper.ru -> Request Headers -> user-agent
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        # F12 -> Network -> www.pepper.ru -> Request Headers -> cookie
        "cookie": "f_v=%2238adad00-81b2-11eb-b426-0242ac110002%22; _ga=GA1.2.684564031.1615388804; browser_push_permission_requested=1615388864; show_my_tab=0; hide_price_comparison=false; time_frame=%220%22; sort_by=%22relevance%22; q=%22%5Cu044f%5Cu043d%5Cu0434%5Cu0435%5Cu043a%5Cu0441+%5Cu043f%5Cu043b%5Cu044e%5Cu0441%22; hide_local=%220%22; hide_clearance=false; hide_deleted=false; hide_moderated=true; view_layout_horizontal=%221-1%22; hide_expired=%221%22; tg=true; navi=%7B%22threadTypeId-2%22%3A%22discussed%22%2C%22homepage%22%3A%22hot%22%2C%22threadTypeId-3%22%3A%22new%22%2C%22group-freebies%22%3A%22hot%22%7D; discussions_widget_selected_option=%22popular%22; pepper_session=%22dRK6RDVxlCTt0NY2JmPH1JEnqhFfshqwuwYdY58m%22; xsrf_t=%22OvynsXlHlTvIE4OZ4UY3R4U2yfAdDoNq84SUOF1I%22; u_l=0; location=%7B%22thread_location%22%3A%5B%221%22%5D%2C%22hide_local%22%3A%221%22%7D"
    }


class Pepper(Parser):
    def __init__(self, StartPage: int = 1, EndPage: int = 30) -> None:
        super().__init__()
        self.File = file.CsvFile("pepper.csv")
        self.ListStock = self.__getAllStock(StartPage, EndPage)
        self.__saveData()

    def __getAllStock(self, StartPage: int, EndPage: int) -> List[List]:
        ListStock: Union[List, List[List]] = []
        for page in range(StartPage, EndPage):
            urlPage = f"https://www.pepper.ru/?page={page}/"
            req = requests.get(urlPage, headers=self.headersAntiBoot).text
            soup = BeautifulSoup(req, "lxml")
            HeadStocks = soup.find_all('a', class_='cept-tt thread-link linkPlain thread-title--list')
            list(ListStock.append([itemStock.get("title"), itemStock.get("href")]) for itemStock in HeadStocks)
        return ListStock

    def __saveData(self):
        self.File.writeFile(self.ListStock, header=("Имя акции", "Ссылка"))


if __name__ == '__main__':
    t = Pepper(1, 3)
    print()

# url = "https://www.pepper.ru/"
# # Параметры которые показывают что ты не бот
# headers = {
#
#     "Accept": "*/*",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
# }
# req = requests.get(url, headers=headers).text
#
# print()

# with open("test/pep.html", mode="r", encoding="utf-8") as file:
#     src = file.read()
#
# soup = BeautifulSoup(src, "lxml")
#
# res = soup.find_all('a', class_='cept-tt thread-link linkPlain thread-title--list')
#
# res2 = soup.find_all("div",
#                      class_="userHtml userHtml-content")
#
#
# find_textThenRe = soup.find_all('a', class_='cept-tt thread-link linkPlain thread-title--list',text=re.compile("Холодильник"))
#
#
# """
#
# res[0].text = Имя акции
#
# res[0].attrs["href"] =  res[0].get("href") = Ссылка на акуццию
# .
# res2[0].text - Описание товара
# """
#
# print()
