import tkinter as tk
import matplotlib
import os
import matplotlib.pyplot as plt
import csv
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import PySimpleGUI as sg
import tkinter as Tk
from PIL import Image, ImageTk, ImageSequence

matplotlib.rc('figure', max_open_warning = 0)

def draw_figure(canvas, fig): #to embed the matplotlib graph into the gui
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=1)

    def on_key_press(event):
        key_press_handler(event, canvas, toolbar)
        canvas.TKCanvas.mpl_connect("key_press_event", on_key_press)
    return

sg.ChangeLookAndFeel('Purple') #change colour

# menu_def = [['&File', ['Properties']]] #to add a menu at top


centred =  [[sg.Text('AlcoLock', size=(30, 1), justification='center', font=("Helvetica", 25), relief=sg.RELIEF_RIDGE)],
            [sg.Button('Take reading',key='_PLOT_')],
            [sg.Canvas(key='controls_cv')],
            [sg.T('Figure:')],
            [sg.Column(
                layout=[
                    [sg.Canvas(key='fig_cv',
                               size=(400 * 2, 400) #set size for graph
                               )]
                ],
                background_color='#DAE0E6',
                pad=(0, 0)
            )]
            ]

blocked_sites = ['Red', 'Green', 'Blue', 'Yellow', 'Orange', 'Purple', 'Chartreuse']

layout = [
   # [sg.Menu(menu_def, tearoff=True)],
    [sg.Column(centred, element_justification='center')],
    [sg.T('Blocked sites')],
    [sg.Listbox(blocked_sites, size=(15, len(blocked_sites)), key='-SITES-')],   
    [sg.Button('Close')]]

window = sg.Window('AlcoLock', layout, default_element_size=(40, 1), grab_anywhere=False)
window.Finalize()
plt.figure() 

while True:
    event, values = window.read()
    if event in [None, 'Exit']: 
        window.close()
        break
    #potential implementation check if the CSV has been modified, use that as event
    #if(!table.equals(self, pd.read_csv("data\Alcolock2021-02-10.csv"))):
    #   table = pd.read_csv("data\Alcolock2021-02-10.csv")
    #   boolean hasChanged = True
    elif(event == '_PLOT_'): #change to hasChanged, itll replot every time new data comes in 
        #table = pd.read_csv("Book1.csv")
        table = pd.read_csv("data\Alcolock2021-02-10.csv")
        #table.plot(x='Time')
        table.plot(x='timestamp')
        #status = table["Alcohol"].iloc[-1]
        status = table["alcohol_level"].iloc[-1]
        output = None
        if(status < 10):
            output = "You are not drunk!"
        elif(status < 15 and status >= 10):
            output = "You are slightly drunk!"
        elif(status >= 15):
            output = "You are very drunk!"
        matplotlib.pyplot.title(output)
        matplotlib.pyplot.hlines(11, 0, 10, colors='k', linestyles='solid') #these will be the level at which not drunk and drunk
        matplotlib.pyplot.hlines(15, 0, 10, colors='k', linestyles='solid') #ie inbetween is tipsy so some websites are blocked
        fig = plt.gcf()
        DPI = fig.get_dpi()
        
        fig.set_size_inches(404 * 2 / float(DPI), 404 / float(DPI))
        
        plt.grid()
        draw_figure(window.FindElement('fig_cv').TKCanvas, fig)
        #sg.popup_animated('earth.gif','Test')

    #websites = [add multiple websites]
    #Add the function to block the websites here
    #if(drunk):
    #   call block function
    #   set boolean as drunk
    #   if(super drunk):
    #       block(websites[all])
    #   if(tipsy):
    #       block(websites[-2:])
    #if(drunk to undrunk ie if .iloc[-1] < drunk and .iloc[-2] > drunk)
    #   unblock the websites

    #potential implementation, text in sick for work if beyong 1am and still drunk
    elif(event == 'Close'):
        window.close()