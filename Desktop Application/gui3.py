#Importing the necessary libraries.

import tkinter as tk
import matplotlib
import os
import matplotlib.pyplot as plt
import csv
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import datetime
import PySimpleGUI as sg
import tkinter as Tk
from PIL import Image, ImageTk, ImageSequence

from blocker.website_control import block_write, unblock_write
from Emails.email_sender import send_email

import subprocess
import string


matplotlib.rc('figure', max_open_warning = 0)
glass_image = 'iVBORw0KGgoAAAANSUhEUgAAABUAAAAjCAIAAAD0VtZxAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAKzSURBVEhLpZbNUtswEMd3JfkrxgRKTDscoLee4Un6Kn2Tvknfo5fe6AwzzIRDmUmbpDSpndiytF3JhgCdKfb0d3A0K/13tauvYFmW8B880VdVtd1uq7oGAkL+ABEhw+OABIogCJIkCcOwE7B9Npv9LDYqGSXpCFB05n/AXq0pit9Q1yf5RKzKTZimSZr2EjM8GSnTbJ+knM/neD2dxkfHerMpi7Xz3Y4AlFKi8B4JLFlrDOfE+SB3I2bjA06Gfi1xejMNXh37cdzhxnj9IwiMZSP3sSPiJqMEKARVroUU0lt4hI/+TMwgzxekoIZn0Zm6UVxIEcexb79MLN1CtLgWgVIKV6vVGlTr0ICoQC1W5q7QZWUaYyxxD0WBSkI5ToOjTKGtkWykhCB7oNCt/11Dny6d/u/cd9z3uSoAScD378whu2GT1vXlgr7O7XRZzzdQGqlRGZDWlQT5y20jFNt/lHS90FcL4vFNo1nr4n+7W338suecv4SvMAhOieDDRXEyznz8qvL2l+EMXOG8G6NdfKcXrWEgvKP46/XsdaAHd668xOml4J+HrdELXn/Ble3iI0aw8fa+SBfcrafTcznfZMqZe6Ow4i3ADaePgug0310JfQip9vJWH0dnea/1f2CyF7THzuuj6CgeUj+CyX536nz+XD8zoH58UUwyFQSuZE7P1PW2bfSBE+f4fJdyu9P338Ithyk91pPRjW/0JSD7WI+yO1p9CUELf7t285d+MftD/vAxnZ73Mw45hdZ0+e7ixzjgIdT8xnnu9ULmyYAczLP4vAXP8rh/AsZfHsxOf5rv9Z+AuA+1e79vZ981inT/8KYafb5a3q6xhohPBTsNQGdqe/52fH4SNcXSlEWoxOs8f6JvYb+6qouy0Lqx7p717z+RFIJf/tFo5P8N7HiuHwbAH0ChJnb7ImCxAAAAAElFTkSuQmCC'

#Store path to readings csv file as constant variable
READINGS_PATH = "Readings_data\Alcolock.csv"
#Path to chrome browser on windows laptop.
CHROME = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"


#Read in from relevant files the lists of sites that will be blocked under different scenarios:
#   - blocked_sites contains the sites that are blocked when the user is "very drunk" (red region of the graph display).
#   - m_blocked_sites has sites blocked when the user is "slightly drunk" (yellow region of the graph display).
# Hence, while the program is running, a drunk user cannot modify any of the sites listed to block.
blocked_sites = []
m_blocked_sites = []
with open("blocker/sites.txt", "r+") as f:
    blocked_sites = f.read().splitlines()
with open("blocker/medium.txt", "r+") as f:
    m_blocked_sites = f.read().splitlines()

#Print to console to test
print(blocked_sites)
print(m_blocked_sites)


#to embed the matplotlib graph (parameter fig) into the gui (parameter canvas)
def draw_figure(canvas, fig):
    #Get rid of the current existing graph in the GUI
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    #Add the new graph in
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=1)

    def on_key_press(event):
        key_press_handler(event, canvas, toolbar)
        canvas.TKCanvas.mpl_connect("key_press_event", on_key_press)
    return

sg.ChangeLookAndFeel('Purple') #change colour

#Describes the layout of the GUI - text elements, windows, graphs etc.

centred =  [[sg.Text('AlcoLock', size=(30, 1), justification='center', font=("Helvetica", 25), relief=sg.RELIEF_RIDGE)],
            [sg.Button('Take reading',key='_PLOT_',bind_return_key=True)],
            [sg.Canvas()],
            #[sg.T('Figure:')],

            #The graph display
            [sg.Column(
                layout=[
                    [sg.Canvas(key='fig_cv',
                               size=(400 * 2, 400) #set size for graph
                               )]
                ],
                background_color='#DAE0E6',
                pad=(0, 0)
            )],
            #The displayed list of blocked sites
            [sg.T('Blocked sites')],
            [sg.Listbox(blocked_sites, size=(80, len(blocked_sites)), key='_SITES_')],
            #The icon displaying water intake
            [sg.ProgressBar(1,size=(20,20),key='_WATER_')],
            [sg.Button(key='_GLASS_',image_data=glass_image)],
            #The link to the site on chrome that aids sobering up
            [sg.Button('How to sober up fast',key='_CHROME_')]
            ]

layout = [
    [sg.Column(centred, element_justification='center')],
    [sg.Button('Close',key='_CLOSE_')]
    #[sg.Button('Exit', image_data=red_button, button_color=('white', sg.COLOR_SYSTEM_DEFAULT), border_width=0)]
    ]

#Instantiate the GUI
window = sg.Window('AlcoLock', layout, default_element_size=(40, 1), grab_anywhere=False,return_keyboard_events= True)

#Define various constants used in the loop below.
water = window.FindElement('_WATER_')
#How full the water progress bar is
glass = 0
#Used to record how many readings are currently in the csv file that is displayed as the graph.
no_of_readings = 0
#Indicates the last time at which the computer hosts file was written to to enforce site blocking.
last_write_time = 0
#Bool variable that decides whether we perform an unblock_write() on the hosts file. Repeatedly performing
#unblock_write() and block_write() consecutively can result in permission denied to modify the hosts file.
#This variable is introduced to combat this: see line 209 for usage.
unblock_needed = False
#Maximum time difference between two successive writes to the host file. Over-frequent writes result
#in the program being denied write access.
TIME_THRESHOLD = 5

#Define alcohol reading thresholds:
SLIGHTLY_DRUNK = 4000
VERY_DRUNK = 8000
UPPER_LIMIT = 15000

#Set up window and matplotlib plotting
window.Finalize()
plt.figure()
password = ''

#Obtain the initial set of readings as a pandas dataframe.
table = pd.read_csv(READINGS_PATH)

#GUI loop that listens for events
while True:
    event, values = window.read()
    print("Event: ", event)

    status = table["alcohol_level"].iloc[-1]
    print("Status: ", status)
    print(table)

    #--------------------EVENT CASES------------------------------------------------------------------------------

    #In case window is closed, unblock all sites
    if event in [None, 'Exit']:
        unblock_write(blocked_sites)
        window.close()
        break

    #In case the "Close" button is pressed and the user is highly drunk, unblock sites and send out emails.
    elif(event == '_CLOSE_'):
        if status > VERY_DRUNK: #if very drunk
            send_email()
        unblock_write(blocked_sites)
        window.close()
        break

    #When we click on the glass icon update the water progress bar.
    elif(event == '_GLASS_'):
        print("water")
        glass+=1
        water.UpdateBar(glass,5)

    #In case of a key press we update the graph if new readings have arrived.
    elif(event in string.printable):
        table = pd.read_csv(READINGS_PATH)
        #If the below condition is true, it means that the server has written a new entry to the csv file.
        if(len(table) != no_of_readings):
            no_of_readings = len(table)
            #Plot the data
            table.plot(x='timestamp')
            #Obtain the latest new reading of alcohol level
            status = table["alcohol_level"].iloc[-1]
            output = None
            #Based on the reading, set the on-screen message
            if(status < SLIGHTLY_DRUNK):
                output = "You are not drunk!"
            elif(status < VERY_DRUNK and status >= SLIGHTLY_DRUNK):
                output = "You are slightly drunk!"
            elif(status >= VERY_DRUNK):
                output = "You are very drunk!"
            #Plot the figure based on the data - set up additional graphics on the figure.
            matplotlib.pyplot.title(output)
            #Lines to demarcate the different categories of drunkenness.
            matplotlib.pyplot.hlines(10, 0, len(table.index), colors='g', linestyles='solid') #these will be the level at which not drunk and drunk
            matplotlib.pyplot.hlines(15, 0, len(table.index), colors='r', linestyles='solid') #ie inbetween is tipsy so some websites are blocked
            #Colours that fill in the gaps to denote the regions.
            matplotlib.pyplot.fill_between([0,len(table.index)], VERY_DRUNK, UPPER_LIMIT, facecolor='r', interpolate=True)
            matplotlib.pyplot.fill_between([0,len(table.index)], SLIGHTLY_DRUNK, VERY_DRUNK, facecolor='y', interpolate=True)
            matplotlib.pyplot.fill_between([0,len(table.index)], 0, SLIGHTLY_DRUNK, facecolor='g', interpolate=True)

            #Set up figure, adjust size, plot and embed in the GUI.
            fig = plt.gcf()
            plt.grid(b=None)
            DPI = fig.get_dpi()

            fig.set_size_inches(404 * 2 / float(DPI), 404 / float(DPI))

            plt.grid()
            draw_figure(window.FindElement('fig_cv').TKCanvas, fig)

    #In case the 'How to Sober Up' link is clicked.
    elif(event == '_CHROME_'):
        try:
            sp = subprocess.Popen([CHROME, 'https://www.wikihow.com/Sober-Up-Fast'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            print ("Exception opening chrome: " + str(e) + ". Check that Google Chrome is installed.")

    #----------------------------END OF EVENT CASES-------------------------------------------------------------------------------------------------------------------

    #Below section enforces blocking of sites whenever the event-driven loop runs an iteration
    time_now = time.time()
    #Ensure that successive writes to the hosts file must have a pre-set threshold between them.
    #Over-frequent writing results in access being denied.
    if time_now - last_write_time >= TIME_THRESHOLD:
        last_write_time = time_now
        if(status < SLIGHTLY_DRUNK):
            print("nothing")
            window.Element('_SITES_').Update([])
            #unblock_needed not required here as consecutive unblock writes are ok.
            unblock_write(blocked_sites)
        elif(status < VERY_DRUNK and status >= SLIGHTLY_DRUNK):
            print("medium")
            window.Element('_SITES_').Update(m_blocked_sites)
            #We want to unblock websites in the host file on first iteration and then after that
            #only write in the file the list of sites to block on each iteration. We want to avoid
            #performing unblock_write() and block_write() together as computer security does not like.
            if unblock_needed:
                #Find those sites that are no longer needed i.e can be unblocked.
                sites_to_unblock = list(set(blocked_sites).difference(m_blocked_sites))
                unblock_write(sites_to_unblock)
                unblock_needed = False
            else:
                #Block the sites that have to be blocked.
                block_write(m_blocked_sites)
        elif(status >= VERY_DRUNK):
            print("all")
            window.Element('_SITES_').Update(blocked_sites)
            #Consecutive block writes are ok.
            block_write(blocked_sites)
            unblock_needed = True
