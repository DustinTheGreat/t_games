"""
player.py

Base player classes for tgames.

Classes:
Player: The base player class. (object)
Human: A human being, with stored data. (Player)
"""


from __future__ import print_function

import os
import random
import string
import sys


if sys.version_info[0] == 2:
    input = raw_input
    

class Player(object):
    """
    The base player class. (object)

    Attributes:
    game: The game the player is playing. (game.Game)
    name: The name of the player. (str)

    Methods:
    ask: Get information from the player. (str)
    tell: Give information to the player. (None)

    Overridden Methods:
    __init__
    """

    def __init__(self, name):
        """
        Save the player's name. (None)

        Parameters:
        name: The name of the player. (str)
        """
        self.name = name
        self.game = None

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        return input(prompt)

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        !! get the actual signature from print.

        Parameters:
        The parameters are as per the built-in print function.
        """
        print(*args, **kwargs)


class Bot(Player):
    """
    A computer player. (Player)

    Overridden Methods:
    __init__
    """

    def __init__(self, taken_names = [], initial = ''):
        """
        Set the bot's name. (None)

        If initial is empty, the bot's name can start with any letter.

        Parameters:
        taken_names: Names already used by a player. (list of str)
        initial: The first letter of the bot's name. (str)
        """
        while True:
            if initial:
                self.name = random.choice(BOT_NAMES[initial].split('/'))
            else:
                self.name = random.choice(BOT_NAMES[random.choice(string.ascii_lowercase)].split('/'))
            if self.name not in taken_names:
                break


class Human(Player):
    """
    A human being, with stored data. (Player)

    Attributes:
    color: The player's favorite color. (str)
    folder_name: The local folder with the player's data. (str)
    quest: The player's quest. (str)

    Overridden Methods:
    __init__
    """

    def __init__(self):
        while True:
            # Get the user's name.
            self.name = input('What is your name? ')
            # Allow for single or multiple entry of quest and color.
            if ';' in self.name:
                self.name, self.quest, self.color = [word.strip() for word in self.name.split(';')]
            else:
                self.quest = input('What is your quest? ')
                self.color = input('What is your favorite color? ')
            # Check for previous log in.
            self.folder_name = 'player_data/{}-{}-{}/'.format(self.name, self.quest, self.color).lower()
            if not os.path.exists(self.folder_name):
                new_player = input('I have not heard of you. Are you a new player? ')
                if new_player.lower() in ('yes', 'y', '1'):
                    os.mkdir(self.folder_name)
                    break
                print()
            else:
                break


BOT_NAMES = {'a': 'Ash/Abby/Adam/Alan/Alice/Ada/Adele/Alonzo/Angus/Astro',
    'b': 'Bender/Barbara/Blue/Bella/Buckaroo/Beth/Bob/Bishop/Betty/Brooke',
    'c': 'Caitlyn/Calvin/Candice/Carl/Carol/Carsen/Cassandra/Cecilia/Chance/Craig',
    'd': 'Data/Deckard/Dahlia/Dana/Daphne/Damon/Debby/David/Darryl/Denise',
    'e': 'Edith/Eve/Ed/Elliot/Elizabeth/Edgar/Enzo/Emelia/Erin/Ernest',
    'f': 'Felicity/Futura/Fatima/Felix/Felipe/Finn/Fiona/Frances/Frank/Fletcher',
    'g': 'Gort/Guido/Geneva/Gia/Gerty/Gilberto/Grace/Gloria/Garry/Grover',
    'h': 'Hymie/Hobbes/Hiro/Homer/Hugo/Haladay/Harriet/Heidi/Hope/Haven',
    'i': 'Ida/Indira/Ines/Inga/Ivy/Ian/Igor/Isaac/Ichabod/Ivan',
    'j': 'Judith/Jade/Jane/Jodie/Julia/John/Jaque/Jim/Johan/Jerome',
    'k': 'Kitt/Karen/Kay/Kelly/Kyoko/Kareem/Kurt/Kronos/Klaus/Kirk',
    'l': 'Lore/Lee/Lars/Leon/Laszlo/Limor/Laverne/Leelu/Lola/Lois',
    'm': 'Marvin/Mr. Roboto/MechaCraig/Maximillian/Mordecai/Maria/Mary Lou/Marlyn/Monique/Mika',
    'n': 'Nellodee/Nancy/Naomi/Norma/Natalie/Nathan/Ned/Nero/Nick/Nigel',
    'o': 'Otis/Ogden/Omar/Oscar/Otto/Olga/Olivia/Oksana/Octavia/Oriana',
    'p': 'Pris/Patience/Patty/Phoebe/Pru/Patrick/Phillip/Parker/Paul/Pavel',
    'q': 'Queenie/Quenby/Quiana/Quinn/Qadir/Qasim/Quincy/Quang/Quest',
    'r': 'Robby/Roy/Rachel/Risana/Rita/Rosie/River/Reiner/Rick/Rusty',
    's': 'Sam/Shroud/Santiago/Steve/Sonny/Sarina/Susan/Sylvia/Shirley/Sheba',
    't': 'Tabitha/Theresa/Tracy/Trinity/Tamala/Tanner/Tariq/Ted/Tyler/Tyrone',
    'u': 'Ulla/Uma/Ursula/Ursuline/Uta/Ulric/Umberto/Uriah/Usher/Urban',
    'v': 'Vincent/Valerie/Venus/Vivian/Vera/Veronica/Victor/Viggo/Vikram/Vladimir',
    'w': 'Wally/Wednesday/Wana/Wendy/Willow/Winnie/Waylon/Wayne/William/Woflgang',
    'x': 'Xander/Xavier/Xena/Xhosa/Ximena/Xiang/Xaria/Xanthus/Xenon/Xerxes',
    'y': 'Yamina/Yasmin/Yoland/Yvette/Yadira/Yaakov/Yitzhak/Yves/Yannick/Yaron',
    'z': 'Zahara/Zelda/Zoe/Zuma/Zenaida/Zachary/Zafar/Zane/Zebulon/Zen'}