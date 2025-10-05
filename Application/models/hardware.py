from machine import Pin
from models.display_pins import DisplayPins
from machine import Pin, SPI
import drivers.ePaper2in9 as epaper
from picozero import Button
from models.display_pins import DisplayPins
from models.event import Event
import framebuf
import uasyncio
import gui.core.writer as writer
from gui.fonts import courier20 
from gui.widgets.textbox import Textbox

class Hardware:
    def __init__(self):
        # Initialize Displays
        self.__spi__ = SPI(1, baudrate=2000_000, sck=Pin(10), mosi=Pin(11))
        self.__primary_display_pins__ = DisplayPins(cs=9, dc=8, rst=12, busy=13)
        self.__secondary_display_pins__ = DisplayPins(cs=17, dc=18, rst=19, busy=20)
        self.__primary_display__ = epaper.EPD(self.__spi__, self.__primary_display_pins__.cs, self.__primary_display_pins__.dc, self.__primary_display_pins__.rst, self.__primary_display_pins__.busy, landscape=True, asyn=True)
        self.__secondary_display__ = epaper.EPD(self.__spi__, self.__secondary_display_pins__.cs, self.__secondary_display_pins__.dc, self.__secondary_display_pins__.rst, self.__secondary_display_pins__.busy, landscape=True, asyn=True)

        # Define Events
        self.on_green_button_press = Event()

        # Initialize Buttons
        self._green_button = Button(28, bounce_time=0.05)
        self._green_button.when_activated = self._green_button_handler
    
    def __paint_background_image__(self, image_bytes):
        img_fb = framebuf.FrameBuffer(image_bytes, 296, 128, framebuf.MONO_HLSB)
        self.__primary_display__.blit(img_fb, 0, 0)
        self.__secondary_display__.blit(img_fb, 0, 0)

    def __show_flash_card__(self, display, text):
        wri = writer.Writer(display, courier20)
        primary_text_width = wri.stringlen(text)
        start_x = (display.width - primary_text_width) // 2
        start_y = (display.height - courier20.height()) // 2
        wri.set_textpos(display, start_y, start_x)
        wri.printstring(text)

    async def __update_displays__(self):
        self.__primary_display__.show()
        self.__secondary_display__.show()

        await uasyncio.gather(
            self.__primary_display__.wait(),
            self.__secondary_display__.wait()
        )

    async def show_flash_cards(self, image_bytes, front, back):
        self.__paint_background_image__(image_bytes)
        self.__show_flash_card__(self.__primary_display__, front)
        self.__show_flash_card__(self.__secondary_display__, back)

        await self.__update_displays__()
        
    async def prime_displays(self, image_bytes: bytearray):
        """Outputs the image across both screens for priming purposes, readying it for partial display"""
        # Load the image into a frame buffer
        img_fb = framebuf.FrameBuffer(image_bytes, 296, 128, framebuf.MONO_HLSB)

        self.__primary_display__.blit(img_fb, 0, 0)
        self.__secondary_display__.blit(img_fb, 0, 0)
        
        await self.__update_displays__()

        # Partial refresh of the screens with the same image
        self.__primary_display__._full = False
        self.__secondary_display__._full = False
        
        await self.__update_displays__()

    async def sleep(self):
        self.__primary_display__.sleep()
        self.__secondary_display__.sleep()

    def _green_button_handler(self):
        self.on_green_button_press()
