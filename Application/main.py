import time
from machine import Pin, SPI
import drivers.ePaper2in9 as epaper
import gui.core.writer as writer
from gui.fonts import courier20 
from gui.widgets.textbox import Textbox
from images import france
import framebuf
from picozero import Button

# --- Hardware Setup ---
spi = SPI(1, baudrate=4000_000, sck=Pin(10), mosi=Pin(11))
correct_button = Button(28)

# 2. Define unique pins for Screen A
cs_a = Pin(9, Pin.OUT)
dc_a = Pin(8, Pin.OUT)
rst_a = Pin(12, Pin.OUT)
busy_a = Pin(13, Pin.IN)

# 3. Define unique pins for Screen B
cs_b = Pin(17, Pin.OUT)
dc_b = Pin(18, Pin.OUT)
rst_b = Pin(19, Pin.OUT)
busy_b = Pin(20, Pin.IN)


# --- Global State Variables ---
card_index = 0
showing_answer = False

print("Initializing display in PORTRAIT mode...")
# Create the display object in its default portrait mode
epd = epaper.EPD(spi, cs_a, dc_a, rst_a, busy_a, landscape=True)
epd2 = epaper.EPD(spi, cs_b, dc_b, rst_b, busy_b, landscape=True)

# Load the image data AND SLICE OFF THE 6-BYTE HEADER
image_bytes = france.image_bytes[6:]

# Create the framebuffer with the corrected data
img_fb = framebuf.FrameBuffer(image_bytes, 296, 128, framebuf.MONO_HLSB)

epd.blit(img_fb, 0, 0)
epd.show()
epd.sleep()

epd2.blit(img_fb, 0, 0)
epd2.show()
epd2.sleep()

print("--- Phase 2: Starting App in Partial Mode ---")
epd_partial = epaper.EPD(spi, cs_a, dc_a, rst_a, busy_a, landscape=True, full=True)
wri = writer.Writer(epd_partial, courier20)

epd2_partial = epaper.EPD(spi, cs_b, dc_b, rst_b, busy_b, landscape=True, full=True)
wri2 = writer.Writer(epd2_partial, courier20)

# Prime the partial object's buffer with the background image
epd_partial.blit(img_fb, 0, 0)
epd2_partial.blit(img_fb, 0, 0)

#time.sleep(5)

tb = Textbox(wri, 55, 50, 150, 1, bdcolor=False) 
tb.append("Mercredi")

tb2 = Textbox(wri2, 55, 50, 150, 1, bdcolor=False) 
tb2.append("Wednesday")
    
# Perform the fast partial update
epd_partial.show()
    
# Perform the fast partial update
epd2_partial.show()

def on_button_press():
    print(f"Button pressed!")
    
    # --- Update Screen A ---
    tb = Textbox(wri, 55, 50, 150, 1, bdcolor=False) 
    tb.append("Lundi")
    epd_partial.show()

    # --- Update Screen B ---
    tb2 = Textbox(wri2, 55, 50, 150, 1, bdcolor=False) 
    tb2.append("Monday")
    epd2_partial.show()

# --- Main Program ---
time.sleep(1)
correct_button.when_activated = on_button_press