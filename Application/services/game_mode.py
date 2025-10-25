from models.flash_card import FlashCard
from models.game import Game
from models.hardware import Hardware
import urandom
import uasyncio
from images import france
import framebuf
import gui.core.writer as writer
from gui.fonts import courier20 
from gui.widgets.textbox import Textbox

class GameMode:
    def __init__(self, hardware: Hardware, game: Game, is_flipped: bool):
        # Wire up hardware
        self.hardware = hardware
        self.is_busy = True

        self.image_bytes = france.image_bytes[6:]
        self.cards = game.cards
        self.current_card_index = 0
        self.card_count = len(self.cards)
        self.correct_answers = 0
        self.is_flipped = is_flipped

        hardware.on_green_button_press += self._correct_answer_registered
    
    def _shuffle_cards(self):
        """Shuffles a list in-place using the Fisher-Yates algorithm."""
        n = len(self.cards)
        for i in range(n - 1, 0, -1):
            # Pick a random index j from 0 to i (inclusive)
            j = urandom.randrange(i + 1)
            # Swap the elements at positions i and j
            self.cards[i], self.cards[j] = self.cards[j], self.cards[i]

    def _advance(self):
        self.current_card_index += 1
        if self.current_card_index >= self.card_count:
            uasyncio.create_task(self._output_results())
        else:
            uasyncio.create_task(self._show_current_card())

    def _correct_answer_registered(self):
        if self.is_busy:
            return
        
        self.correct_answers += 1
        self._advance()

    def _incorrect_answer_registered(self):
        if self.is_busy:
            return
        
        self._advance()

    def _paint_background_image(self, image_bytes):
        img_fb = framebuf.FrameBuffer(image_bytes, 296, 128, framebuf.MONO_HLSB)
        self.hardware.primary_display.blit(img_fb, 0, 0)
        self.hardware.secondary_display.blit(img_fb, 0, 0)

    def _show_flash_card(self, display, text):
        wri = writer.Writer(display, courier20)
        primary_text_width = wri.stringlen(text)
        start_x = (display.width - primary_text_width) // 2
        start_y = (display.height - courier20.height()) // 2
        wri.set_textpos(display, start_y, start_x)
        wri.printstring(text)

    async def _show_flash_cards(self, image_bytes, front, back):
        self._paint_background_image(image_bytes)
        self._show_flash_card(self.hardware.primary_display, front)
        self._show_flash_card(self.hardware.secondary_display, back)

        await self.hardware._update_displays()
    
    async def _show_results(self, image_bytes, correct_answers, total_cards):
        self._paint_background_image(image_bytes)
        self._show_flash_card(self.hardware.primary_display, "Finished")
        self._show_flash_card(self.hardware.secondary_display, f"{correct_answers}/{total_cards}")
        
    async def _prime_displays(self, image_bytes: bytearray):
        """Outputs the image across both screens for priming purposes, readying it for partial display"""
        # Load the image into a frame buffer
        img_fb = framebuf.FrameBuffer(image_bytes, 296, 128, framebuf.MONO_HLSB)

        self.hardware.primary_display.blit(img_fb, 0, 0)
        self.hardware.secondary_display.blit(img_fb, 0, 0)
        
        await self.hardware._update_displays()

        # Partial refresh of the screens with the same image
        self.hardware.primary_display._full = False
        self.hardware.secondary_display._full = False
        
        await self.hardware._update_displays()

    async def _output_results(self):
        self.is_busy = True
        try:
            await self._show_flash_cards(self.image_bytes, f"{self.correct_answers}/{self.card_count}", "")
            await self.hardware.sleep()
        finally:
            self.is_busy = False

    async def _show_current_card(self):
        self.is_busy = True
        try:
            card = self.cards[self.current_card_index]
            front = card.back if self.is_flipped else card.front
            back = card.front if self.is_flipped else card.back
            await self._show_flash_cards(self.image_bytes, front, back)
        finally:
            self.is_busy = False

    async def start_game(self):
        # Shuffle the cards
        self._shuffle_cards()

        # We need to "prime" the ePaper displays
        await self._prime_displays(self.image_bytes)
        await self._show_current_card()

        self.is_busy = False


