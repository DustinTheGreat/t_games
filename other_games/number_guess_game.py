"""
number_guess_game.py

A classic number guessing game.

Copyright (C) 2018 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Classes:
NumberGuess: A classic number guessing game. (game.Game)
"""


import random

from .. import game
from .. import player
from .. import utility


class GuessBot(player.Bot):
    """
    A number guessing bot. (player.Bot)

    Attributes:
    high_guess: The highest guess the bot should make. (int)
    last_guess: The last guess the bot made. (int)
    low_guess: The lowest guess the bot should make. (int)

    Methods:
    guess: Guess a number.
    secret_number: Make a number to be guessed. (int)

    Overridden Methods:
    ask
    ask_int
    set_up
    tell
    """

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        if prompt == 'What is your guess? ':
            self.last_guess = self.guess()
            return str(self.last_guess)

    def ask_int(self, prompt, **kwargs):
        """
        Get an integer response from the human. (int)

        Parameters:
        prompt: The question asking for the interger. (str)
        kwargs: The standard arguments to ask_int
        """
        if 'secret number' in prompt:
            return self.secret_number(kwargs['low'], kwargs['high'])
        else:
            return super(GuessBot, self).ask_int(prompt, **kwargs)

    def guess(self):
        """Guess a number. (int)"""
        return random.randint(self.low_guess, self.high_guess)

    def secret_number(self, low, high):
        """
        Make a number to be guessed. (int)

        Parameters:
        low: The lowest possible secret number. (int)
        high: The highest possible secret number. (int)
        """
        return random.randint(low, high)

    def set_up(self):
        """Set up the bot. (None)"""
        self.low_guess = self.game.low
        self.high_guess = self.game.high
        self.last_guess = None

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        if 'lower' in args[0]:
            self.low_guess = self.last_guess + 1
        elif 'higher' in args[0]:
            self.high_guess = self.last_guess - 1
        super(GuessBot, self).tell(*args, **kwargs)


class NumberGuess(game.Game):
    """
    A classic number guessing game. (game.Game)

    Attributes:
    easy: A flag for easier game play. (bool)
    high: The highest possible secret number. (int)
    low: The lowest possible secret number. (int)
    number: The secret number. (int)
    phase: Whether the human is guessing or answering. (str)

    Methods:
    do_guess: Guess the secret number. (bool)
    reset: Reset guess tracking. (None)

    Overridden Methods:
    default
    handle_options
    player_action
    set_options
    set_up
    """

    aka = ['NuGG', 'Guess a Number']
    categories = ['Other Games']
    name = 'Number Guessing Game'
    num_options = 3

    def default(self, line):
        """
        Handle unrecognized commands. (bool)

        Parameters:
        text: The raw text input by the user. (str)
        """
        try:
            guess = int(line)
        except ValueError:
            return super(NumberGuess, self).default(line)
        else:
            return self.do_guess(line)

    def do_guess(self, arguments):
        """
        Guess the secret number. (g)
        """
        player = self.players[self.player_index]
        try:
            guess = int(arguments)
        except ValueError:
            player.error('{!r} is not a valid integer.'.format(arguments))
        else:
            if guess < self.low:
                player.error('{} is below the lowest possible secret number.'.format(guess))
            elif guess > self.high:
                player.error('{} is above the highest possible secret number.'.format(guess))
            else:
                self.guesses += 1
                if guess < self.number:
                    player.tell('{} is lower than the secret number.'.format(guess))
                elif guess > self.number:
                    player.tell('{} is higher than the secret number.'.format(guess))
                else:
                    text = '{} is the secret number! You got it in {} guesses.'
                    player.tell(text.format(guess, self.guesses))
                    self.scores[player.name] = self.guesses
                    self.reset()
                    return False
        return True

    def game_over(self):
        """Determine if the game is finished or not. (bool)"""
        if self.turns == 2:
            if self.scores[self.human.name] < self.scores[self.bot.name]:
                text = 'You won, {0} guesses to {1}.'
                self.win_loss_draw[0] = 1
            elif self.scores[self.human.name] > self.scores[self.bot.name]:
                text = 'You lost, {0} guesses to {1}.'
                self.win_loss_draw[1] = 1
            else:
                text = 'It was a tie, with {0} guesses each.'
                self.win_loss_draw[2] = 1
            self.human.tell(text.format(self.scores[self.human.name], self.scores[self.bot.name]))
            return True
        else:
            return False

    def handle_options(self):
        """Process the option settings for the game. (None)"""
        super(NumberGuess, self).handle_options()
        self.bot = GuessBot(taken_names = [self.human.name])
        self.players = [self.human, self.bot]

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        guess_text = utility.number_plural(self.guesses, 'guess', 'guesses')
        player.tell('\nYou have made {} so far.'.format(guess_text))
        if self.number is None:
            foe = self.players[1 - self.player_index]
            query = 'What do you want the secret number to be? '
            self.number = foe.ask_int(query, low = self.low, high = self.high)
        return self.handle_cmd(player.ask('What is your guess? '))

    def reset(self):
        """Reset guess tracking. (None)"""
        self.number = None
        self.guesses = 0

    def set_options(self):
        """Set the options for the game. (None)"""
        self.option_set.add_option('easy', ['e'], question = 'Do you want to play in easy mode? bool')
        self.option_set.add_option('low', ['l'], int, 1,
            question = 'What should the lowest possible number be (return for 1)? ')
        self.option_set.add_option('high', ['h'], int, 108,
            question = 'What should the highest possible number be (return for 108)? ')

    def set_up(self):
        """Set up the game. (None)"""
        self.reset()
