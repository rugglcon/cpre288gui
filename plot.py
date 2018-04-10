import matplotlib.pyplot as plt
import numpy as np
import math

class Plotter():
    def __init__(self):
        self.objlist = []

    def add_object(self, angle, distance, width):
        tmpobj = {
            'x': np.cos(np.deg2rad(angle)) * distance + (width / 2),
            'y': np.sin(np.deg2rad(angle)) * distance + (width / 2),
            'r': width / 2
        }
        circle = plt.Circle((tmpobj["x"], tmpobj["y"]), tmpobj["r"], color='r', fill=True)
        self.objlist.append(circle)

    def draw(self, filename=None):
        fig, ax = plt.subplots()
        ax.set_xlim((-80, 80))
        ax.set_ylim((0, 80))
        for obj in self.objlist:
            ax.add_artist(obj)

        if filename is None:
            plt.show()
        else:
            fig.savefig(filename)
