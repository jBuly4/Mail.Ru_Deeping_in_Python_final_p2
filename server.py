import asyncio
from collections import namedtuple

requests = namedtuple('requests', 'put get all') # all = '*\n'
request = requests(put = 'put', get = 'get', all = '*\n')


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
        if data_to_save:
            for key in data_to_save:
                for value in data_to_save[key]:
                    output += f'{key} {value[0]} {value[1]}\n'
                    # output += str(key) + ' ' + str(value[0]) + ' ' + str(value[1]) +  '\n'
            return 'ok\n' + output + '\n'
        else:
            return 'ok\n\n'

    def return_part(self, key):
        output = ''
        if key in data_to_save:
            for value in data_to_save[key]:
                output += f'{key} {value[0]} {value[1]}\n'
                # output += str(key) + ' ' + str(value[0]) + ' ' + str(value[1]) + '\n'
            return 'ok\n' + output + '\n'
        else:
            return 'ok\n\n'

    def put_in(self, raw):
        try:
            key, value, timestamp = raw.split()
            if key not in data_to_save:
                data_to_save[key] = []
            data_to_save[key].append((value, timestamp))
            return 'ok\n\n'
        except Exception:
            return 'error\nwrong command\n\n'

        return

class ClientServer(asyncio.Protocol):

    def connection_made(self, transport):
        self.transport = transport
        print(self.transport)

    def data_received(self, data):
        print('data received: {}'.format(data))
        resp = self.save(data.decode())
        self.transport.write(resp.encode())

    # @staticmethod
    def save(self, input):
        output = ''
        print('save input {}'.format(input))
        try:
            query, input = input.split(' ', maxsplit=1)
            if query == request.get:
                return getting(input)

            elif query == request.put:
                return putting(input)

            else:
                return 'error\nwrong command\n\n'
        except Exception:
            return 'error\nwrong command\n\n'

    def getting(self, input):
        try:
            key = input.strip('\n')

            if key == request.all:
                return Storage.return_all()
            else:
                return Storage.return_part(key)

        except Exception:
            return 'error\nwrong command\n\n'

    def putting(self, input):

        raw = input.strip('\n')

        return Storage.put_in(raw)


run_server('127.0.0.1', 8888)
