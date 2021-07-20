import datetime
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from helpful import file


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


class MailSend:
    def __init__(self, login: str = None, password: str = None, from_send_mail: str = None, settingSMPTP: str = None,
                 nameFileConfig: str = None) -> None:

        """
        :param login:
        :param password:
        :param from_send_mail:
        :param settingSMPTP:
        :param nameFileConfig:
        """

        if nameFileConfig:
            DataConfig = file.TxtFile(nameFileConfig).readFileToResDict("login_mail", "password_mail",
                                                                        "mail_send_data", "smtp")
            self.Login: str = DataConfig["login_mail"]
            self.Password: str = DataConfig["password_mail"]
            self.FromSendMail: str = DataConfig["mail_send_data"]
            self.SettingSMPTP: str = DataConfig["smtp"]

        else:
            self.Login: str = login
            self.Password: str = password
            self.FromSendMail: str = from_send_mail
            self.SettingSMPTP: str = settingSMPTP

        self.smtpObj = smtplib.SMTP(self.SettingSMPTP)
        self.smtpObj.starttls()

    def IfConnected(self):
        try:
            self.smtpObj.login(self.Login, self.Password)
            return True
        except smtplib.SMTPAuthenticationError:
            return False

    def __connection(self):
        self.smtpObj = smtplib.SMTP(self.SettingSMPTP)
        self.smtpObj.starttls()
        self.smtpObj.login(self.Login, self.Password)

    def SendMessage(self, titleMail: str, HtmlSend: str):
        """
        :param HtmlSend: HTML текст
        :param titleMail: Тема письма
        """
        self.__connection()

        message = MIMEMultipart("alternative")
        message["From"] = self.Login
        message["To"] = self.FromSendMail
        message["Subject"] = titleMail
        message.attach(MIMEText(HtmlSend, "html"))  # Переводим Html текст в понтяный формат для отображения
        messageSend = message.as_string().encode('utf-8')
        self.smtpObj.sendmail(self.Login, self.FromSendMail,
                              msg=messageSend)

        self.__disconnection()

    def __disconnection(self):
        self.smtpObj.quit()
