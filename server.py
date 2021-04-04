import asyncio
from Collections import namedtuple

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

    return

class ClientServer(asyncio.Protocol):
    data_recieved = {}

    def connection_made(self, transport):
        self.transport = transport

    def data_recieved(self, data):
        resp = process_data(data.decode())
        self.transport.write(resp.encode())

    def save(input):
        try:
            pass
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

server.close()
loop.run_until_complete(server.wait_closed())
loop.close()

''' som '''
