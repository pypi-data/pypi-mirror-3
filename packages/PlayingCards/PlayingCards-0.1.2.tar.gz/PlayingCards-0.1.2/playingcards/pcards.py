"""
A module that generates a box of cards using instances
of a card class. The box of cards can have a variable number of decks,
and can be shuffled or manipulated by removing or placing cards from or in it.
"""

# card class definition

from random import shuffle


class CardClass(object):
    """
    The CardClass class has 2 data members, 
    which identify a card's suit and value.
    """
    def __init__(self, in_suit, in_value):
        if in_suit in range(1, 4 + 1) and in_value in range(1, 13 + 1):    
            self.suit = in_suit
            self.value = in_value
        else:
            self.suit = -1
            self.value = -1     


class BoxClass(object):
    """
    A box of cards consists of a number of decks, 
    which is specified to the BoxClass class as a parameter.
    The BoxClass class initialises 52*in_deck_count instances of 
    CardClass by iterating through the suits and values of a 
    deck of playing cards in_deck_count times.
    """
    def __init__(self, in_deck_count):

        self.card_box = []
        self.max_cards = in_deck_count * 52

        for i in range(0, in_deck_count):
            for suit in range(1, 4 + 1):
                for value in range(1, 13 + 1):
                    new_card = CardClass(suit, value)
                    self.card_box.append(new_card)
                    del new_card

    def shuffle(self):
        """
        Shuffles the box of cards.
        """
        shuffle(self.card_box)

    def deal(self, count_of_cards):
        """
        Deals a specified number of cards by popping 
        them from the deck into a list.
        """
        dealt_list = []

        if count_of_cards <= len(self.card_box):
            for i in range(0, count_of_cards):
                dealt_list.append(self.card_box.pop())

        #Handles the condition where the requested number of cards
        #is greater than what is left in the deck.
        else:
            for i in range(0, len(self.card_box)):
                dealt_list.append(self.card_box.pop())

        return dealt_list

    def place(self, card):
        """
        Places a valid card at the top of a non-full card box.
        Use the return values to check for full, invalid-card or ok conditions.
        """

        if len(self.card_box) == self.max_cards:
            return 'FULL'
        elif card.suit == -1: 
            return 'NOCARD'
        else:
            match = 0
            for i in self.card_box:
                if (card.suit == i.suit and card.value == i.value):
                    match += 1
                    if match == (self.max_cards / 52):
                        return 'DUPLICATE'
                    else: 
                        pass    

            self.card_box.append(card)
            return 'OK'

    def split(self, count_subdecks):
        
        if count_subdecks > self.max_cards:
            return 'MAX'
        else:
            cards_per_deck = self.max_cards // count_subdecks
            remaining_cards = self.max_cards % count_subdecks

            split_box = []

            for i in range(0, count_subdecks):
                subdeck = []
                for j in range(0, cards_per_deck):
                    if len(self.card_box) > 0:
                        subdeck.append(self.card_box.pop())
                    else:
                        break

                split_box.append(subdeck)

            subdeck = []

            for j in range(0, remaining_cards):
                if len(self.card_box) > 0:
                    subdeck.append(self.card_box.pop())
                else:
                    break

            split_box.append(subdeck)
            del subdeck
            return split_box

    def unshuffle(self):
        """
        Sorts the box of cards according to value and suit.    
        """
        self.card_box.sort()


def name_card(card):
    """
    Returns a Dict that contains the names of cards 
    mapped from (1->Spades,2->Hearts,3->Diamonds and 4->Clubs, 
    and 11->Jack, etc into a tuple and as a string)
    """    
    suit_map = {1: 'Spades', 2: 'Hearts', 3: 'Diamonds', 4: 'Clubs'}

    value_map = {1: 'Ace', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five',
                    6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine',
                    10: 'Ten', 11: 'Jack', 12: 'Queen', 13: 'King'}
        
    value_name = value_map[card.value]
    suit_name = suit_map[card.suit]

    card_name = {'Tuple': (value_name, suit_name), 
                    'NameString': '%s of %s' % (value_name, suit_name)}
    return card_name
