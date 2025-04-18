import ssl 
import socket
import os
from tkinter.font import Font

class URL:
    def __init__(self, url):
        if not url:
            url = "file://" + os.path.join(os.path.expanduser("~"), g_index.html)

        if "://" in url:
            self.scheme, url = url.split("://", 1)
        

            if self.scheme in ["http", "https"]:
                if self.scheme == "http":
                    self.port = 80
                else:
                    self.port = 443

                if "/" not in url:
                    url = url + "/"

                self.host, url = url.split("/", 1)
                self.path = "/" + url

                if ":" in self.host:
                    self.host, port = self.host.split(":", 1)
                    self.port = int(port)

            elif self.scheme == "file":
                self.host = None
                self.port = None

                if url.startswith("/"):
                    self.path = "/" + url
                elif url.startswith("\\"):
                    self.path = url
                elif len(url) >= 2 and url[1] == ":":
                    self.path = url
                else:
                    self.path = os.path.join(os.getcwd(), url)
            
        else:
            self.scheme = "file"

            if url.startswith("/"):
                    self.path = "/" + url
            elif os.name == 'nt' and (url.startswith("\\") or (len(url) >= 2 and url[1] == ":")):
                self.path = url
            else:
                self.path = os.path.join(os.getcwd(), url)

            self.host = None
            self.port = None

    def request (self):
        if self.scheme == "file":
            return  self.read_file()
        else:
            return self.http_request()

    def read_file(self):
        try:
            path = self.path
        
            if os.name == 'nt':
                if path.startswith("/"):
                    path = path[1:]
        
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"<html><body><h1>Error</h1><p>Could not read file: {e}</p></body></html>"

    def http_request(self):
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
    def __init__(self, text, parent):
        self.text = text
        self.children = []
        self.parent = parent
    
    def __repr__(self):
        return repr(self.text)

class Element:
    def __init__(self, tag, attributes, parent):
        self.tag = tag
        self.attributes = attributes
        self.children = []
        self.parent = parent

    def __repr__(self):
        attrs = [" " + k + "=\"" + v + "\"" for k,v in self.attributes.items()]
        attr_str = ""
        for attr in attrs:
            attr_str += attr
        return "<" + self.tag + attr_str + ">"

def lex(body):
    out = []
    buffer = ""
    in_tag = False

    for c in body:
        if c == "<":
            in_tag = True
            if buffer: out.append(Text(buffer))
            buffer = ""
        elif c == ">":
            in_tag = False
            out.append(Tag(buffer))
            buffer = ""
        else:
            buffer += c
    if not in_tag and buffer:
        out.append(Text(buffer))
    return out 
    

def load(url):
    body = url.request()
    # return lex(body)
    return body

