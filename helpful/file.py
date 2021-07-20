import csv
import json
import os
import pickle
import shutil
from os import remove, SEEK_END, SEEK_SET
from os.path import getsize, abspath, exists
from typing import List, Dict, Union, Any


class File:
    """
    )Утилиты
    - удаление файла
    - проверка существаования файла
    - проверка существаования файла и если его нет то создание
    - путь к файлу
    - размер файла
    - проверка разрешения открытия файла
    """
    __slots__ = "nameFile"

    def __init__(self, nameFile: str):
        self.nameFile: str = nameFile
        self.createFileIfDoesntExist()

    def createFileIfDoesntExist(self):  # +
        # Создать файл если его нет
        if not exists(self.nameFile):
            try:
                open(self.nameFile, "w+").close()
            except FileNotFoundError:  # Создавать папки и деректории
                self.createRoute()
                open(self.nameFile, "w+").close()


    def checkExistenceFile(self) -> bool:  # +
        # Проверить существование файла
        return True if exists(self.nameFile) else False

    def deleteFile(self):  # +
        # Удаление файла
        if File.checkExistenceFile(self.nameFile):
            remove(self.route())

    def sizeFile(self) -> int:  # +
        # Размер файла в байтах
        return getsize(self.nameFile)

    def route(self) -> str:  # +
        # Путь к файлу
        return abspath(self.nameFile)

    def readFile(self, *arg) -> Any:
        raise NotImplementedError()

    def writeFile(self, arg: Any):
        raise NotImplementedError()

    def appendFile(self, arg: Any):
        raise NotImplementedError()

    def createRoute(self):
        tmp_route: str = ""
        for folder_name in self.nameFile.split('/')[:-1]:
            tmp_route += folder_name
            os.mkdir(tmp_route)
            tmp_route += '/'

    def removeRoute(self):
        shutil.rmtree(self.nameFile.split('/')[1])


class PickleFile(File):
    # https://docs.python.org/3/library/pickle.html
    def __init__(self, nameFile: str):
        tmp = nameFile.split(".")
        if any((len(tmp) != 2, tmp[1] != "pkl")):
            raise ValueError("Файл должен иметь разшерение .pkl")

        File.__init__(self, nameFile)

    def writeFile(self, data: Any, *, protocol: int = 3):
        with open(self.nameFile, "wb") as pickFile:
            pickle.dump(data, pickFile, protocol=protocol)

    def readFile(self) -> Any:
        with open(self.nameFile, "rb") as pickFile:
            return pickle.load(pickFile)

    def appendFile(self, data: Any, *, protocol: int = 3):

        tmp_data = self.readFile()
        if type(data) == type(tmp_data):
            # Tuple List
            if type(data) == tuple or type(data) == list:
                self.writeFile(tmp_data + data)

            # Dict Set
            elif type(data) == dict:
                tmp_data.update(data)
                self.writeFile(tmp_data)
        else:
            raise TypeError("Тип даннных в файле и тип входных данных раличны")


class CsvFile(File):
    def __init__(self, nameFile: str):
        tmp = nameFile.split(".")
        if any((len(tmp) != 2, tmp[1] != "csv")):
            raise ValueError("Файл должен иметь разшерение .csv")

        File.__init__(self, nameFile)

    def readFile(self, *,
                 encoding: str = "utf-8",
                 newline: str = "",
                 limit: int = None,
                 miss_get_head=False
                 ) -> List[List[str]]:  # +
        """
        :param limit: ограничения чтения строк
        :param miss_get_head: # Пропустить чтение заголвка
        :param encoding: open()
        :param newline: open()
        :return:
        """
        res = []
        with open(self.nameFile, "r", encoding=encoding, newline=newline) as f:
            if limit:  # Лимит чтения строк
                reader = csv.reader(f)
                try:
                    for row in range(limit):
                        res.append(reader.__next__())
                except StopIteration:
                    pass
            else:
                res = list(csv.reader(f))

            if miss_get_head:  # Провустить заголовок
                return res[1::]
            return res

    def readFileAndFindDifferences(self, new_data_find: List[List], funIter) -> bool:  # +
        """
        for new_data, data_file in zip(self.ListStock, DataFile):
            if new_data != data_file:
                funIter(new_data)

        :param new_data_find: Новые данные
        :param funIter: Функция которая будет выполняться на каждой итерации
        """
        DataFile = self.readFile(miss_get_head=True)
        if DataFile != new_data_find:
            list(funIter(new_data) for new_data in new_data_find if new_data not in DataFile)
            return True
        else:
            return False

    def readFileRevers(self, *,
                       limit: int = None,
                       encoding: str = "utf-8",
                       newline: str = ""
                       ) -> List[List[str]]:
        def reversed_lines(file):
            # Generate the lines of file in reverse order
            part = ''
            for block in reversed_blocks(file):
                for c in reversed(block):
                    if c == '\n' and part:
                        yield part[::-1]
                        part = ''
                    part += c
            if part:
                yield part[::-1]

        def reversed_blocks(file, block_size=4096):
            # Generate blocks of file's contents in reverse order.
            file.seek(0, SEEK_END)
            here = file.tell()
            while 0 < here:
                delta = min(block_size, here)
                here -= delta
                file.seek(here, SEEK_SET)
                yield file.read(delta)

        res = []
        with open(self.nameFile, "r", encoding=encoding, newline=newline) as f:

            if limit:  # Лимит чтения строк
                for row in csv.reader(reversed_lines(f)):
                    if limit:
                        res.append(row)
                        limit -= 1
                    else:
                        break
            else:
                for row in csv.reader(reversed_lines(f)):
                    res.append(row)
        return res

    def writeFile(self, data: Union[List[Union[str, int, float]],
                                    List[List[Union[str, int, float]]]], *,
                  header: tuple = None,
                  FlagDataConferToStr: bool = False,
                  encoding: str = "utf-8",
                  newline: str = ""
                  ):  # +
        """
        :param data:
        :param header: Эти даныне будут заголовками
        :param FlagDataConferToStr: Переводит все данные в формат str
        :param encoding: open()
        :param newline: open()
        """
        with open(self.nameFile, "w", encoding=encoding, newline=newline) as f:
            writer = csv.writer(f)
            if header:  # Запись заголовка
                writer.writerow(header)

            if FlagDataConferToStr:
                if type(data[0]) != list:
                    data = [str(n) for n in data]
                else:
                    data = [[str(n) for n in m] for m in data]

            if type(data[0]) != list:
                writer.writerow(data)
            else:
                writer.writerows(data)

    def appendFile(self, data: Union[List[Union[str, int, float]],
                                     List[List[Union[str, int, float]]]], *,
                   FlagDataConferToStr: bool = False,
                   encoding: str = "utf-8",
                   newline: str = ""
                   ):  # +
        with open(self.nameFile, "a", encoding=encoding, newline=newline) as f:
            writer = csv.writer(f)
            if FlagDataConferToStr:
                if type(data[0]) != list:
                    data = [str(n) for n in data]
                else:
                    data = [[str(n) for n in m] for m in data]

            if type(data[0]) != list:
                writer.writerow(data)
            else:
                writer.writerows(data)


class TxtFile(File):
    """
    )Открытьвать текстового файла в текстовом и БИНАРНОМ виде на
    - чтение
    - запись
    - дозапись стандартную
    """

    def __init__(self, nameFile: str):
        tmp = nameFile.split(".")
        if any((len(tmp) != 2, tmp[1] != "txt")):
            raise ValueError("Файл должен иметь разшерение .txt")

        File.__init__(self, nameFile)

    def readFileToResDict(self, *args: str, separator: str = '\n') -> Dict[str, str]:
        """
        :param separator:
        :param args: Имя ключей словаря
        """
        resDict: Dict[str, str] = {}
        with open(self.nameFile, "r") as f:
            for index, line in enumerate(f):
                resDict[args[index]] = line.replace(separator, "")
        return resDict

    def readFile(self, limit: int = 0) -> str:  # +
        with open(self.nameFile, "r") as f:
            if limit:
                res: str = ""
                for line in f:
                    if limit:
                        res += line
                        limit -= 1
                    else:
                        break
                return res
            else:
                return f.read()

    def searchFile(self, data: str) -> bool:
        res = False
        with open(self.nameFile, "r") as f:
            for line in f:
                if line.find(data) != -1:
                    res = True
                    break
        return res

    def readBinaryFile(self) -> bytes:  # +
        with open(self.nameFile, "rb") as f:
            return f.read()

    def writeFile(self, data: str):  # +
        with open(self.nameFile, "w") as f:
            f.write(data)

    def writeBinaryFile(self, data: Union[bytes, memoryview]):  # +
        with open(self.nameFile, "wb") as f:
            f.write(data)

    def appendFile(self, data: str):  # +
        with open(self.nameFile, "a") as f:
            f.write(data)

    def appendBinaryFile(self, data: bytes):  # +
        with open(self.nameFile, "ab") as f:
            f.write(data)


class JsonFile(File):
    """
    )Открывать json файлы на
    - чтение
    - запись
    - дозапись массива
    """

    def __init__(self, nameFile: str):
        tmp = nameFile.split(".")
        if len(tmp) != 2 or tmp[1] != "json":
            raise ValueError("Файл должен иметь разшерение .json")
        File.__init__(self, nameFile)

    def readFile(self) -> Union[List, Dict]:  # +
        with open(self.nameFile, "r") as read_file:
            return json.load(read_file)

    def writeFile(self, data: Union[List, Dict], *, indent=4, ensure_ascii: bool = False):  # +
        """
        :param data: Даныне на запись
        :param indent: Отступы пр записи
        :param ensure_ascii: Экранировать символы, использовать False для записи кирилицы
        """
        with open(self.nameFile, "w") as write_file:
            json.dump(data, write_file, indent=1, ensure_ascii=ensure_ascii)

    def appendFile(self, data: Union[List, Dict], *, ensure_ascii: bool = False):  # +
        tmp_data = self.readFile()
        if type(data) == type(tmp_data):
            # Tuple List
            if type(data) == tuple or type(data) == list:
                self.writeFile(tmp_data + data, ensure_ascii=ensure_ascii)

            # Dict Set
            elif type(data) == dict:
                tmp_data.update(data)
                self.writeFile(tmp_data, ensure_ascii=ensure_ascii)
        else:
            raise TypeError("Тип даннных в файле и тип входных данных раличны")


if __name__ == '__main__':
    pass
