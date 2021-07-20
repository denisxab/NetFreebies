import sys

NameProj = "NetFreebies"
VersionProj = "0.0.1"

from helpful import file
from logic import mainLogic, mail_menager


class Console:
    BeakGround = f"{'*' * 40}\n{NameProj} v{VersionProj}\n"

    def __init__(self) -> None:
        print(Console.BeakGround)
        self.tmpFile = file.TxtFile("config.txt")

        try:
            if not mail_menager.SMTP_Manager(nameFileConfig="config.txt").IfConnected():
                print("[ERROR]\tIncorrect login or password!!!")
                print("[INFO]\tCreate new config.txt\n")
                self.createConfigFile()

        except KeyError:
            print("[ERROR]\tIncorrect login or password!!!")
            print("[INFO]\tCreate new config.txt\n")
            self.createConfigFile()

        mainLogic()

    def createConfigFile(self):
        login = input("Login Mail > ")
        password = input("Password Mail > ")
        send = input("Send Mail > ")
        smtp = input("Smtp > ")
        smtp = input("Imap > ")
        self.tmpFile.writeFile(f"{login}\n{password}\n{send}\n{smtp}")
        if not mail_menager.SMTP_Manager(nameFileConfig="config.txt").IfConnected():
            print("[ERROR]\tIncorrect login or password twice !!!")
            sys.exit(0)


def mainConsole():
    Console()


if __name__ == '__main__':
    mainConsole()
