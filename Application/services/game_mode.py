from models.flash_card import FlashCard
from models.game import Game
from models.hardware import Hardware
import urandom
import uasyncio
from images import france
import framebuf

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

        hardware.on_green_button_press += self.correct_answer_registered
    
    def _shuffle_cards(self):
        """Shuffles a list in-place using the Fisher-Yates algorithm."""
        n = len(self.cards)
        for i in range(n - 1, 0, -1):
            # Pick a random index j from 0 to i (inclusive)
            j = urandom.randrange(i + 1)
            # Swap the elements at positions i and j
            self.cards[i], self.cards[j] = self.cards[j], self.cards[i]

    def advance(self):
        self.current_card_index += 1
        if self.current_card_index >= self.card_count:
            uasyncio.create_task(self.output_results())
        else:
            uasyncio.create_task(self.show_current_card())

    def correct_answer_registered(self):
        if self.is_busy:
            return
        
        self.correct_answers += 1
        self.advance()

    def incorrect_answer_registered(self):
        if self.is_busy:
            return
        
        self.advance()

    async def output_results(self):
        self.is_busy = True
        try:
            await self.hardware.show_flash_cards(self.image_bytes, f"{self.correct_answers}/{self.card_count}", "")
            await self.hardware.sleep()
        finally:
            self.is_busy = False

    async def show_current_card(self):
        self.is_busy = True
        try:
            card = self.cards[self.current_card_index]
            front = card.back if self.is_flipped else card.front
            back = card.front if self.is_flipped else card.back
            await self.hardware.show_flash_cards(self.image_bytes, front, back)
        finally:
            self.is_busy = False

    async def start_game(self):
        # Shuffle the cards
        self._shuffle_cards()

        # We need to "prime" the ePaper displays
        await self.hardware.prime_displays(self.image_bytes)
        await self.show_current_card()

        self.is_busy = False


