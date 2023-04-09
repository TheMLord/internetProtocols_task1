from tracing import TracingAS
import sys


def main():
    """Функция main

    Получает на вход IP адрес и создает объект класса TracingAS, который осуществляет
    трассировку и выводит информацию по каждому IP адресу.
    """
    if len(sys.argv) == 2:
        if sys.argv[1] == "-h" or sys.argv[1] == "--help":
            print("Справка по программе: \n",
                  "Чтобы запустить трассировку, можно ввести: \n",
                  "     ...InternetProtocols_tracing> python tracing_utility.py example.ru[8.8.8.8] \n",
                  "либо написать: \n",
                  "     ...InternetProtocols_tracing> python tracing_utility.py      \n",
                  "\n",
                  "О программе: \n",
                  "     ВХОД: на вход подается доменное имя или IP адрес \n",
                  "     осуществляется трассировка до указанного узла.   \n",
                  "     ВЫХОД: для каждого ip маршрутизатора адреса выводится к какой автономной системе он относится, "
                  "определяется страна и провайдер \n")
        else:
            entry = sys.argv[1]
            tr = TracingAS(entry)
    else:
        entry = input("Введите IP-адрес или доменное имя: ")
        tr = TracingAS(entry)


if __name__ == "__main__":
    main()
