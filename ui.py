import threading
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmb

import phfetch

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
    
    def on_verbose(self, cur: int, total: int) -> None:
        '''
        Update the app status.
        '''
        
        pro = round((cur / total) * 100)
        
        # Update progress bar and label
        self.bar.config(value = pro)
        self.status.set(f'Downloading {pro}% [{cur}/{total}]')
    
    def download(self, *_) -> None:
        '''
        Start the download process.
        '''
        
        def main():
            try:
                url = self.url.get()
                video = phfetch.video(url)
                path = tkfd.askdirectory() + '/'
                
                video.download(path, callback = self.on_verbose)
                
                # Reset app
                self.status.set('Enter video URL')
                self.url.delete(0, tk.END)
                self.bar.config(value = 0)
                
                tkmb.showinfo('Done', 'Downloaded video!')
            
            except Exception as err:
                tkmb.showerror('Error', repr(err))
        
        threading.Thread(target = main).start()

if __name__ == '__main__':
    App().mainloop()

# EOF