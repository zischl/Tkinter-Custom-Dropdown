import customtkinter as ctk
import tkinter as tk
import platform 
from collections import defaultdict 
import threading


                                   
class addCustomDropdown(ctk.CTkToplevel):
    def __init__(self, master, width=None, height=200, corner_radius=10, bg_color="#4a412a", border_width=0, border_color="white", values = (), 
                 fg_color="#181818", text_color='gray', hover_color="#383838", hover_text_color="white", mouse_cursor="hand2", command=None, 
                 font=('', 11), option_outline=0, option_border_color='', option_bg_color='#282828', **kwargs):
        super().__init__(master)
        self.configure(fg_color="#4a412a", corner_radius=corner_radius)
        self.wm_overrideredirect(True)
        _platform = platform.platform().lower()
        if _platform.startswith("linux"):
            pass
        elif _platform.startswith('win'):
            self.overrideredirect(True)
            self.wm_attributes("-transparentcolor", '#4a412a')
            
        self.master = master
        self.width = width if width is not None else master.cget('width')
        self.height = height if height is not None else master.cget('height')
        self.items = {}
        self.itemLookup = defaultdict(list)
        self.command = command
        self.optionHeight = 15
        self.padx, self.pady = 10, 10
        self.ipadx = 5
        self.hoverItem = 0
        self.hoverItemFrame = None
        self.borderWidth = border_width
        self.borderColor = border_color
        self.fg = fg_color
        self.hoverColor, self.hoverTextColor = hover_color, hover_text_color
        self.textColor = text_color
        self.option_outline, self.option_border_color, self.option_bg_color = option_outline, option_border_color, option_bg_color
        
        self.mainFrame = ctk.CTkFrame(self, width=self.width, height=self.height, corner_radius=corner_radius, border_width=border_width, border_color=border_color
                                   , fg_color=fg_color)
        self.mainFrame.pack()
        self.mainFrame.grid_propagate(False)
        
        self.mainFrame.grid_rowconfigure(0, weight=1)
        self.mainFrame.grid_columnconfigure(0, weight=1)
        
        self.mainCanvas = tk.Canvas(self.mainFrame, height=self.height, bg=self.fg, highlightbackground=self.fg)
        self.mainCanvas.grid(row=0, column=0, sticky='nwse', pady=7)        
        
        self.scrollbar = ctk.CTkScrollbar(self.mainFrame, fg_color=fg_color, command=self.mainCanvas.yview, height=self.height)
        self.scrollbar.grid(row=0, column=0, sticky='nes', pady=7) 
        # self.scrollbar.lower()
        self.mainCanvas.update()

        self.mainCanvas.configure(yscrollcommand=self.scrollbar.set)
        # self.mainCanvas.configure(height=500)

        master.update()
        self.withdraw()
        
        
        self.mainCanvas.bind("<Motion>", self.onHover)
        self.mainCanvas.bind("<MouseWheel>" ,self.mouseScroller)
        
        
        # btn_up = tk.Button(self.mainFrame, text="▲").pack(fill='x')
        # btn_down = tk.Button(self.mainFrame, text="▼").pack(fill='x')
        
        if values:
            self.multiAdd(values)
        
    def multiAdd(self, values):
        for item in values:
            self.mainCanvas.after(0, lambda : self.add(item))
    
    def open(self, *args):
        self.geometry(f"{self.master.cget('width')}x{300}+{self.master.winfo_rootx()}+{self.master.winfo_height()+self.master.winfo_rooty()}")
        self.deiconify() if self.state() == 'withdrawn' else self.withdraw()
    
    def createRoundedRectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        
        points = [x1+radius, y1,
                x1+radius, y1,
                x2-radius, y1,
                x2-radius, y1,
                x2, y1,
                x2, y1+radius,
                x2, y1+radius,
                x2, y2-radius,
                x2, y2-radius,
                x2, y2,
                x2-radius, y2,
                x2-radius, y2,
                x1+radius, y2,
                x1+radius, y2,
                x1, y2,
                x1, y2-radius,
                x1, y2-radius,
                x1, y1+radius,
                x1, y1+radius,
                x1, y1]

        return self.mainCanvas.create_polygon(points, **kwargs, smooth=True)
    
    def add(self, option, command=None):
        x, y = self.padx, len(self.items)*(5+self.optionHeight+self.pady*2)+self.pady
        self.mainCanvas.create_rectangle(self.borderWidth+0, y+self.borderWidth, self.winfo_width()-self.borderWidth*2, (y+self.optionHeight+self.pady*2), 
                                         outline=self.option_border_color, fill=self.option_bg_color, width=self.option_outline, tags=("optionFrame"))
        item = self.mainCanvas.create_text(x, y+self.pady, text=option, fill=self.textColor, font=("Arial", 11), tags=("option"), anchor='nw')
        self.items[len(self.items)] = item
        self.itemLookup[option].append(len(self.items))
        self.mainCanvas.configure(scrollregion=self.mainCanvas.bbox('all'))
            
    def onHover(self, event):
        option = self.mainCanvas.find_closest(self.padx, self.mainCanvas.canvasy(event.y))
        if option in (self.hoverItem, self.hoverItemFrame): return
        
        tag = self.mainCanvas.gettags(option)[0]
        
        if tag in ('option', 'optionFrame'):
            item = {'option':option, 'optionFrame':self.mainCanvas.find_above(option)}[tag]

            frame = self.mainCanvas.find_below(item)
            self.mainCanvas.itemconfigure(item, fill=self.hoverTextColor)
            self.mainCanvas.itemconfigure(frame, fill=self.hoverColor)
            if self.hoverItem !=  item:
                    self.mainCanvas.itemconfig(self.hoverItem, fill=self.textColor)
                    self.mainCanvas.itemconfig(self.mainCanvas.find_below(self.hoverItem), fill=self.option_bg_color)
            self.hoverItem = item
            self.hoverItemFrame = frame
            
    def mouseScroller(self, event):
        self.mainCanvas.yview_scroll(int(-1*(event.delta/120)), "units")

                
app = ctk.CTk()
dropdown = ctk.CTkComboBox(app)
dropdown.pack()
dropdown._dropdown_menu = addCustomDropdown(dropdown, values=['bleh' for _ in range(100)])

app.mainloop()
