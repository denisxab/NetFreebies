import datetime
import email
import email.header
import imaplib
import smtplib
import time
from collections import namedtuple
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from helpful import file

"""
kustovd662@gmail.com
kustov20001
pro-progerkustov@yandex.ru
smtp.gmail.com:587
imap.gmail.com:993
"""


class HoursWaiting:
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


class IMAP_Manager:

    def __init__(self, nameFileConfig: str) -> None:
        DataConfig = file.TxtFile(nameFileConfig).readFileToResDict("login_mail", "password_mail",
                                                                    "mail_send_data", "smtp", "imap")
        self.Login: str = DataConfig["login_mail"]
        self.Password: str = DataConfig["password_mail"]
        self.FromSendMail: str = DataConfig["mail_send_data"]
        self.SettingIMAP: str = DataConfig["imap"]
        self.imapObj = None  # Параметры для чтения сообщений

    def __connectionIMAP(self):
        self.imapObj = imaplib.IMAP4_SSL(self.SettingIMAP)  # Параметры для чтения сообщений
        self.imapObj.login(self.Login, self.Password)

    def __disconnectionIMAP(self):
        self.imapObj.logout()

    def ListReadMyMail(self, limitReadMessage: int = 10, folderMail: str = "INBOX") -> List[namedtuple]:
        self.__connectionIMAP()

        self.imapObj.select(folderMail)
        result, data = self.imapObj.search(None, "ALL")
        ids = data[0]
        id_list = ids.split()

        ResList: List[namedtuple] = []
        Nd = namedtuple("HeadMessage", ["ID", "To", "Data", "From", "Message_Id", "Subject"])

        # Чтение от новых к сарым
        for id_message in id_list[::-1][:limitReadMessage]:
            result, data = self.imapObj.fetch(id_message, "(RFC822)")
            raw_email = data[0][1]
            raw_email_string = raw_email.decode('utf-8')
            email_message = email.message_from_string(raw_email_string)

            ResList.append(Nd(id_message.decode("utf-8"),
                              email_message['To'],
                              email_message['Date'],
                              email.utils.parseaddr(email_message['From']),
                              email_message['Message-Id'],
                              IMAP_Manager.decode_mime_words(email_message['Subject'])
                              ))

        self.__disconnectionIMAP()
        return ResList

    def ReadBodyMailByIndex(self, indexMail: str, folderMail: str = "INBOX") -> str:
        self.__connectionIMAP()

        self.imapObj.select(folderMail)
        result, data = self.imapObj.fetch(bytes(indexMail, 'utf-8'), "(RFC822)")
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

    def DeleteMessageByIndex(self, indexMail: str, folderMail: str = "INBOX"):
        self.__connectionIMAP()

        self.imapObj.select(folderMail)
        self.imapObj.store(bytes(indexMail, 'utf-8'), '+FLAGS', '\\Deleted')
        self.imapObj.expunge()

        self.__disconnectionIMAP()

    @staticmethod
    def decode_mime_words(text_email) -> str:
        """
        Перевод дял '=?utf-8?B?0J7RgtGH0LXRgtGL?='
        :param text_email: email_message['Subject']
        """
        return u''.join(
            word.decode(encoding or 'utf8') if isinstance(word, bytes) else word
            for word, encoding in email.header.decode_header(text_email))

    def __del__(self):
        self.__disconnectionIMAP()


class SMTP_Manager:
    def __init__(self, nameFileConfig: str) -> None:
        DataConfig = file.TxtFile(nameFileConfig).readFileToResDict("login_mail", "password_mail",
                                                                    "mail_send_data", "smtp", "imap")
        self.Login: str = DataConfig["login_mail"]
        self.Password: str = DataConfig["password_mail"]
        self.FromSendMail: str = DataConfig["mail_send_data"]
        self.SettingSMPTP: str = DataConfig["smtp"]
        self.smtpObj = smtplib.SMTP(self.SettingSMPTP)  # Параметры для отправки сообщений

    def __connectionSMTP(self):
        self.smtpObj.starttls()
        self.smtpObj.login(self.Login, self.Password)

    def __disconnectionSMTP(self):
        self.smtpObj.quit()

    def IfConnected(self):
        try:
            self.smtpObj.starttls()
            self.smtpObj.login(self.Login, self.Password)
            return True
        except smtplib.SMTPAuthenticationError:
            return False

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

    def __del__(self):
        self.__disconnectionSMTP()


if __name__ == '__main__':
    pass
