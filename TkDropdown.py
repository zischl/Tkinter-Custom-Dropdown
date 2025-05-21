import concurrent.futures
import customtkinter as ctk
import tkinter as tk
import platform 
from collections import defaultdict 
import threading, concurrent
import time

class addCustomDropdown(ctk.CTkToplevel):
    def __init__(self, master, width=None, height=200, corner_radius=10, 
                 border_width=2, border_color="#8800FF", values = (), 
                 fg_color="#181818", text_color='gray', hover_color="#383838", hover_text_color="white", 
                 command=None, anchor='center', hideScrollBar=False, scrollpadx=(0,3), scrollpady=(0,0), enableSearch = False,
                 font=("Arial", 11, 'bold'), option_outline=0, option_border_color='', option_bg_color='', option_rounded_corners=25,
                 option_spacing=10, padx=(3,5), pady=(0,0), ipadx=10, ipady=10, **kwargs):
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
        self.height = height
        self.items = {}
        self.itemLookup = defaultdict(list)
        self.command = command
        self.padx, self.ipadx, self.pady, self.ipady ,self.optionSpacing, self.scrollpadx, self.scrollpady = padx, ipadx, pady, ipady, option_spacing, scrollpadx, scrollpady
        self.hoverItem = (0,)
        self.hoverItemFrame = 1
        self.borderWidth = border_width
        self.borderColor = border_color
        self.fg = fg_color
        self.hoverColor, self.hoverTextColor, self.font = hover_color, hover_text_color, font
        self.optionHeight = self.getOptionHeight()
        self.textColor, self.anchor = text_color, 'nw' if anchor == 'left' else 'ne' if anchor == 'right' else 'center'
        self.option_outline, self.option_border_color, self.option_bg_color, self.option_rounded_corners = option_outline, option_border_color, option_bg_color, option_rounded_corners
        self.need_redraw = False
        self.editCount = 0
        
        self.mainFrame = ctk.CTkFrame(self, width=self.width, height=self.height, corner_radius=corner_radius, border_width=border_width, border_color=border_color
                                   , fg_color=fg_color)
        self.mainFrame.pack()
        self.mainFrame.grid_propagate(False)
        
        self.mainFrame.grid_rowconfigure(0, weight=1)
        self.mainFrame.grid_columnconfigure(0, weight=1)
        
        if not hideScrollBar:
            self.scrollbar = ctk.CTkScrollbar(self.mainFrame, fg_color=fg_color, height=self.height)
            self.scrollbar.grid(row=0, column=0, sticky='nes', pady=(max(7, border_width)+self.pady[0]+self.scrollpady[0], max(7, border_width)+self.pady[1]+self.scrollpady[1]),
                                padx=(0+self.scrollpadx[0], border_width+self.scrollpadx[1]))
        self.scrollbarWidth = self.scrollbar.winfo_reqwidth() if not hideScrollBar else 0
        
        self.mainCanvas = tk.Canvas(self.mainFrame, height=self.height, bg=self.fg, highlightbackground=self.fg)
        self.mainCanvas.grid(row=0, column=0, sticky='nwse', pady=(max(7, border_width)+self.pady[0],max(7, border_width)+self.pady[1]),
                             padx=(border_width+self.padx[0], border_width+self.scrollbarWidth+self.padx[1]))
        self.mainCanvas.update()
        
        if not hideScrollBar:
            self.scrollbar.configure(command=self.mainCanvas.yview)
            self.mainCanvas.configure(yscrollcommand=self.scrollbar.set)

        master.update()
        self.withdraw()
        
        self.mainCanvas.bind("<Motion>", self.onHover)
        self.mainCanvas.bind("<MouseWheel>" ,self.mouseScroller)
        
        self.mainCanvas.bind("<Button-1>", self.onClick)
        
        if values:
            self.add(values[0])
            self.addThreaded(values[1:])
            self.setMasterValue(values[0])
            
        elif hasattr(master ,"_values"):
            self.addThreaded(master._values)
            self.setMasterValue(master._values[0])
            
        self.setGetter()
        self._getRoot()
        if enableSearch: master.bind("<KeyRelease>", self.search)
        self.root.bind("<Configure>", self._positionManager)
        
    def _getRoot(self, master=None):
        if not hasattr(master, 'geometry'):
            self._getRoot(self.master.master)
        else:
            self.root = master
        
        
    def setGetter(self):
        if hasattr(self.master, 'get'):
            self.get = self.master.get
        elif hasattr(self.master, 'cget'):
            self.get = lambda: self.master.cget('text')
        else:
            self.get = None
        
    def setMasterValue(self, value):
        if hasattr(self.master, 'set'):
            self.master.set(value)
        elif hasattr(self.master, 'configure'):
            self.master.configure(text=value)
        elif hasattr(self.master, 'insert') and hasattr(self.master, 'delete'):
            self.master.delete(0, 'end')
            self.master.insert(0, value)
        if hasattr(self.master, '_variable'):
            if self.master._variable is not None:
                self.master._variable.set(value)
        
            
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
        if self.state() == 'withdrawn': 
            self.deiconify() 
            self.focus_force()
            self.bind("<KeyPress>", self.keyScroller)
        else:
            self.withdraw()
            self.unbind("<KeyPress>")
        
    
    def createRoundedRectangle(self, x1, y1, x2, y2, **kwargs):
        radius = self.option_rounded_corners
        points = [
                x1+radius, y1,x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1,
                x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2,
                x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2,
                x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1
                ]

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
        self.itemLookup[option].append(len(self.items))
        self.items[len(self.items)] = item
        self.mainCanvas.configure(scrollregion=self.mainCanvas.bbox('all'))
            
    def onHover(self, event):
        option = self.mainCanvas.find_closest(self.ipadx, self.mainCanvas.canvasy(event.y))
        if option in (self.hoverItem, self.hoverItemFrame): return
        
        tag = self.mainCanvas.gettags(option)[0]
        
        if tag in ('option', 'optionFrame'):
            item = {'option':option, 'optionFrame':self.mainCanvas.find_above(option)}[tag]

            frame = self.mainCanvas.find_below(item)
            if self.hoverItem !=  item:
                    self.mainCanvas.itemconfig(self.hoverItem, fill=self.textColor)
                    self.mainCanvas.itemconfig(self.mainCanvas.find_below(self.hoverItem), fill=self.option_bg_color)
            self.mainCanvas.itemconfigure(item, fill=self.hoverTextColor)
            self.mainCanvas.itemconfigure(frame, fill=self.hoverColor)
            self.hoverItem = item
            self.hoverItemFrame = frame

            
    def mouseScroller(self, event):
        self.mainCanvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def keyScroller(self, event):
        print(1+self.hoverItem[0]//2)
        self.mainCanvas.itemconfigure(self.hoverItem, fill=self.textColor)
        self.mainCanvas.itemconfigure(self.hoverItemFrame, fill=self.option_bg_color)
        if event.keysym == 'Up':
            self.hoverItem = (max(2, self.hoverItem[0]-2),)
            self.hoverItemFrame = self.mainCanvas.find_below(self.hoverItem)
        elif event.keysym == 'Down':
            self.hoverItem = (self.items.get(self.hoverItem[0]//2, 2),)
            self.hoverItemFrame = self.mainCanvas.find_below(self.hoverItem)
            
        self.mainCanvas.itemconfigure(self.hoverItem, fill=self.hoverTextColor)
        self.mainCanvas.itemconfigure(self.hoverItemFrame, fill=self.hoverColor)
        self.mainCanvas.yview_moveto((self.mainCanvas.bbox(self.hoverItemFrame)[1]-self.ipady)/self.mainCanvas.bbox('all')[3])

    def onClick(self, event):
        self.setMasterValue(self.mainCanvas.itemcget(self.hoverItem, 'text'))
        self.withdraw()
        if self.need_redraw: self.redraw()
        
    def delete(self):
        value = self.get()
        if value == '' : return
        [option for item in self.itemLookup for option in self.itemLookup[item] if item.lower().startswith(value.lower())]
        
    def search(self, event):
        value = self.get()
        if value == '':
            self.redraw()
            return
        editCount = self.multiEdit([item for item in self.itemLookup for option in self.itemLookup[item] if item.lower().startswith(value.lower())], tags=('edited',))
        if editCount > self.editCount : self.editCount = editCount
        bbox = self.mainCanvas.bbox('edited')
        if bbox is not None:
            self.mainCanvas.configure(scrollregion=(0, bbox[1]-self.ipady, bbox[2], bbox[3]-bbox[1]+self.ipady*3+self.option_outline))
            for _ in range(10):
                self.mainCanvas.itemconfigure(self.items[editCount+_], state="hidden", tags='hidden')
                self.mainCanvas.itemconfigure(self.mainCanvas.find_below(self.items[editCount+_]), state="hidden", tags='hiddenFrame')
            self.need_redraw = True
        self.mainCanvas.yview_moveto(0)
        
    def multiEdit(self, valueArray, tags=()):
        editCount = len(valueArray)
        for valueIndex in range(editCount):
            self.mainCanvas.itemconfigure(self.items[valueIndex], text=valueArray[valueIndex], tags=("option", *tags), state='normal')
            self.mainCanvas.itemconfigure(self.mainCanvas.find_below(self.items[valueIndex]), tags=('optionFrame'), state="normal")
        return editCount
    
    def redraw(self):
            for option in self.mainCanvas.find_withtag('hidden'):   
                self.mainCanvas.itemconfigure(option, state="normal", tags=('option'))
                self.mainCanvas.itemconfigure(self.mainCanvas.find_below(option), state="normal", tags=('optionFrame'))

            self.mainCanvas.configure(scrollregion=(self.mainCanvas.bbox('all')))
            self.multiEdit([item for item in list(self.itemLookup.keys())[:self.editCount+1]])
            
            self.need_redraw = False
            
    def _positionManager(self, event):
        self.geometry(f"{self.master.cget('width')}x{300}+{self.master.winfo_rootx()}+{self.master.winfo_height()+self.master.winfo_rooty()}")
        
        
        

