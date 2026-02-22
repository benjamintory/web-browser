## Web Browser Main File
import socket
import ssl
import tkinter
from sys import platform

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100


class Browser:
    def __init__(self):
        self.width, self.height = WIDTH, HEIGHT
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack(fill=tkinter.BOTH, expand=1)
        self.window.bind("<Configure>", self.resizewindow)
        self.scroll = 0

        # Bind scroll buttons
        self.window.bind("<Button-4>", self.userscroll)
        self.window.bind("<Button-5>", self.userscroll)
        self.window.bind("<MouseWheel>", self.userscroll)
        self.window.bind("<Down>", self.userscroll)
        self.window.bind("<Up>", self.userscroll)

    def load(self, url):
        self.url = url
        body = url.request()
        text = lex(body)
        self.text = text
        self.display_list = layout(text, self.width)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(10, 20, 100, 200, fill="green")
        for x, y, c in self.display_list:
            if y > self.scroll + self.height:
                continue
            if y + VSTEP < self.scroll:
                continue
            self.canvas.create_text(x, y - self.scroll, text=c)

    def userscroll(self, e):
        # TODO recalculate height stuff for scrolling after window is resized

        # print("self.scroll: " + str(self.scroll))
        # print("display_list bottom y cord: " + str(self.display_list[-1][1]))
        print("Scroll delta" + str(e.delta))
        print(e)

        # check os
        if platform == "linux" or platform == "linux2":
            # linux
            if e.delta <= 0 or e.keysym == "Up":
                print("up")
                if self.scroll < self.display_list[-1][1] - 500:
                    self.scroll += SCROLL_STEP
            elif e.delta >= 0 or e.keysym == "Down":
                print("down")
                if self.scroll > 0:
                    self.scroll -= SCROLL_STEP
        elif platform == "darwin" or platform == "win32":
            # OS X or Windows
            if e.delta >= 0 and e.keysym == "Down":
                # print("up")
                if self.scroll < self.display_list[-1][1] - 500:
                    print("up working")
                    self.scroll += SCROLL_STEP
            elif e.delta <= 0 and e.keysym == "Up":
                # print("down")
                if self.scroll > 0:
                    self.scroll -= SCROLL_STEP
        self.draw()
        print("\n")

    def resizewindow(self, e):
        self.width = e.width
        self.height = e.height
        self.display_list = layout(self.text, self.width)
        self.draw()


class URL:
    def __init__(self, url):
        # try:
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https"]

        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

    # except:

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

        request = "GET {} HTTP/1.0\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
        request += "\r\n"
        s.send(request.encode("utf8"))

        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n":
                break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        content = response.read()
        s.close

        return content


def lex(body):
    text = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            text += c
    return text


def layout(text, width):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x >= width - HSTEP or c == "\\n":
            cursor_y += VSTEP
            cursor_x = HSTEP
    return display_list


if __name__ == "__main__":
    import sys

    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
