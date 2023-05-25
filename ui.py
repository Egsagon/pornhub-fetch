import threading
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmb

import pyhub

class App(tk.Tk):
    
    def __init__(self) -> None:
        '''
        Initialises the app.
        '''
        
        super().__init__()
        
        self.title('Pornhub Fetch GUI')
        self.geometry('400x200')
        
        urlbox = tk.Frame()
        self.url = tk.Entry(urlbox)
        self.url.bind('<Return>', self.download)
        self.status = tk.StringVar(self, 'Enter video URL')
        
        tk.Label(self, textvariable = self.status).pack()
        self.url.pack(side = 'left', fill = 'x', expand = 1)
        ttk.Button(urlbox, text = 'OK', command = self.download).pack(side = 'right')
        urlbox.pack(fill = 'x', padx = 24, expand = 1)
        
        self.bar = ttk.Progressbar(self, mode = 'determinate', value = 0)
        self.bar.pack(fill = 'x', padx = 24, pady = 24)
    
    def on_verbose(self, *args) -> None:
        '''
        Update the app status.
        '''
        
        msg = args
        
        if len(args) == 3:
            *msg, cur, out = args
            
            msg += [f'[{cur}/{out}]']
            
            # Update progress bar
            self.bar.config(value = (cur / out) * 100)
        
        # Update label
        self.status.set(' '.join(msg))
    
    def download(self, *_) -> None:
        '''
        Start the download process.
        '''
        
        def main():
            try:
                url = self.url.get()
                video = pyhub.video(url)
                path = tkfd.askdirectory() + '/'
                
                video.download(path, callback = self.on_verbose)
                tkmb.showinfo('Done', 'Downloaded video!')
            
            except Exception as err:
                tkmb.showerror('Error', repr(err))
        
        threading.Thread(target = main).start()

if __name__ == '__main__':
    App().mainloop()

# EOF