import time
import queue
import threading
from tkinter import *
from tkinter import ttk
from PIL import ImageTk
from GoogleTracking import GoogleTracking, pathGoogle

INITIAL_LATITUDE = 0.0
INITIAL_LONGITUDE = 0.0

ACTUAL_LATITUDE = 0.0
ACTUAL_LONGITUDE = 0.0

SPEED_POSITION = 0

ALTITUDE = 0.0
GEO_SEPARATION = 0.0

LAST_TIME = 0.0
ACTUAL_TIME = 0.0

speedMatrix = []

if __name__ == "__main__":

    windowPanel = Tk()
    windowPanel.title('Speed Panel')
    windowPanel.geometry('500x200')
    windowPanel.resizable(width=True, height=True)

    windowMap = Toplevel()
    windowMap.title('Speed Map')
    windowMap.geometry('640x640')
    windowMap.resizable(width=True, height=True)

#   CREATION OF THE TRACKER_INICIALATION OF THE TRACKER
    tracker = GoogleTracking(INITIAL_LATITUDE, INITIAL_LONGITUDE, ACTUAL_LATITUDE, ACTUAL_LONGITUDE,
                            SPEED_POSITION, LAST_TIME, ACTUAL_TIME, speedMatrix, ALTITUDE, GEO_SEPARATION)

    textKMH = IntVar()
    textKMH.set(0.0)

    # CREATION OF A THREAD IN ORDER TO RUN THE FUNCTION THAT READS DATA FROM THE GPS SENSOR
    # WE USE A QUEUE TO EXCHANGE INFO BETWEEN THE RUNNING THREAD AND THE PANEL
    q = queue.Queue()
    t1 = threading.Thread(target=tracker.read_data, name=tracker.read_data, args=(q,))
    t1.start()

    ttk.Button(windowPanel, text='Exit', command=quit).pack(side=BOTTOM)
    ttk.Button(windowMap, text='Exit', command=quit).pack(side=BOTTOM)

    #CREATION OF GUI LABEL WITH INSIA'S IMAGE
    img = ImageTk.PhotoImage(file= pathGoogle)
    label = ttk.Label(windowMap, image=img)
    label.pack()

while True:

    speedBackground = q.get()  # GETTING THE PANEL COLOUR FROM THE QUEUE
    speed = q.get()  # GETTING THE SPEED FROM THE QUEUE

    print("Velocidad : " + str(speed), "Zona  : " + str(speedBackground))

    textKMH.set(speed)

    ttk.Label(windowPanel, textvariable=textKMH).place(relx=.5, rely=.5, anchor="center")

    # UPDATING INSIA'S IMAGE IN GUI
    img_2 = ImageTk.PhotoImage(file=pathGoogle)
    label.configure(image=img_2)
    label.image = img_2

    if speedBackground == 0:
        windowPanel.configure(bg='black')
    elif speedBackground == 1:
        windowPanel.configure(bg='green')
    elif speedBackground == 2:
        windowPanel.configure(bg='yellow')
    elif speedBackground == 3:
        windowPanel.configure(bg='red')
    else:
        windowPanel.configure(bg='white')

    time.sleep(0.5)
    windowPanel.update()

windowPanel.mainloop()
windowMap.mainloop()