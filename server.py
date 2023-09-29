#  coding: utf-8
import os.path
import socketserver


# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip().decode("utf-8")
        print("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK", 'utf-8'))

        request = self.data.splitlines()  # split the request line
        http_request = request[0].split()
        # print(http_request)
        request_method = http_request[0]  # request method is first part of the line
        # print(request_method)

        paths = http_request[1]  # path is the second part of the line

        # checking if the method is get or not
        # any method other than get will not be allowed
        if request_method != "GET":
            self.request.sendall("HTTP/1.1 405 Method Not Allowed\r\n".encode())
            return

        # checking if the path is in directory or not
        if os.path.isdir("www" + paths):
            if paths != "/":
                if paths[-1] != "/":
                    self.request.sendall("HTTP/1.1 301 Moved Permanently\r\n".encode())
                    self.request.sendall(("Content-Type: Location: http://127.0.0.1:8080" + paths + "/" + "\n").encode())
                    return

            paths = paths + "/"

            # checking if the path ends with index.html
            # if it does not, adding index.html at the end
            if not paths.endswith("index.html"):
                paths = paths + "index.html"

        # adding www at the start of the path
        paths = os.path.abspath("www" + paths)

        # checking if path exists
        # https://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-without-exceptions
        if not os.path.exists(paths):
            self.request.sendall("HTTP/1.1 404 File Not Found\r\n".encode())
            return

        elif '..' in http_request[1]:
            self.request.sendall("HTTP/1.1 404 File Not Found\r\n".encode())
            return

        # Opening the file in "r" -> read mode
        with open(paths, "r") as file:
            self.request.sendall("HTTP/1.1 200 OK\r\n".encode())

            # mimetypes for html and css
            if paths.endswith("html"):
                self.request.sendall("Content-type: text/html; charset=utf-8\r\n".encode())
            else:
                self.request.sendall("Content-type: text/css; charset=utf-8\r\n".encode())

            data = file.read().encode()
            self.request.sendall(("Content-Length: " + str(len(data)) + "\r\n\r\n").encode() + data)


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
