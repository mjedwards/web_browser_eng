import tkinter
from url_handler import URL,Text, load
from tkinter.font import Font

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
    def __init__(self, tokens):
        self.tokens = tokens
        self.display_list = []

        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.size = 16

        self.line = []

        for tok in tokens:
            self.token(tok)
        self.flush
        
    def token(self, tok):
        if isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word)
                
        elif tok.tag == "i":
            self.style = "italic"
        elif tok.tag == "/i":
            self.style = "roman"
        elif tok.tag == "b":
            self.weight = "bold"
        elif tok.tag == "/b":
            self.weight = "normal"
        elif tok.tag == "small":
            self.size -= 2
        elif tok.tag == "/small":
            self.size += 2
        elif tok.tag == "big":
            self.size += 4
        elif tok.tag == "/big":
            self.size -= 4
        
        self.cursor_x += HSTEP
        if self.cursor_x >= WIDTH - HSTEP:
            self.cursor_y += VSTEP
            self.cursor_x = HSTEP
    
    def word(self, word):
        font = get_font(self.size, self.weight, self.style)
        w = font.measure(word)
        if self.cursor_x + w > WIDTH - HSTEP:
            self.flush()
        self.line.append((self.cursor_x, word, font))
        print(self.line)
        self.cursor_x += w + font.measure(" ")
    
    def flush(self):
        if not self.line: return
        
        metrics = [font.metrics() for x, word, font in self.line]
        
        max_ascent = max([font.metrics("ascent") for x, word, font in self.line])
        baseline = self.cursor_y + 1.25 * max_ascent
        

        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))
        
            
        
        max_descent = max([font.metrics("descent") for x, word, font in self.line])
        
        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = HSTEP
        self.line = []
        
class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH, 
            height=HEIGHT
        )
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Up>", self.scrollUp)
        self.window.bind("<Down>", self.scrollDown)
        self.display_list = []
        
        

    def scrollUp(self, e):
        self.scroll -= SCROLL_STEP
        self.draw()

    def scrollDown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for x, y, word, font in self.display_list:
            if y > self.scroll + HEIGHT: continue
            if y + font.metrics("linespace") < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll ,text=word, font=font, anchor="nw")

    def load(self, url):
        tokens = load(URL(url))
        self.display_list = Layout(tokens).display_list
        self.draw()
        

if __name__ == "__main__":
    import sys
    Browser().load(sys.argv[1])
    tkinter.mainloop()
