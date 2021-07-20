import datetime
import email
import email.header
import imaplib
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict

from helpful import file

"""
kustovd662@gmail.com
kustov20001
pro-progerkustov@yandex.ru
smtp.gmail.com:587
imap.gmail.com:993
"""
class HoursNotification:

    def __init__(self, horsList: List[int]) -> None:
        self.horsList = horsList
        self.selectHors: int = 0

    def WaitRightHour(self):
        HorsTrigger: bool = True
        while HorsTrigger:
            if datetime.datetime.now().hour in self.horsList and self.selectHors != datetime.datetime.now().hour:
                self.selectHors = datetime.datetime.now().hour
                HorsTrigger = False
            else:
                time.sleep(60)


class MailMenger:
    def __init__(self, login: str = None, password: str = None, from_send_mail: str = None, settingSMPTP: str = None,
                 nameFileConfig: str = None, settingIMAP: str = None) -> None:

        """
        :param login:
        :param password:
        :param from_send_mail:
        :param settingSMPTP:
        :param nameFileConfig:
        """

        if nameFileConfig:
            DataConfig = file.TxtFile(nameFileConfig).readFileToResDict("login_mail", "password_mail",
                                                                        "mail_send_data", "smtp", "imap")
            self.Login: str = DataConfig["login_mail"]
            self.Password: str = DataConfig["password_mail"]
            self.FromSendMail: str = DataConfig["mail_send_data"]
            self.SettingSMPTP: str = DataConfig["smtp"]
            self.SettingIMAP: str = DataConfig["imap"]

        else:
            self.Login: str = login
            self.Password: str = password
            self.FromSendMail: str = from_send_mail
            self.SettingSMPTP: str = settingSMPTP
            self.SettingIMAP: str = settingIMAP

        self.smtpObj = smtplib.SMTP(self.SettingSMPTP)  # Параметры для отправки сообщений
        self.imapObj = None  # Параметры для чтения сообщений

    def IfConnected(self):
        try:
            self.smtpObj.starttls()
            self.smtpObj.login(self.Login, self.Password)
            return True
        except smtplib.SMTPAuthenticationError:
            return False

    def __connectionSMTP(self):
        self.smtpObj.starttls()
        self.smtpObj.login(self.Login, self.Password)

    def SendMessage(self, titleMail: str, HtmlSend: str):
        """
        :param HtmlSend: HTML текст
        :param titleMail: Тема письма
        """
        self.__connectionSMTP()

        message = MIMEMultipart("alternative")
        message["From"] = self.Login
        message["To"] = self.FromSendMail
        message["Subject"] = titleMail
        message.attach(MIMEText(HtmlSend, "html"))  # Переводим Html текст в понтяный формат для отображения
        messageSend = message.as_string().encode('utf-8')
        self.smtpObj.sendmail(self.Login, self.FromSendMail,
                              msg=messageSend)

        self.__disconnectionSMTP()

    def __disconnectionSMTP(self):
        self.smtpObj.quit()

    def __connectionIMAP(self):
        self.imapObj = imaplib.IMAP4_SSL(self.SettingIMAP)  # Параметры для чтения сообщений
        self.imapObj.login(self.Login, self.Password)

    def ListReadMyMail(self, limit: int = 10, folderMail: str = "INBOX") -> List[Dict]:
        self.__connectionIMAP()

        self.imapObj.select(folderMail)
        result, data = self.imapObj.search(None, "ALL")
        ids = data[0]
        id_list = ids.split()

        ResList: List[Dict] = []
        ResDict: Dict = {}

        # Чтение от новых к сарым
        for id_message in id_list[::-1][:limit]:
            result, data = self.imapObj.fetch(id_message, "(RFC822)")
            raw_email = data[0][1]
            raw_email_string = raw_email.decode('utf-8')
            email_message = email.message_from_string(raw_email_string)

            ResDict["ID"] = id_message.decode("utf-8")
            ResDict["To"] = email_message['To']
            ResDict["Date"] = email_message['Date']
            ResDict["From"] = email.utils.parseaddr(email_message['From'])
            ResDict["Message-Id"] = email_message['Message-Id']
            ResDict["Subject"] = MailMenger.decode_mime_words(email_message['Subject'])
            ResList.append(ResDict.copy())
            ResDict.clear()

        self.__disconnectionIMAP()
        return ResList

    def ReadBodyMailWithIndex(self, idMail: str, folderMail: str = "INBOX") -> str:
        self.__connectionIMAP()

        self.imapObj.select(folderMail)

        result, data = self.imapObj.fetch(bytes(idMail, 'utf-8'), "(RFC822)")
        raw_email = data[0][1]
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)

        ResTextMessage: str = ""
        if email_message.is_multipart():
            for payload in email_message.get_payload():
                ResTextMessage = payload.get_payload()
        else:

            ResTextMessage = email_message.get_payload()

        self.__disconnectionIMAP()
        return ResTextMessage

    @staticmethod
    def decode_mime_words(text_email) -> str:
        """
        Перевод дял '=?utf-8?B?0J7RgtGH0LXRgtGL?='
        :param text_email: email_message['Subject']
        """
        return u''.join(
            word.decode(encoding or 'utf8') if isinstance(word, bytes) else word
            for word, encoding in email.header.decode_header(text_email))

    def __disconnectionIMAP(self):
        self.imapObj.logout()


if __name__ == '__main__':
    T = MailMenger(nameFileConfig="config.txt")
    Res = T.ListReadMyMail()
    T.ReadBodyMailWithIndex(Res[0]["ID"])
