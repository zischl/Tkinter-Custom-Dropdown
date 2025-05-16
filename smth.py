import customtkinter as ctk
import tkinter as tk
import platform 
from collections import defaultdict 
import threading

class addCustomDropdown(ctk.CTkToplevel):
    def __init__(self, master, width=None, height=200, corner_radius=10, 
                 border_width=0, border_color="white", values = (), 
                 fg_color="#181818", text_color='gray', hover_color="#383838", hover_text_color="white", 
                 command=None, anchor='left', hideScrollBar=False,
                 font=("Arial", 11, 'bold'), option_outline=0, option_border_color='', option_bg_color='', option_rounded_corners=25,
                 option_spacing=10, padx=(0,0), pady=(0,0), ipadx=10, ipady=10, **kwargs):
        super().__init__(master)
        self.configure(fg_color="#4a412a", corner_radius=corner_radius)
        self.wm_overrideredirect(True)
        _platform = platform.platform().lower()
        if _platform.startswith("linux"):
            pass
        elif _platform.startswith('win'):
            self.overrideredirect(True)
            self.wm_attributes("-transparentcolor", '#4a412a')
        
        if "combo" in master.winfo_name():
            master._dropdown_menu = self
        
        
        self.master = master
        self.width = width if width is not None else master.cget('width')
        self.height = height if height is not None else master.cget('height')
        self.items = {}
        self.itemLookup = defaultdict(list)
        self.command = command
        self.padx, self.ipadx, self.pady, self.ipady ,self.optionSpacing = padx, ipadx, pady, ipady, option_spacing
        self.hoverItem = 0
        self.hoverItemFrame = None
        self.borderWidth = border_width
        self.borderColor = border_color
        self.fg = fg_color
        self.hoverColor, self.hoverTextColor, self.font = hover_color, hover_text_color, font
        self.optionHeight = self.getOptionHeight()
        self.textColor, self.anchor = text_color, 'nw' if anchor == 'left' else 'ne' if anchor == 'right' else 'center'
        self.option_outline, self.option_border_color, self.option_bg_color, self.option_rounded_corners = option_outline, option_border_color, option_bg_color, option_rounded_corners
        
        
        self.mainFrame = ctk.CTkFrame(self, width=self.width, height=self.height, corner_radius=corner_radius, border_width=border_width, border_color=border_color
                                   , fg_color=fg_color)
        self.mainFrame.pack()
        self.mainFrame.grid_propagate(False)
        
        self.mainFrame.grid_rowconfigure(0, weight=1)
        self.mainFrame.grid_columnconfigure(0, weight=1)
        
        if not hideScrollBar:
            self.scrollbar = ctk.CTkScrollbar(self.mainFrame, fg_color=fg_color, height=self.height)
            self.scrollbar.grid(row=0, column=0, sticky='nes', pady=(max(7, border_width)+self.pady[0],max(7, border_width)+self.pady[1]), padx=(0, border_width))
        self.scrollbarWidth = self.scrollbar.winfo_reqwidth() if not hideScrollBar else 0
        
        self.mainCanvas = tk.Canvas(self.mainFrame, height=self.height, bg=self.fg, highlightbackground=self.fg)
        self.mainCanvas.grid(row=0, column=0, sticky='nwse', pady=(max(7, border_width)+self.pady[0],max(7, border_width)+self.pady[1]), padx=(border_width+self.padx[0], border_width+self.scrollbarWidth+self.padx[1]))        
        self.mainCanvas.update()
        if not hideScrollBar:
            self.scrollbar.configure(command=self.mainCanvas.yview)
            # self.scrollbar.lower()
            self.mainCanvas.configure(yscrollcommand=self.scrollbar.set)

        master.update()
        self.withdraw()
        
        
        self.mainCanvas.bind("<Motion>", self.onHover)
        self.mainCanvas.bind("<MouseWheel>" ,self.mouseScroller)
        self.mainCanvas.bind("<Button-1>", self.onClick)
        
        
        # btn_up = tk.Button(self.mainFrame, text="▲").pack(fill='x')
        # btn_down = tk.Button(self.mainFrame, text="▼").pack(fill='x')
        
        if values:
            self.addThreaded(values)
            
        if master._values:
            self.addThreaded(master._values)
            
    def getOptionHeight(self):
        canvas = tk.Canvas(self, width=50, height=50)
        text = canvas.create_text(0, 0, text="Sample Text", font=self.font)
        bbox = canvas.bbox(text)

        optionHeight = bbox[3] - bbox[1]
        return optionHeight
            
    def addThreaded(self, values):
        threading.Thread(target=self.multiAdd, kwargs={'values':values}, daemon=True).start()
        
    def multiAdd(self, values):
        for item in values:
            self.add(option=item)

    def open(self, *args):
        self.geometry(f"{self.master.cget('width')}x{300}+{self.master.winfo_rootx()}+{self.master.winfo_height()+self.master.winfo_rooty()}")
        self.deiconify() if self.state() == 'withdrawn' else self.withdraw()
    
    def createRoundedRectangle(self, x1, y1, x2, y2, **kwargs):
        radius = self.option_rounded_corners
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
        y =  len(self.items)*(self.optionSpacing+self.optionHeight+self.ipady*2)+self.ipady
        if self.option_rounded_corners != 0:
            self.createRoundedRectangle(self.option_outline+0, y+self.option_outline, self.mainCanvas.winfo_width(), (y+self.optionHeight+self.ipady*2), 
                                            outline=self.option_border_color, fill=self.option_bg_color, width=self.option_outline, tags=("optionFrame"))
        else:
            self.mainCanvas.create_rectangle(self.option_outline+0, y+self.option_outline, self.mainCanvas.winfo_width(), (y+self.optionHeight+self.ipady*2), 
                                            outline=self.option_border_color, fill=self.option_bg_color, width=self.option_outline, tags=("optionFrame"))
        if self.anchor == 'nw':
            item = self.mainCanvas.create_text(self.ipadx, y+self.ipady, text=option, fill=self.textColor, font=self.font, tags=("option"), anchor=self.anchor)
        elif self.anchor == 'center':
            item = self.mainCanvas.create_text((self.mainCanvas.winfo_width()/2), y+self.ipady+self.optionHeight//2, text=option, fill=self.textColor, font=self.font, tags=("option"), anchor=self.anchor)
        else:
            item = self.mainCanvas.create_text(self.mainCanvas.winfo_width()-self.ipadx, y+self.ipady, text=option, fill=self.textColor, font=self.font, tags=("option"), anchor=self.anchor)
        self.items[len(self.items)] = item
        self.itemLookup[option].append(len(self.items))
        self.mainCanvas.configure(scrollregion=self.mainCanvas.bbox('all'))
            
    def onHover(self, event):
        option = self.mainCanvas.find_closest(self.ipadx, self.mainCanvas.canvasy(event.y))
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

    def onClick(self, event):
        self.master.set(self.mainCanvas.itemcget(self.hoverItem, 'text'))
    
app = ctk.CTk()
dropdown = ctk.CTkComboBox(app, values=[f'bleh{_}' for _ in range(30000)], command=lambda: print('grg'))
dropdown.pack()

addCustomDropdown(dropdown)
app.mainloop()
