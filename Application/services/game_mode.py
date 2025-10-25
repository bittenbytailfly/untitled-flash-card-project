from models.flash_card import FlashCard
from models.game import Game
from models.hardware import Hardware
import urandom
import uasyncio
from images import france
import framebuf
import gui.core.writer as writer
from fonts import indie_flower50, indie_flower45, indie_flower40, indie_flower35, indie_flower30, indie_flower25, indie_flower20
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

        self.fonts_by_size = [
            indie_flower50,
            indie_flower45,
            indie_flower40,
            indie_flower35,
            indie_flower30,
            indie_flower25,
            indie_flower20,
        ]
        self.max_text_width = 230

        self.hardware.on_green_button_press += self._correct_answer_registered
        self.hardware.on_red_button_press += self._incorrect_answer_registered
    
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
        """
        Finds the largest possible font that fits within the max width
        and draws the text centered on the display.
        """
        selected_font = None # This will hold the font we choose

        # 1. Loop through fonts from largest to smallest
        for font in self.fonts_by_size:
            # Create a temporary writer just for measuring
            temp_wri = writer.Writer(display, font)
            text_width = temp_wri.stringlen(text)

            # 2. Check if the text fits
            if text_width <= self.max_text_width:
                selected_font = font
                break # Found a font that fits, so we stop the loop

        # 3. If no font fits (very long text), default to the smallest one
        if selected_font is None:
            selected_font = self.fonts_by_size[-1] # The last font in the list

        # 4. Now, create the final writer and draw the text
        final_wri = writer.Writer(display, selected_font)
        
        # Recalculate width and position for final centering
        final_width = final_wri.stringlen(text)
        start_x = (display.width - final_width) // 2
        start_y = (display.height - selected_font.height()) // 2
        writer.Writer.set_textpos(display, start_y, start_x)
        
        final_wri.printstring(text)

    async def _show_flash_cards(self, image_bytes, front, back):
        self._paint_background_image(image_bytes)
        self._show_flash_card(self.hardware.primary_display, front)
        self._show_flash_card(self.hardware.secondary_display, back)

        await self.hardware._update_displays()
        
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
            # Calculate the score percentage
            if self.card_count > 0:
                percentage = (self.correct_answers / self.card_count) * 100
            else:
                percentage = 0
                
            # Get the encouraging message
            message = self._get_encouragement_message(percentage)

            await self._show_flash_cards(self.image_bytes, message, f"{self.correct_answers}/{self.card_count}")
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

    def _get_encouragement_message(self, percentage: float) -> str:
        """Returns a randomized string based on the final score percentage."""
        
        if percentage == 100:
            messages = ["Nailed It!", "Perfect Score!", "Incredible!"]
            return urandom.choice(messages)
        
        elif percentage >= 90:
            messages = ["Excellent!", "Awesome Job!", "Wow!"]
            return urandom.choice(messages)
            
        elif percentage >= 70:
            messages = ["Great Work!", "Very Impressive!", "Well Done!"]
            return urandom.choice(messages)
            
        elif percentage >= 50:
            messages = ["Solid Effort!", "Nice One!", "Good Job!"]
            return urandom.choice(messages)
            
        elif percentage > 0:
            messages = ["Keep practicing!", "You've got this!", "Don't give up!"]
            return urandom.choice(messages)
            
        else:  # This covers the 0% case
            messages = ["Better luck next time!", "A fresh start!", "Let's try again!"]
            return urandom.choice(messages)

    async def start_game(self):
        # Shuffle the cards
        self._shuffle_cards()

        # We need to "prime" the ePaper displays
        await self._prime_displays(self.image_bytes)
        await self._show_current_card()

        self.is_busy = False


