from machine import Pin

class DisplayPins:
    def __init__(self, cs, dc, rst, busy):
        self.cs = Pin(cs, Pin.OUT)
        self.dc = Pin(dc, Pin.OUT)
        self.rst = Pin(rst, Pin.OUT)
        self.busy = Pin(busy, Pin.IN)