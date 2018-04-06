import pygtk
pygtk.require('2.0')
import gtk

import os
import socket
import sys

builder = gtk.Builder()
if getattr(sys, 'frozen', False):
    builder.add_from_file(os.path.join(sys._MEIPASS, "final_projectgtk2.glade"))
else:
    builder.add_from_file("final_projectgtk2.glade")

REVERSE = False

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('192.168.1.1', 42880))
    return s

def do_scan(button):
    print("scanning")

def start(button):
    if REVERSE:
        print("starting backward")
    else:
        print("starting forward")

def stop(button):
    print("stopping")

def turn_left(button):
    print("turning left")

def turn_right(button):
    print("turning right")

def toggle_reverse(button):
    global REVERSE
    REVERSE = not REVERSE
    print(REVERSE)


handlers = {
    "onDelete": gtk.main_quit,
    "doScan": do_scan,
    "doStart": start,
    "doStop": stop,
    "doTurnLeft": turn_left,
    "doTurnRight": turn_right,
    "toggleReverse": toggle_reverse
}

#CON = connect()
builder.get_object("main-window").show()
builder.connect_signals(handlers)
gtk.main()
