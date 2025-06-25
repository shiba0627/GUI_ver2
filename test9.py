import tkinter as tk
from PIL import Image, ImageTk
import time
from config import CCW,CCW_DARK,CW,CW_DARK,FORWARD,FORWARD_DARK,STOP,STOP_DARK

class makeButton:
    def __init__(self):
        pass
class GUIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry('500x500')
        