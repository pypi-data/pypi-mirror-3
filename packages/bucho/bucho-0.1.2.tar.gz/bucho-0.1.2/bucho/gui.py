from bucho.compat import Tkinter as tk

if tk:
    class BuchoFrame(tk.Frame):
        def __init__(self, text):
            tk.Frame.__init__(self)
            self.text = text
            self.init_view()
    
        def init_view(self):
            self.text_view = tk.Text(self)
            self.text_view.insert(tk.END, self.text)
            self.text_view.configure(state=tk.DISABLED)
            self.text_view.pack(fill=tk.BOTH, expand=True)
    
            
        def run(self):
            self.pack(fill=tk.BOTH, expand=True)
            self.mainloop()
