"""
An interface to the pcards module.
"""

import pcards
import sys
import os

TXT_MSG = {0: '',
              1: '**ERROR! BOX IS EMPTY / NON EXISTENT**',
              2: '**ERROR! NO BOX GENERATED YET**',
              3: '**ERROR! INVALID INPUT**',
              4: '**MESSAGE: The box contains %d cards**',
              'HBreak': '---------------------------------------',
              'MainMenu': """
              **WHAT DO YOU WANT TO TEST?**


              *------------------------------------*
              | 1. GENERATE A BOX OF CARDS         |
              | 2. SHUFFLE THE BOX OF CARDS        |
              | 3. UNSHUFFLE THE BOX OF CARDS      |
              | 4. DISPLAY SELECTED CARDS FROM BOX |
              | 5. DEAL CARDS FROM THE BOX         |
              | 6. PLACE CARDS INTO THE BOX        |
              | 7. SPLIT THE BOX INTO SUB DECKS    |
              | 8. QUIT                            |
              *------------------------------------*



              NOTE: OPTIONS 2 - 7 WORK ONLY ON THE LAST GENERATED BOX.

              IF YOU GENERATE A NEW BOX, YOUR OLD BOX WILL BE ERASED, AND

              ALL SUBSEQUENT ACTIONS WILL BE PERFORMED ON THE NEW BOX.

              """}

global EMPTY
EMPTY = False


def generate_box():
    """
    Generate a box of cards.
    """
    deck_count = int(raw_input("How many decks in the box? "))
    if deck_count > 0:
        box_object = pcards.BoxClass(deck_count)
        cards_in_box = len(box_object.card_box)
        print "Generated box holds %d X 52 = %d cards" \
                % (cards_in_box / 52, cards_in_box)
        print TXT_MSG['HBreak']
        return box_object
    else:
        print TXT_MSG[3]
        print TXT_MSG['HBreak']
        return 'empty'


def shuffle(box_object):
    """
    Shuffle a box of cards.
    """
    print TXT_MSG[4] % len(box_object.card_box)
    print TXT_MSG['HBreak']
    print "Shuffling..."
    box_object.shuffle()
    print "Shuffle complete."
    print TXT_MSG['HBreak']
    return box_object


def place(box_object):
    """
    Place a card in a box.
    """
    print TXT_MSG[4] % len(box_object.card_box)
    print TXT_MSG['HBreak']
    print "You can place a single card into the box."
    print "As a demo, you can select a value and a suit",
    print "to insert into the existing box."

    insert_value = int(raw_input("Enter the value of the card (1 - 13) "))
    insert_suit = int(raw_input("Enter the suit of the card (1=Spades, 2=Hearts, 3=Diamonds, 4=Clubs) "))

    insert_card = pcards.CardClass(insert_suit, insert_value)

    place_status = box_object.place(insert_card)

    if place_status == 'OK':
        global EMPTY
        EMPTY = False
        print "CARD INSERTED"
    elif place_status == 'NOCARD':
        print "**ERROR! This is not a valid card**"
    elif place_status == 'FULL':
        print "**ERROR! Cannot insert card. The box is full**"
    elif place_status == 'DUPLICATE':
        print "**ERROR! All possible occurences of this card are already in the box**"
    else:
        print TXT_MSG[3]

    print TXT_MSG['HBreak']
    return box_object


def deal(box_object):
    """
    Deal a specified number of cards from the box.
    """
    print TXT_MSG[4] % len(box_object.card_box)
    print TXT_MSG['HBreak']
    count_of_cards = int(raw_input("How many cards to deal? "))

    if count_of_cards > 0:
        dealt_cards_list = box_object.deal(count_of_cards)
        print "Here are the dealt cards:"

        for i in dealt_cards_list:
            card_name = pcards.name_card(i)
            print card_name['NameString']

    elif count_of_cards == 0:
        pass

    else:
        print TXT_MSG[3]

    if len(box_object.card_box) == 0:
        global EMPTY
        EMPTY = True

    print TXT_MSG['HBreak']
    return box_object


def split(box_object):
    """
    Split the box into subdecks.
    """
    print TXT_MSG[4] % len(box_object.card_box)
    print TXT_MSG['HBreak']
    subdecks = int(raw_input("How many sub decks to create? "))

    if subdecks > 1:
        split_result = box_object.split(subdecks)

        if split_result == 'MAX':
            print "**ERROR! There are more sub decksthan are cards in the box**"
        else:
            print "The box has been split into %d sub deck(s)." \
                    % len(split_result)
            for i in range(0, len(split_result)):
                print "Subdeck %d contains %d card(s)." \
                        % ((i + 1), len(split_result[i]))

    elif subdecks == 0 or subdecks == 1:
        print "No sub decks created. The box remains as is."

    else:
        print TXT_MSG[3]

    if len(box_object.card_box) == 0:
        global EMPTY
        EMPTY = True 

    print TXT_MSG['HBreak']
    return box_object


def unshuffle(box_object):
    """
    Unshuffle the box.
    """
    print TXT_MSG[4] % len(box_object.card_box)
    print TXT_MSG['HBreak']

    print "Unshuffling..."
    box_object.unshuffle()
    print "The cards are now in order."

    print TXT_MSG['HBreak']
    return box_object


def view(box_object):
    """
    View cards in the box without dealing.
    """
    print TXT_MSG[4] % len(box_object.card_box)
    print TXT_MSG['HBreak']

    start_at = int(raw_input("What is the starting point (Top card is at 1)? ")) - 1
    number_of_cards = int(raw_input("How many cards to view? "))

    if (start_at >= 0 and number_of_cards >= 0):
        if start_at + number_of_cards <= len(box_object.card_box): 
            stop_at = start_at + number_of_cards - 1
            print "Showing %d cards starting from position %d"\
                     % (number_of_cards, (start_at + 1))
        else:
            stop_at = len(box_object.card_box) - 1
            print "End of box reached before finding %d cards" \
                    % number_of_cards
            print "Showing last %d cards" % ((stop_at - start_at) + 1)

        selected_view = box_object.card_box[start_at: (stop_at + 1)]

        for i in selected_view:
            card_name = pcards.name_card(i)
            print card_name['NameString']

    else:
        print TXT_MSG[3]

    print TXT_MSG['HBreak']


def user_interface():
    """
    User interface.
    """
    global EMPTY
    
    if os.name == 'nt':
        clear_screen = 'cls'
    else: 
        clear_screen = 'clear'

    box_object = 'none'

    response = '0'
    err = TXT_MSG[0]
    os.system(clear_screen)

    while response != '8':
    
        print """
            %s  
            """ % err

        print TXT_MSG['MainMenu']
        
        response = raw_input("> ")
        os.system(clear_screen) 
       
        if response == '1':
            err = TXT_MSG[0]
            box_object = generate_box()
             
        elif response == '2':
            if box_object == 'none' or EMPTY is True: 
                err = TXT_MSG[1]
            else:
                err = TXT_MSG[0]
                box_object = shuffle(box_object)

        elif response == '3':
            if box_object == 'none' or EMPTY is True:
                err = TXT_MSG[1]
            else:
                err = TXT_MSG[0]    
                box_object = unshuffle(box_object)
                
        elif response == '4':
            if box_object == 'none' or EMPTY is True:
                err = TXT_MSG[1]
            else:
                err = TXT_MSG[0]
                view(box_object)

        elif response == '5':
            if  box_object == 'none' or EMPTY is True:
                err = TXT_MSG[1]
            else:
                err = TXT_MSG[0]
                box_object = deal(box_object)

        elif response == '6':
            if  box_object == 'none':
                err = TXT_MSG[2]
            else:
                err = TXT_MSG[0]
                box_object = place(box_object)

        elif response == '7':
            if  box_object == 'none' or EMPTY is True:
                err = TXT_MSG[1]
            else:
                err = TXT_MSG[0]
                box_object = split(box_object)

        elif response == '8':
            print "Bye"
            print TXT_MSG['HBreak']
            sys.exit(0)
             
        else:
            err = TXT_MSG[3]
            
user_interface()
