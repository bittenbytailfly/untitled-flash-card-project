from machine import Pin
from models.display_pins import DisplayPins
from machine import Pin, SPI
import drivers.ePaper2in9 as epaper
from picozero import Button
from models.display_pins import DisplayPins
from models.event import Event
import framebuf
import uasyncio

class Hardware:
    def __init__(self):
        # Initialize Displays
        self._spi = SPI(1, baudrate=2000_000, sck=Pin(10), mosi=Pin(11))
        self._primary_display_pins = DisplayPins(cs=9, dc=8, rst=12, busy=13)
        self._secondary_display_pins = DisplayPins(cs=17, dc=18, rst=19, busy=20)

        self.primary_display = epaper.EPD(self._spi, self._primary_display_pins.cs, self._primary_display_pins.dc, self._primary_display_pins.rst, self._primary_display_pins.busy, landscape=True, asyn=True)
        self.secondary_display = epaper.EPD(self._spi, self._secondary_display_pins.cs, self._secondary_display_pins.dc, self._secondary_display_pins.rst, self._secondary_display_pins.busy, landscape=True, asyn=True)

        # Define Events
        self.on_green_button_press = Event()

        # Initialize Buttons
        self._green_button = Button(28, bounce_time=0.05)
        self._green_button.when_activated = self._green_button_handler
    
    async def _update_displays(self):
        self.primary_display.show()
        self.secondary_display.show()

        await uasyncio.gather(
            self.primary_display.wait(),
            self.secondary_display.wait()
        )

    async def sleep(self):
        self.primary_display.sleep()
        self.secondary_display.sleep()

    def _green_button_handler(self):
        self.on_green_button_press()
