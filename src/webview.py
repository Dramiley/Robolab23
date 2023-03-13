#!/usr/bin/env python3

"""
This is a simple Webserver to display the current state of the controller
"""
# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

hostName = "172.30.1.45"
serverPort = 8080
controller = None


class Webserver(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>Last position: X: %s Y: %s Direction: %s</p>" % (
        controller.last_position.x, controller.last_position.y, controller.last_position.direction), "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))


class Webview:
    controller = None

    def __init__(self, pController):
        self.planet = None

        # pass the controller to the webserver
        global controller
        controller = pController

        try:
            # start server
            webserver = HTTPServer((hostName, serverPort), Webserver)
            print("Server started http://%s:%s" % (hostName, serverPort))

            # run forever
            webserver.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped.")
        except Exception as e:
            print("Server not started.")
            print(e)



        webserver.server_close()
        print("Server stopped.")
