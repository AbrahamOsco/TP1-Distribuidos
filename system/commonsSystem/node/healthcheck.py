import socketserver

HEALTHCHECK_PORT = 8000

class HealthCheckHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        # Send "OK" in response to any received datagram
        self.wfile.write(b"OK\n")

class HealthcheckServer(socketserver.UDPServer):
    allow_reuse_address = True  # Allow immediate reuse of the port

    def __init__(self):
        super().__init__(("", HEALTHCHECK_PORT), HealthCheckHandler)

def start_healthcheck_server(server):
    server.serve_forever()

def shutdown_server(server):
    server.shutdown()
    server.server_close()