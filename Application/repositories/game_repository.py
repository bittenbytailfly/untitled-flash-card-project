from models.game import Game
from models.flash_card import FlashCard

class GameRepository:
    def __init__(self) -> None:
        pass

    def get_game(self, game_id: str):
        # TODO: Actually get the game from some sort of DB
        cards = [
            FlashCard("Lundi", "Monday"),
            FlashCard("Mardi", "Tuesday"),
            FlashCard("Mercredi", "Wednesday"),
            FlashCard("Jeudi", "Thursday"),
            FlashCard("Vendredi", "Friday"),
            FlashCard("Samedi", "Saturday"),
            FlashCard("Dimanche", "Sunday")
        ]
        return Game(None, cards)
