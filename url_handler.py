import ssl 
import socket
from tkinter.font import Font

class URL:
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme in  ["http", "https"]

        if self.scheme == "http":
            self.port = 30
        elif self.scheme == "https":
            self.port = 443

        if "/" not in url:
            url = url + "/"

        self.host, url = url.split("/", 1)

        self.path = "/" + url

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

    def request(self):
        s = socket.socket(
            family=socket.AF_INET, 
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )

        s.connect((self.host, self.port))

        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        s.send(("GET {} HTTP/1.0\r\n".format(self.path) + \
            "Host: {}\r\n\r\n".format(self.host) + \
            "Connection: {}\r\n\r\n".format("close") + \
            "User-Agent: {}\r\n\r\n".format("my_agent")) \
                .encode("utf8"))

        response = s.makefile("r", encoding="utf-8", newline="\r\n")

        statusline = response.readline()

        version, status, explanation = statusline.split(" ", 2)

        response_headers = {}

        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        body = response.read()
        s.close()

        return body

class Text:
    def __init__(self, text):
        self.text = text
    
    def __repr__(self):
        return "Text('{}')".format(self.text)

class Tag:
    def __init__(self, tag):
        self.tag = tag
    def __repr__(self):
        return "Tag('{}')".format(self.tag)

def lex(body):
    out = []
    buffer = ""
    in_tag = False

    for c in body:
        if c == "<":
            if buffer: out.append(Text(buffer))
            buffer = ""
            in_tag = True
        elif c == ">":
            out.append(Tag(buffer))
            in_tag = False
            buffer = ""
        else:
            buffer += c
    if not in_tag and buffer:
        out.append(Text(buffer))
    return out 
    

def load(url):
    body = url.request()
    return lex(body)

