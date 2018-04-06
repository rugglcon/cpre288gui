import platform

builder = {}
if platform.release() == "Windows":
    import gtk
elif platform.release() == "Linux":
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk

import os
import socket
import sys

builder = Gtk.Builder()
builder.add_from_file(os.path.join(sys._MEIPASS, "final_project.glade"))
CON = connect()

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
    "onDelete": Gtk.main_quit,
    "doScan": do_scan,
    "doStart": start,
    "doStop": stop,
    "doTurnLeft": turn_left,
    "doTurnRight": turn_right,
    "toggleReverse": toggle_reverse
}

builder.get_object("main-window").show_all()
builder.connect_signals(handlers)
Gtk.main()
