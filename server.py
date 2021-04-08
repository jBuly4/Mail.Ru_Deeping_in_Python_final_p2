import asyncio
from collections import namedtuple

requests = namedtuple('requests', 'put get all') # all = '*\n'
request = requests(put = 'put', get = 'get', all = '*')


def run_server(host, port):
    server_loop = asyncio.get_event_loop()
    server_obj = server_loop.create_server(ClientServer, host, port) #creates a TCP server and returns server object. Server objects are asynchronous context managers

    server = server_loop.run_until_complete(server_obj) # loop.run_until_complete(future) - Run until the future (an instance of Future) has completed.

    try:
        server_loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    server_loop.run_until_complete(server.wait_closed())
    server_loop.close()

class Storage:
    data_to_save = {}

    def return_all(self):
        output = ''

        if self.data_to_save:
            for key in self.data_to_save:
                for value in self.data_to_save[key]:
                    output += f'{key} {value[0]} {value[1]}\n'
            return 'ok\n' + output + '\n'

        else:
            return 'ok\n\n'

    def return_part(self, key):
        output = ''

        if key in self.data_to_save:
            for value in self.data_to_save[key]:
                output += f'{key} {value[0]} {value[1]}\n'
            return 'ok\n' + output + '\n'
        else:
            return 'ok\n\n'

    def put_in(self, raw):
        try:
            key, value, timestamp = raw.split()
            if key not in self.data_to_save:
                self.data_to_save[key] = []

            self.data_to_save[key] = list(filter(lambda saved_values: saved_values[1] != int(timestamp), self.data_to_save[key])) #filtering timestamps

            self.data_to_save[key].append((float(value), int(timestamp)))

            return 'ok\n\n'

        except Exception:

            return 'error\nwrong command\n\n'

storage = Storage()

class ClientServer(asyncio.Protocol):

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        print('data received: {}'.format(data))
        resp = self.save(data.decode())
        self.transport.write(resp.encode())

    def save(self, input):
        try:
            query, input = input.split(' ', maxsplit=1)

            if query not in request:
                return 'error\nwrong command\n\n'

            elif query == request.get and len(input.split()) == 1:
                return self.getting(input)

            elif query == request.put and len(input.split()) == 3:
                return self.putting(input)

            else:
                return 'error\nwrong command\n\n'

        except Exception:
            return 'error\nwrong command\n\n'

    def getting(self, input):
        try:
            key = input.strip('\n')

            if key == request.all:
                return storage.return_all()

            else:
                return storage.return_part(key)

        except Exception:
            return 'error\nwrong command\n\n'

    def putting(self, input):

        raw = input.strip('\n')

        return storage.put_in(raw)


# run_server('127.0.0.1', 8888)

''' solution

Ниже наша реализация сервера для приема метрик. Код приложения разбит на классы Storage, StorageDriver и MetricsStorageServerProtocol. Storage инкапсулирует в себе методы для работы с хранилищем и сами метрики, в нашем случае мы просто сохраняем их в словарь, лежащий в памяти, однако класс легко расширить и добавить персистентность. StorageDriver — класс представляющий интерфейс для работы с хранилищем. Передача объекта хранилища при инициализации, позволяет абстрагироваться от конкретной реализации самого хранилища (мы можем реализовать хранение на файловой системе или на удаленном сервере, при этом в код класса StorageDriver не придется вносить изменения). В методе __call__ реализована логика разбора входных данных. MetricsStorageServerProtocol — класс, который реализует asyncio-сервер.

Разбив логику приложения на несколько классов, мы можем легко модифицировать программу и добавлять новую функциональность. Также намного легче воспринимать и отлаживать код, который выполняет конкретную задачу, а не делает всё сразу. Надеемся, вы тоже постарались разбить свою реализацию на функциональные блоки с помощью классов и функций.

import asyncio
from collections import defaultdict
from copy import deepcopy


class StorageDriverError(ValueError):
    pass


class Storage:
    """Класс для хранения метрик в памяти процесса"""

    def __init__(self):
        self._data = defaultdict(dict)

    def put(self, key, value, timestamp):
        self._data[key][timestamp] = value

    def get(self, key):

        if key == '*':
            return deepcopy(self._data)

        if key in self._data:
            return {key: deepcopy(self._data.get(key))}

        return {}


class StorageDriver:
    """Класс, предосталяющий интерфейс для работы с хранилищем данных"""

    def __init__(self, storage):
        self.storage = storage

    def __call__(self, data):

        method, *params = data.split()

        if method == "put":
            key, value, timestamp = params
            value, timestamp = float(value), int(timestamp)
            self.storage.put(key, value, timestamp)
            return {}
        elif method == "get":
            key = params.pop()
            if params:
                raise StorageDriverError
            return self.storage.get(key)
        else:
            raise StorageDriverError


class MetricsStorageServerProtocol(asyncio.Protocol):
    """Класс для реализации сервера при помощи asyncio"""

    # Обратите внимание на то, что storage является атрибутом класса, что предоставляет
    # доступ к хранилищу данных для всех экземпляров класса MetricsStorageServerProtocol
    # через обращение к атрибуту self.storage.
    storage = Storage()
    # настройки сообщений сервера
    sep = '\n'
    error_message = "wrong command"
    code_err = 'error'
    code_ok = 'ok'

    def __init__(self):
        super().__init__()
        self.driver = StorageDriver(self.storage)
        self._buffer = b''

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        """Метод data_received вызывается при получении данных в сокете"""

        self._buffer += data

        try:
            request = self._buffer.decode()
            # ждем данных, если команда не завершена символом \n
            if not request.endswith(self.sep):
                return

            self._buffer, message = b'', ''
            raw_data = self.driver(request.rstrip(self.sep))

            for key, values in raw_data.items():
                message += self.sep.join(f'{key} {value} {timestamp}' \
                                         for timestamp, value in sorted(values.items()))
                message += self.sep

            code = self.code_ok
        except (ValueError, UnicodeDecodeError, IndexError):
            message = self.error_message + self.sep
            code = self.code_err

        response = f'{code}{self.sep}{message}{self.sep}'
        # отправляем ответ
        self.transport.write(response.encode())


def run_server(host, port):
    loop = asyncio.get_event_loop()
    coro = loop.create_server(MetricsStorageServerProtocol, host, port)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == "__main__":
    run_server("127.0.0.1", 8888)

'''
