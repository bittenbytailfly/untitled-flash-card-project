import time
from machine import Pin, SPI
import drivers.ePaper2in9 as epaper
import gui.core.writer as writer
from gui.fonts import courier20 
from gui.widgets.textbox import Textbox
from images import france
import framebuf
from picozero import Button
from models.display_pins import DisplayPins
from models.hardware import Hardware
import uasyncio
from services.game_mode import GameMode
from models.game import Game
from repositories.game_repository import GameRepository

async def main():
    hw = Hardware()
    gr = GameRepository()
    gm = GameMode(hw, gr.get_game("french_to_english"), False)

    await gm.start_game()
    while True:
        await uasyncio.sleep(1)

try:
    uasyncio.run(main())
except KeyboardInterrupt:
    print("Program Stopped")
