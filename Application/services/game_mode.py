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
        uasyncio.create_task(self.show_current_card())

    def correct_answer_registered(self):
        self.correct_answers += 1
        self.advance()

    def incorrect_answer_registered(self):
        self.advance()

    async def show_current_card(self):
        card = self.cards[self.current_card_index]
        front = card.back if self.is_flipped else card.front
        back = card.front if self.is_flipped else card.back
        await self.hardware.show_flash_cards(self.image_bytes, front, back)

    async def start_game(self):
        # Shuffle the cards
        self._shuffle_cards()

        # We need to "prime" the ePaper displays
        await self.hardware.prime_displays(self.image_bytes)

        await self.show_current_card()


