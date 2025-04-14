import tkinter
from url_handler import URL, Text, load
from tkinter.font import Font
from parser import HTMLParser
from sys import platform

WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100
HSTEP, VSTEP = 13, 18


FONTS = {}


def get_font(size, weight, slant):
    key = (size, weight, slant)
    if key not in FONTS:
        font = Font(
            size=size,
            weight=weight,
            slant=slant
        )
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]


class Layout:
    def __init__(self, tree):
        self.display_list = []

        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.size = 16

        self.line = []

        self.recurse(tree)
        self.flush()

    def open_tag(self, tag):
        if tag == "i":
            self.style = "italic"
        elif tag == "b":
            self.weight = "bold"
        elif tag == "small":
            self.size -= 2
        elif tag == "big":
            self.size += 4
        elif tag == "br":
            self.flush()

    def close_tag(self, tag):
        if tag == "i":
            self.style = "roman"
        elif tag == "b":
            self.weight = "normal"
        elif tag == "small":
            self.size += 2
        elif tag == "big":
            self.size -= 4
        elif tag == "p":
            self.flush()
            self.cursor_y += VSTEP

    def recurse(self, tree):
        if isinstance(tree, Text):
            for word in tree.text.split():
                self.word(word)
        else:
            self.open_tag(tree.tag)
            for child in tree.children:
                self.recurse(child)
            self.close_tag(tree.tag)

    # def token(self, tok):
    #     if isinstance(tok, Text):
    #         for word in tok.text.split():
    #             self.word(word)

    #     elif tok.tag == "i":
    #         self.style = "italic"
    #     elif tok.tag == "/i":
    #         self.style = "roman"
    #     elif tok.tag == "b":
    #         self.weight = "bold"
    #     elif tok.tag == "/b":
    #         self.weight = "normal"
    #     elif tok.tag == "small":
    #         self.size -= 2
    #     elif tok.tag == "/small":
    #         self.size += 2
    #     elif tok.tag == "big":
    #         self.size += 4
    #     elif tok.tag == "/big":
    #         self.size -= 4
    #     elif tok.tag == "br":
    #         self.flush()
    #     elif tok.tag == "/p":
    #         self.flush()
    #         self.cursor_y += VSTEP

    #     self.cursor_x += HSTEP
    #     if self.cursor_x >= WIDTH - HSTEP:
    #         self.cursor_y += VSTEP
    #         self.cursor_x = HSTEP

    def word(self, word):
        font = get_font(self.size, self.weight, self.style)
        w = font.measure(word)

        if self.cursor_x + w > WIDTH - HSTEP:
            self.flush()
        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ")

    def flush(self):
        if not self.line:
            return

        metrics = [font.metrics() for x, word, font in self.line]

        max_ascent = max([font.metrics("ascent")
                         for x, word, font in self.line])
        baseline = self.cursor_y + 1.25 * max_ascent

        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))

        max_descent = max([font.metrics("descent")
                          for x, word, font in self.line])

        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = HSTEP
        self.line = []


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.scrollbar = tkinter.Scrollbar(self.window, orient="vertical")
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT,
            yscrollcommand=self.scrollbar.set
        )

        self.scrollbar.config(command=self.canvas.yview)
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Up>", self.scrollUp)
        self.window.bind("<Down>", self.scrollDown)
        # self.window.bind_all("<MouseWheel>", self.mouseScroll)
        if sys.platform == "darwin":
            self.canvas.bind("<Button-4>", self.scrollUp) 
            self.canvas.bind("<Button-5>", self.scrollDown)
            self.canvas.bind("<Button-2>", self.mouseScroll)
            self.canvas.bind("<MouseWheel>", self.mouseScroll)
        
            # For newer versions of macOS and Tk
            self.canvas.bind("<MouseWheel>", lambda e: self.mouseScroll(e))
        
        self.display_list = []

    def scrollUp(self, e):
        self.scroll -= SCROLL_STEP
        self.scroll = max(0, self.scroll)
        self.draw()

    def scrollDown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def mouseScroll(self, e):
        print(e.delta, "touch pad scrolling")
        if hasattr(e, 'delta'):
            if e.delta > 0:
                self.scrollUp(e)
            else:
                self.scrollDown(e)

    def draw(self):
        self.canvas.delete("all")
        for x, y, word, font in self.display_list:
            if y > self.scroll + HEIGHT:
                continue
            if y + font.metrics("linespace") < self.scroll:
                continue
            self.canvas.create_text(
                x, y - self.scroll, text=word, font=font, anchor="nw")

    def load(self, url):
        body = load(URL(url))
        self.nodes = HTMLParser(body).parse()
        self.display_list = Layout(self.nodes).display_list
        self.draw()


if __name__ == "__main__":
    import sys
    if (len(sys.argv) == 1):
        # specify a file to load
        Browser().load("./g_index.html")
    else:
        Browser().load(sys.argv[1])

    tkinter.mainloop()
