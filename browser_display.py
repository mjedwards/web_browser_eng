import tkinter
from url_handler import URL, Text, load
from tkinter.font import Font
from parser import HTMLParser, print_tree
from sys import platform

WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100
HSTEP, VSTEP = 13, 18


FONTS = {}

BLOCK_ELEMENTS = [
    "html", "body", "article", "section", "nav", "aside", "h1",
    "h2", "h3", "h4", "h5", "h6", "hgroup", "header", "footer",
    "address", "p", "hr", "pre", "blockquote", "ol", "ul", "menu",
    "li", "dl", "dt", "dd", "figure", "figcaption", "main", "div",
    "table", "form", "fieldset","legend", "details", "summary"
]

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


class BlockLayoutLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []

        self.display_list = []

        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.size = 16

        self.line = []

        self.recurse(node)
        self.flush()

        self.x = None
        self.y = None
        self.width = None
        self.height = None

    def layout_mode(self):
        if isinstance(self.node, Text):
            return "inline"
        elif any([isinstance(child, Element)and child.tag in BLOCK_ELEMENTS for child in self.node.children]):
            return "block"
        elif self.node.children:
            return "inline"
        else:
            return "block"
    
    def layout(self):
        mode = self.layout_mode()

        if mode == "block":
            previous = None

            for child in self.node.children:
                next = BlockLayout(child, self, previous)
                self.children.append(next)
                previous = next
        else:
            self.cursor_x = 0
            self.cursor_y = 0
            self.weight = "normal"
            self.style = "roma"
            font.size = 12

            self.line = []
            self.recurse(self.node)
            self.flush()
        
        for child in self.children:
            child.layout()
    def recurse(self, tree):
        if isinstance(tree, Text):
            for word in tree.text.split():
                self.word(word)

        # elif tree.tag == "h1":
        #     self.size += 4
        # elif tree.tag == "/h1":
        #     self.size -= 4
        elif tree.tag == "i":
            self.style = "italic"
        elif tree.tag == "/i":
            self.style = "roman"
        elif tree.tag == "b":
            self.weight = "bold"
        elif tree.tag == "/b":
            self.weight = "normal"
        elif tree.tag == "small":
            self.size -= 2
        elif tree.tag == "/small":
            self.size += 2
        elif tree.tag == "big":
            self.size += 4
        elif tree.tag == "/big":
            self.size -= 4
        elif tree.tag == "br":
            self.flush()
        elif tree.tag == "/p":
            self.flush()
            self.cursor_y += VSTEP

        # self.cursor_x += HSTEP
        # if self.cursor_x >= WIDTH - HSTEP:
        #     self.cursor_y += VSTEP
        #     self.cursor_x = HSTEP

        else:
            self.open_tag(tree.tag)
            for child in tree.children:
                self.recurse(child)
            self.close_tag(tree.tag)

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

    def paint(self):

class DocumentLayout:
    def __init__(self, node):
        self.node = node
        self.parent = None
        self.children = []

    def layout(self):
        child = BlockLayout(self.node, self, None)
        self.children.append(child)
        child.layout()
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
        print_tree(self.nodes)
        self.display_list = Layout(self.nodes).display_list
        self.document = Layout(self.nodes)
        self.document.layout()
        self.draw()


class BlockLayout:
    def __init__(self):
        self.block = ""


if __name__ == "__main__":
    import sys
    if (len(sys.argv) == 1):
        # specify a file to load
        Browser().load("./g_index.html")
    else:
        Browser().load(sys.argv[1])

    tkinter.mainloop()
