import tkinter as tk
import matplotlib
import os
import matplotlib.pyplot as plt
import csv
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
from blocker.website_control import block_write, unblock_write
import PySimpleGUI as sg
import tkinter as Tk
from PIL import Image, ImageTk, ImageSequence
import smtplib, ssl
import pyautogui

matplotlib.rc('figure', max_open_warning = 0)

blocked_sited = []
m_blocked_sited = []
with open("blocker/sites.txt", "r+") as f:
    blocked_sites = f.read().splitlines()
with open("blocker/medium.txt", "r+") as f:
    m_blocked_sites = f.read().splitlines()

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

centred =  [[sg.Text('AlcoLock', size=(30, 1), justification='center', font=("Helvetica", 25), relief=sg.RELIEF_RIDGE)],
            [sg.Button('Take reading',key='_PLOT_')],
            [sg.Canvas()],
#            [sg.T('Figure:')],
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

layout = [
   # [sg.Menu(menu_def, tearoff=True)],
    [sg.Column(centred, element_justification='center')],
    [sg.T('Blocked sites')],
    [sg.Listbox(blocked_sites, size=(15, len(blocked_sites)), key='_SITES_')],
    [sg.Text('Password', size=(15, 1)), sg.InputText('', key='pass', password_char='*')],  
    [sg.Button('Close')]
    #[sg.Button('Exit', image_data=red_button, button_color=('white', sg.COLOR_SYSTEM_DEFAULT), border_width=0)]
    ]

window = sg.Window('AlcoLock', layout, default_element_size=(40, 1), grab_anywhere=False)
window.Finalize()
plt.figure() 
password = ''
table = pd.read_csv("data\Alcolock.csv")


while True:
    event, values = window.read()
    # if(table.equals(pd.read_csv("data\Alcolock.csv"))):
    #     print("Same")
    #     event = '_PLOT_'
    # else:
    #     print("Changed")

    status = table["alcohol_level"].iloc[-1]
    if(status < 10):
        window.Element('_SITES_').Update([])
        unblock_write(blocked_sites)
    if(status < 15 and status >= 10):
        window.Element('_SITES_').Update(m_blocked_sites)
        unblock_write(blocked_sites)
        block_write(m_blocked_sites)
    if(status >= 15):
        window.Element('_SITES_').Update(blocked_sites)
        block_write(blocked_sites) 
    if event in [None, 'Exit']:
        unblock_write(blocked_sites) 
        window.close()
        break

    elif(event == '_PLOT_'): 
        table = pd.read_csv("data\Alcolock.csv")
        table.plot(x='timestamp')
        output = None
        if(status < 10):
            output = "You are not drunk!"
        elif(status < 15 and status >= 10):
            output = "You are slightly drunk!"
        elif(status >= 15):
            output = "You are very drunk!"
        matplotlib.pyplot.title(output)
        matplotlib.pyplot.hlines(10, 0, 10, colors='k', linestyles='solid') #these will be the level at which not drunk and drunk
        matplotlib.pyplot.hlines(15, 0, 10, colors='k', linestyles='solid') #ie inbetween is tipsy so some websites are blocked
        fig = plt.gcf()
        DPI = fig.get_dpi()
        
        fig.set_size_inches(404 * 2 / float(DPI), 404 / float(DPI))
        
        plt.grid()
        draw_figure(window.FindElement('fig_cv').TKCanvas, fig)
    elif(event == 'Close'):
        event, values = window.read()
        password = values['pass']
        unblock_write(blocked_sites)
        window.close()
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
        

#email if program closed after 1am
#if(time after 1am)
port = 587  # For starttls
smtp_server = "smtp.gmail.com"
sender_email = "rishilpatel14@gmail.com"
receiver_email = "rpp3618@ic.ac.uk"
password = password
message = """\
Subject: Hi there

Hello I have woken up with a...
Thank you for your consideration!
Kind Regards,
This message is sent from Python."""

context = ssl.create_default_context()
with smtplib.SMTP(smtp_server, port) as server:
    server.ehlo()  # Can be omitted
    server.starttls(context=context)
    server.ehlo()  # Can be omitted
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)