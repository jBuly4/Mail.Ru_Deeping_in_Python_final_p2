import asyncio
from collections import namedtuple

requests = namedtuple('requests', 'put get all') # all = '*\n'
request = requests(put = 'put', get = 'get', all = '*\n')

# print(request.put)

def run_server(host, port):
    # print(host, port)
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

    return

class ClientServer(asyncio.Protocol):
    data_to_save = {}

    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        print('start connection')
        self.transport = transport
        print('connection made')
        print(self.transport)

    def data_recieved(self, data):
        print('data recieved: {}'.format(data.decode()))
        resp = self.save(data.decode())
        self.transport.write(resp.encode())

    # @staticmethod
    def save(self, input):
        output = ''
        print(input.decode())
        try:
            # print(input)
            raw = input.split(' ')
            if raw[0] == request.get:
                if raw[1] == request.all:
                    if self.data_to_save:
                        for key in self.data_to_save:
                            for value in self.data_to_save[key]:
                                output += str(key) + ' ' + str(value[0]) + ' ' + str(value[1]) +  '\n'
                        return 'ok\n' + output + '\n'
                    else:
                        return 'ok\n\n'
                if raw[1] in self.data_to_save:
                    for value in self.data_to_save[raw[1]]:
                        output += str(raw[1]) + ' ' + str(value[0]) + ' ' + str(value[1]) + '\n'
                    return 'ok\n' + output + '\n'
                else:
                    return 'ok\n\n'
            elif raw[0] == request.put:
                try:
                    if raw[1] not in self.data_to_save:
                        self.data_to_save[raw[1]] = []
                    self.data_to_save[raw[1]].append((raw[2], raw[3]))
                    return 'ok\n\n'
                except Exception:
                    return 'error\nwrong command\n\n'
            else:
                return 'error\nwrong command\n\n'
        except Exception:
            return 'error\nwrong command\n\n'


#loop = asyncio.get_event_loop() #moved to run_server func
#coro = loop.create_server(ClientServer, '127.0.0.1', 8181)

# server = loop.run_until_complete(coro)
#
# try:
#     loop.run_forever()
# except KeyboardInterrupt:
#     pass

# server.close()
# loop.run_until_complete(server.wait_closed())
# loop.close()

run_server('127.0.0.1', 8888)
# ''' som '''
