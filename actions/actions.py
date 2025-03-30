from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionStartGame(Action):
    def name(self) -> Text:
        return "action_start_game"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Ensure the game hasn't started yet
        if tracker.get_slot("game_started"):
            dispatcher.utter_message("The game is already in progress!")
            return []

        # Game starting
        dispatcher.utter_message("You find yourself in a dimly lit room with a locked door. A bookshelf stands in the corner.")
        return [SlotSet("game_started", True)]


class ActionExamineBookshelf(Action):
    def name(self) -> Text:
        return "action_examine_bookshelf"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not tracker.get_slot("game_started"):
            dispatcher.utter_message("You haven't started the game yet! Say 'start game' to begin.")
            return []

        dispatcher.utter_message("The bookshelf contains several books. One of them seems oddly placed.")
        return [SlotSet("bookshelf_examined", True)]


class ActionEnterCode(Action):
    def name(self) -> Text:
        return "action_enter_code"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not tracker.get_slot("bookshelf_examined"):
            dispatcher.utter_message("You need to examine the bookshelf first!")
            return []
        
        dispatcher.utter_message("You enter the code. The bookshelf slides open, revealing a hidden passage!")
        return [SlotSet("code_entered", True)]


class ActionWhisperPhrase(Action):
    def name(self) -> Text:
        return "action_whisper_phrase"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not tracker.get_slot("code_entered"):
            dispatcher.utter_message("You don't know the phrase yet!")
            return []
        
        dispatcher.utter_message("You whisper the phrase, and the door unlocks with a click. You have escaped!")
        return [SlotSet("game_started", False)]


class ActionReadBook(Action):
    def name(self) -> Text:
        return "action_read_book"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message("You read the book. It contains a hidden clue!")
        return []


class ActionExaminePainting(Action):
    def name(self) -> Text:
        return "action_examine_painting"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message("The painting reveals a secret message.")
        return []


class ActionGiveHint(Action):
    def name(self) -> Text:
         return "action_give_hint"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        hints = {
            "start": "Look around and examine objects in the room.",
            "bookshelf": "Check if any book looks different from the rest.",
            "code": "There might be something behind the bookshelf.",
            "phrase": "Think about what the game has told you so far."
        }

        if not tracker.get_slot("bookshelf_examined"):
            dispatcher.utter_message(hints["bookshelf"])
        elif not tracker.get_slot("code_entered"):
            dispatcher.utter_message(hints["code"])
        elif not tracker.get_slot("game_started"):
            dispatcher.utter_message("You have already escaped!")
        else:
            dispatcher.utter_message(hints["phrase"])
        
        return []


class ActionGameOver(Action):
    def name(self) -> str:
        return "action_game_over"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Game over! The cursed library remains locked. Try again to escape!")
        return []


class ActionRestartGame(Action):
    def name(self) -> str:
        return "action_restart_game"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="The game will restart. Good luck!")
        return [
            SlotSet("game_started", False),
            SlotSet("bookshelf_examined", False),
            SlotSet("code_entered", False)
        ]
