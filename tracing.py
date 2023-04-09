from subprocess import run

from ipwhois import IPWhois, IPDefinedError
import pandas as pd
import concurrent.futures


class TracingAS:
    """Класс TracingAS

    Запускает трассировку с помощью утилиты tracert и находит информацию через RIPE об IP
    """

    def __init__(self, ip_or_domain_name):
        """Функция инициализации класса

        :param ip_or_domain_name: входной IP адрес или доменное имя

        Содержит поля: entry - входное доменное имя или IP адрес,
        utility - название используемой утилиты для осуществления трассировки
        trace_result - содержит результат трассировки
        table - для формирования выходного результата в формате таблицы с номером,
        IP, автономной системы, страной и провайдером

        Запускает функции: get_info_about_ip() для получения информации об IP адресах
        через RIPE
        output_table() для вывода результата работы программы в виде таблицы на консоль
        """
        self.entry = ip_or_domain_name
        self.utility = "tracert"
        self.trace_result = self.route_tracing()
        self.table = pd.DataFrame(columns=["№", "IP", "AS", "COUNTRY", "PROVIDER"])
        self.get_info_about_ip()
        self.output_table()

    def route_tracing(self):
        """Функция для осуществления процесса трассировки с помощью утилиты tracert


        с помощью метода run из subprocess запускается утилита tracert c параметрами -h 30 - максимальное
        число прыжков, -d - для отключения обратного DNS резолвирования, так как в данном случае это нецелесообразно,
        поскольку в процессе маршрутизации пакетов могут использоваться только IP адреса узлов, -w 100 для ограничения
        на время ожидания ответа в миллисекундах. После параметров подаем то, что нам ввели - IP адрес или доменное имя
        параметр capture_output=True для захвата и сохранения результатов выполнения команды в атрибуте stdout и
        сообщения об ошибках в stderr

        :return: возвращает информацию о маршрутизации пакетов от исходного узла до заданного узла (хоста),
        проходя через промежуточные маршрутизаторы в сети Интернет
        """
        trace = run([self.utility, "-h", "30", "-d", "-w", "100", self.entry], capture_output=True)
        return trace.stdout.decode("cp866")

    def get_info_from_ripe(self, ip):
        """Функция для получения информации об IP через RIPE

        :param ip: ip адрес о котором нужно получить информацию
        :return: возвращает словарь с информацией о регистрации и владельцах IP адреса
        """
        return IPWhois(ip).lookup_rdap()

    def get_info_about_ip(self):
        """Функция, которая формирует информацию об IP адресах

        в поле trace_result содержится результат трассировки в виде последовательности
        строк, каждая из которых соответствует промежуточному узлу на маршруте до конечного узла

        берет строки вида * ms * ms * ms [8.8.8.8], достаем от туда IP адреса и через многопоточность
        по каждому IP адресу возвращает информацию через функцию get_info_from_ripe()

        :return: заполняет таблицу результата
        """
        counter = 0
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for i in self.trace_result.split("\n"):
                if "ms" in i:
                    ip = i.split()[-1].strip("[]")
                    futures.append(executor.submit(self.get_info_from_ripe, ip))
            for future in concurrent.futures.as_completed(futures):
                try:
                    info_about_ip = future.result()
                    self.table.loc[counter] = [counter + 1, info_about_ip["query"], info_about_ip["asn"],
                                               info_about_ip["asn_country_code"],
                                               info_about_ip["network"]["name"]]
                    counter += 1
                except IPDefinedError:
                    continue

    def output_table(self):
        """Функция для вывода результата программы

        :return: печатает на консоль результат работы программы
        """
        if not self.table.empty:
            print(self.table)
        else:
            print("Неверно указан IP-адрес или доменное имя")
