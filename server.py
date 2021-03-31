import socket
import asyncio

requests = ['put', 'get', '*\n']

def run_server(host, port):
    return

class ClientServer(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_recieved(self, data):
        resp = process_data(data.decode())
        self.transport.write(resp.encode())


loop = asyncio.get_event_loop()
coro = loop.create_server(ClientServer, '127.0.0.1', 8181)

server = loop.run_until_complete(coro)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
