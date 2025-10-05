import time
from machine import Pin, SPI
import drivers.ePaper2in9 as epaper
import gui.core.writer as writer
from gui.fonts import courier20 
from gui.widgets.textbox import Textbox
import urandom
from images import france
import framebuf

# --- Word List & Hardware Setup ---
word_list = ["Pico", "Python", "E-Paper", "Demo", "Hello", "World", "Success"]
spi = SPI(1, baudrate=8000_000, sck=Pin(10), mosi=Pin(11)) # Using a faster baudrate
cs = Pin(9, Pin.OUT)
dc = Pin(8, Pin.OUT)
rst = Pin(12, Pin.OUT)
busy = Pin(13, Pin.IN)

def main():
    # 1. Create the display object, starting in default FULL refresh mode
    epd = epaper.EPD(spi, cs, dc, rst, busy, landscape=True)
    wri = writer.Writer(epd, courier20)

    # 2. Prepare the background image from your file
    image_bytes = france.image_bytes[6:] # Slice the header if needed
    img_fb = framebuf.FrameBuffer(image_bytes, 296, 128, framebuf.MONO_HLSB)

    # 3. Perform an initial full refresh with the background
    print("Performing initial full refresh of background...")
    epd.blit(img_fb, 0, 0)
    epd.show()
    epd.wait_until_ready()

    # 4. Manually switch the display object to PARTIAL refresh mode
    print("Switching to partial refresh mode.")
    epd._full = False
    # important - must "prime" the partial with the image
    epd.show()
    epd.wait_until_ready()

    # --- Main Loop ---
    try:
        while True:
            random_word = urandom.choice(word_list)
            print(f"Displaying: {random_word}")
            
            # A. ERASE old text by re-drawing the background image to the buffer
            epd.blit(img_fb, 0, 0)
            
            # B. DRAW the new text on top of the restored background
            text_width = wri.stringlen(random_word)
            start_x = (epd.width - text_width) // 2
            start_y = (epd.height - courier20.height()) // 2
            writer.Writer.set_textpos(epd, start_y, start_x)
            wri.printstring(random_word)
            
            # C. SHOW the changes using a fast partial update
            epd.show()
            epd.wait_until_ready()

            print("Waiting for 5 seconds...")
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nStopping program.")
        # On exit, do a final full refresh to clear the screen to white
        epd._full = True
        epd.fill(0) # 0 = white, 1 = black
        epd.show()
        epd.wait_until_ready()
        epd.sleep()
        print("Screen cleared and put to sleep.")

# --- Run the application ---
time.sleep(1)
main()