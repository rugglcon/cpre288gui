import pygtk
pygtk.require("2.0")
import gtk, gobject

import json
import os
import PIL
import socket
import sys
import threading
import time

import plot

gobject.threads_init()

builder = gtk.Builder()
if getattr(sys, "frozen", False):
    builder.add_from_file(os.path.join(sys._MEIPASS, "final_projectgtk2.glade"))
else:
    builder.add_from_file("final_projectgtk2.glade")

class Client():
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.reverse = False
        self.command_lock = threading.Lock()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.addr, self.port))

    def close(self, widget, data):
        self.s.close()
        gtk.main_quit()

    def send_command_thread(self, cmd):
        thread = threading.Thread(target=self.send_command, args=cmd)
        thread.start()

    def send_command(self, cmd):
        self.s.send(cmd)

        timeout = 0

        if cmd.isdigit():
            self.delete_objects()
            return

        if cmd[0] == "s":
            timeout = 10
            time.sleep(3)
        elif cmd[0] == "g":
            timeout = 6
        elif cmd[0] == "b":
            timeout = 0
        elif cmd[0] == "h":
            timeout = 0
        elif cmd[0] == "l":
            timeout = 6
            time.sleep(1)
        elif cmd[0] == "r":
            timeout = 6
            time.sleep(1)
        elif cmd[0] == "p":
            timeout = 6
            time.sleep(1)
        elif cmd[0] == "n":
            timeout = 6
            time.sleep(1)
        elif cmd[0] == "e":
            timeout = 6
            time.sleep(1)

        if timeout == 0:
            self.delete_objects()
            return

        self.s.setblocking(0)
        data = []
        cur_data = ""
        msg = ""

        start = time.time()
        while True:
            if data and time.time() - start > timeout:
                msg = "".join(data)
                break
            elif time.time() - start > timeout * 2:
                msg = '{"error": 1}'

            try:
                response = self.s.recv(4096)
                cur_data = response.decode("ascii")
                if cur_data:
                    data.append(cur_data)
                    start = time.time()
                else:
                    time.sleep(0.1)
            except:
                pass
        self.s.settimeout(None)
        if cmd[0] == "s":
            self.parse_objects(msg)
        else:
            self.parse_response(msg)

    def delete_objects(self):
        builder.get_object("obj-list").foreach(gtk.Widget.destroy)

    def parse_response(self, msg):
        print(msg)
        try:
            json_msg = json.loads(msg)
        except Exception:
            print("something went wrong, message could be formatted wrong?")
            return

        if json_msg["error"] == 1:
            print("something went wrong :/")
            return

        self.delete_objects()
        builder.get_object("left-bumper").set_text("Left Bumper: " + str(json_msg["bump_left"]))
        builder.get_object("right-bumper").set_text("Right Bumper: " + str(json_msg["bump_right"]))
        builder.get_object("cliff-left").set_text("Left: " + str(json_msg["cliff_left"]))
        builder.get_object("cliff-right").set_text("Right: " + str(json_msg["cliff_right"]))
        builder.get_object("cliff-left-front").set_text("Left Front: " + str(json_msg["cliff_front_left"]))
        builder.get_object("cliff-right-front").set_text("Right Front: " + str(json_msg["cliff_front_right"]))
        builder.get_object("cliff-signal-left").set_text("Left: " + str(json_msg["cliff_signal_left"]))
        builder.get_object("cliff-signal-right").set_text("Right: " + str(json_msg["cliff_signal_right"]))
        builder.get_object("cliff-signal-left-front").set_text("Left Front: " + str(json_msg["cliff_signal_front_left"]))
        builder.get_object("cliff-signal-right-front").set_text("Right Front: " + str(json_msg["cliff_signal_front_right"]))

    def parse_objects(self, msg):
        print(msg)
        try:
            json_msg = json.loads(msg)
        except Exception:
            print("something went wrong, message could be formatted wrong?")
            return

        if json_msg["error"] == 1:
            print("something went wrong :/")
            return

        self.delete_objects()
        obj_window = builder.get_object("obj-list")
        data = json_msg["data"]
        builder.get_object("ping-sensor").set_text("PING sensor: " + str(data["ping"]))
        builder.get_object("ir-sensor").set_text("IR sensor: " + str(data["ir"]))
        objects = data["objects"]
        plotter = plot.Plotter()
        index = 0
        for obj in objects:
            obj_window.add(gtk.Label("Object " + str(index)))
            obj_window.add(gtk.Label("Distance: " + str(obj["distance"])))
            obj_window.add(gtk.Label("Width: " + str(obj["width"])))
            obj_window.add(gtk.Label("Angle: " + str(obj["angle"])))
            plotter.add_object(obj["angle"], obj["distance"], obj["width"])
            index += 1

        plotter.draw("objects.png")
        basewidth = 500
        img = PIL.Image.open("objects.png")
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
        img.save("objects.png")
        builder.get_object("image1").set_from_file("objects.png")

    def do_scan(self, button):
        print("scanning")
        self.send_command_thread("s")

    def start(self, button):
        speed = builder.get_object("robot-speed").get_text()
        if not self.reverse:
            print("starting forward " + speed)
            self.send_command_thread("g")
        else:
            print("starting backward " + speed)
            self.send_command_thread("b")

    def stop(self, button):
        print("stopping")
        self.send_command_thread("h")

    def turn_left(self, button):
        degrees = builder.get_object("turn-degrees").get_text()
        print("turning left " + degrees)
        if degrees == "90":
            self.send_command_thread('l')
        elif degrees == "45":
            self.send_command_thread('n')
        elif degrees == "180":
            self.send_command_thread('e')

    def turn_right(self, button):
        degrees = builder.get_object("turn-degrees").get_text()
        print("turning right " + degrees)
        if degrees == "90":
            self.send_command_thread('r')
        elif degrees == "45":
            self.send_command_thread('p')
        elif degrees == "180":
            self.send_command_thread('e')

    def toggle_reverse(self, button):
        self.reverse = not self.reverse
        print(self.reverse)

    def do_connect(self, button):
        self.s.close()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.addr, self.port))

client = Client("192.168.1.1", 288)
handlers = {
    "onDelete": client.close,
    "doScan": client.do_scan,
    "doStart": client.start,
    "doStop": client.stop,
    "doTurnLeft": client.turn_left,
    "doTurnRight": client.turn_right,
    "toggleReverse": client.toggle_reverse,
    "onConnect": client.do_connect
}
mock_info = str('''
{
    "error": 0,
    "data": {
        "ping": 30,
        "ir": 32,
        "objects": [
            {
                "distance": 60,
                "width": 8.5,
                "angle": 148
            },
            {
                "distance": 77,
                "width": 6,
                "angle": 60
            },
            {
                "distance": 48,
                "width": 8.5,
                "angle": 10
            }
        ]
    }
}''')
builder.get_object("main-window").set_title("iRobot Command Center")
builder.get_object("main-window").show()
builder.connect_signals(handlers)
#client.parse_response(mock_info)
gtk.main()
