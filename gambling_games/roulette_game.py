"""
roulette_game.py

Constants:
CREDITS: The credits for roulette. (str)
RULES: The rules of roulette. (str)

Classes:
Roulette: A game of roulette. (game.Game)
"""


import random
import re
import time

import tgames.game as game
import tgames.utility as utility


CREDITS = """
Game Design: Traditional (French)
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
You may make one or more bets on the numbers 0-36 (and 00 depending on the 
layout). One of the numbers is chosen at random, and bets including that 
number are paid out. Traditionally the number is chosen by spinning a small
wheel (the literal translation of roulette) with a pocket for each number, and
rolling a ball into a bowl with the wheel at the bottom.

Bets are typically made with a command, a number or set of numbers separated
by dashes, and the ammount bet. Payouts are made based on the number of
numbers bet on, assuming the zeroes do not exist (the zeros give the house
its edge). There are inside bets on individual numbers or groups of numbers
based on a layout of the numbers in three columns. There are outside bets 
based on the features of the number, including high/low, even/odd and red/
black (each number has a color, with the zeroes being green). There are also 
called bets that are groups of other bets. Once all of your bets are placed,
use the spin command to spin the wheel to detrmine the winning number.

The bets are listed below. The number in brackets is the number of numbers 
that must be specified for the bet. Bets with a capital F in the brackets may
only be made on the French layout, and bets with a capital A may only be made
on the American layout (see options).

INSIDE BETS:
Basket/First Four: A bet on the first two rows of numbers (0, 1, 2, 3). [0F]
Column: Bet on a column of 12 numbers. The column can be specified with 1/2/3,
    P/M/D (Premiere, Moyenne, Derniere) or F/S/T (First, Second, Third). [1]
Corner: Bet on four numbers in a square. Specify the highest and lowest
    numbers in the square. [2]
Double Street/Six Line: Bet on six numbers that form two rows. Specify the
    first number of the first row and the last number of the second row. [2]
Dozen: Bet on the first, second, or third dozen. Use 1/2/3, P/M/D, or F/S/T
    to specify the dozen (seel Column bet). [1]

OUTSIDE BETS:
Black/Noir: Bet on the black numbers. [0]
Even: Bet on the even numbers. [0]
High/19-36: Bet on the high numbers (over 18). [0]

CALLED BETS:
Complete: Make every inside bet that contains the specified number. May be
    done as 'complete progressive,' which multiplies each bet by the number
    of numbers in the bet. [1]
Final/Finals/Finale: Bet on all non-zero numbers ending with the specified
    digit. [1]

OTHER COMMANDS:
Bets: Show a numbered list of the current bets.

OPTIONS:
"""


class Roulette(game.Game):
    """
    A game of roulette.

    Class Attributes:
    american: The order of the wheel in the American layout. (list of str)
    black: The black numbers. (list of str)
    french: The order of the wheel in the French layout. (list of str)
    int_re: A regular expression to capture numbers. (re.SRE_Pattern)
    red: The red numbers. (list of str)

    Attributes
    bets: Bets made this round. (list of tuple)
    layout: American or French layout. (str)
    numbers: The numbers on the wheel. (list of str)
    stake: The starting money the player gets. (int)

    Methods:
    check_bet: Do common checking for valid bets. (str, int)
    check_two_numbers: Check for two numbers in the layout. (bool)
    do_basket: Make a four number bet incluidng 0. (bool)
    do_bets: Show a numbered list of the current bets. (bool)
    do_black: Bet on black. (bool)
    do_column: Bet on a column. (bool)
    do_complete: Make all inside bets on a given number. (bool)
    do_corner: Make a bet on a square of numbers. (bool)
    do_double: Make a bet on two consecutive rows of numbers. (bool)
    do_dozen: Bet on a consecutive dozen. (bool)
    do_even: Bet on the the even numbers. (bool)
    do_final: Bet on numbers ending with a specified digit. (bool)
    do_high: Bet on the the high half of the range. (bool)
    do_spin: Spin the wheel. (bool)
    do_straight: Make a bet on a single number. (bool)

    Overridden Methods:
    handle_options
    player_turn
    set_up
    """

    aliases = {'1-18': 'low', '19-36': 'high', 'double-street': 'double', 'douzaine': 'dozen', 
        'finale': 'final', 'finals': 'final' 'first': 'basket', 'impair': 'odd', 'le': 'third', 
        'manque': 'low', 'noir': 'black', 'orphelins': 'orphans', 'pair': 'even', 'passe': 'high', 
        'rouge': 'red', 'single': 'straight', 'six': 'double', 'six-line': 'double', 'tiers': 'third', 
        'voisins': 'neighbors'}
    # The order of the wheel in the American layout.
    american = ['0', '28', '9', '26', '30', '11', '7', '20', '32', '17', '5', '22', '34', '15', '3', '24', 
        '36', '13', '1', '00', '27', '10', '25', '29', '12', '8', '19', '31', '18', '6', '21', '33', '16', 
        '4', '23', '35', '14', '2']
    # The black numbers.
    black = ['2', '4', '6', '8', '10', '11', '13', '15', '17', '20', '22', '24', '26', '28', '29', '31',
        '33', '35']
    categories = ['Gambling Games', 'Other Games']
    # The order of the wheel in the French layout.
    french = ['0', '32', '15', '19', '4', '21', '2', '25', '17', '34', '6', '27', '13', '36', '11', '30', 
        '8', '23', '10', '5', '24', '16', '33', '1', '20', '14', '31', '9', '22', '18', '29', '7', '28', 
        '12', '35', '3', '26']
    # A regular expression to capture numbers.
    int_re = re.compile('\d+')
    name = 'Roulette'
    num_options = 3
    red = ['1', '3', '5', '7', '9', '12', '14', '16', '18', '19', '21', '23', '25', '27', '30', '32', '34', 
        '36']

    def check_bet(self, arguments):
        """
        Do common checking for valid bets. (str, int)

        This checks the valid number of arguments and a valid bet amount. The
        specific bet method will need to check that the thing being bet on is valid.

        Parameters:
        arguments: The arguments to the bet command. (str)
        """
        args = arguments.split()
        # Check for number and bet
        if len(args) != 2:
            self.human.tell('Invalid number of arguments to a bet command.')
        else:
            target, bet = args
            # Check for a valid bet.
            if bet.isdigit():
                bet = int(bet)
                max_bet = min(self.max_bet, self.scores[self.human.name])
                if 1 <= bet <= max_bet:
                    return target, bet
                else:
                    self.human.tell('That bet is too large. You may only bet {} bucks.'.format(max_bet))
            else:
                self.human.tell('All bets must be decimal integers.')
        # Return dummy (False) values on failure.
        return '', 0

    def check_two_numbers(self, pair, bet_type):
        """
        Check for two numbers in the layout. (bool)

        Parameters:
        pair: The two numbers separated by a dash. (str)
        bet_type: The type of bet trying to be made. (str)
        """
        pair = pair.split('-')
        # Check for two numbers.
        if len(pair) != 2:
            self.human.tell('You must enter two numbers for a {} bet.'.format(bet_type))
        # Check that they are on the wheel.
        elif pair[0] not in self.numbers:
            self.human.tell('{} is not in this layout.'.format(pair[0]))
        elif pair[1] not in self.numbers:
            self.human.tell('{} is not in this layout.'.format(pair[1]))
        else:
            return True
        return False

    def do_basket(self, arguments):
        """
        Make a four number bet incluidng 0. (bool)

        Parameters:
        arguments: The ammount to bet. (str)
        """
        # Handle aliases.
        words = arguments.split()
        if words[0].lower() != 'four':
            words = ['basket'] + words
        # Check the bet.
        numbers, bet = self.check_bet(' '.join(words))
        # Check the layout.
        if numbers and self.layout == 'french':
            self.scores[self.human.name] -= bet
            self.bets.append(('basket bet', ('0', '1', '2', '3'), bet))
        elif numbers:
            self.human.tell('That bet can only be made on a French layout.')
        return True

    def do_bets(self, arguments):
        """
        Show a numbered list of the current bets. (bool)

        Parameters:
        arguments: The ignored arguments. (str)
        """
        text = '\n'
        for bet_index, bet in enumerate(self.bets):
            text += '{}: {} ({} bucks)\n'.format(bet_index + 1, bet[0], bet[2])
        self.human.tell(text[:-1])
        return True

    def do_black(self, arguments):
        """
        Bet on black. (bool)

        Parameters:
        arguments: The amount to bet. (str)
        """
        # Check the bet.
        numbers, bet = self.check_bet('black {}'.format(arguments))
        if numbers:
            # Make the bet.
            self.scores[self.human.name] -= bet
            self.bets.append(('black bet', self.black, bet))
        return True

    def do_column(self, arguments):
        """
        Bet on a column. (bool)

        Parameters:
        arguments: The column and the bet. (str)
        """
        # Check the bet
        column, bet = self.check_bet(arguments)
        if column:
            # Get the numbers for the column
            targets = []
            if column.lower() in ('1', 'p', 'f'):
                targets = [str(number) for number in range(1, 37, 3)]
            elif column.lower in ('2', 'm', 's'):
                targets = [str(number) for number in range(2, 37, 3)]
            elif column.lower in ('3', 'd', 't'):
                targets = [str(number) for number in range(2, 37, 3)]
            if targets:
                # Make the bet.
                self.scores[self.human.name] -= bet
                self.bets.append(('column bet on {}'.format(column), targets, bet))
            else:
                # Warn on invalid column
                self.human.tell('That is not a valid column. Please use 1/2/3, P/M/D, or F/S/T.')
        return True

    def do_complete(self, arguments):
        """
        Make all inside bets on a given number. (bool)

        Parameters:
        arguments: The number to bet on and the bet. (str)
        """
        # Check for progressive bets.
        words = arguments.split()
        progressive = 'progressive' in words
        if progressive:
            words.remove('progressive')
        # Check the bet
        number, bet = self.check_bet(' '.join(words))
        if number:
            if number in self.numbers:
                num = int(number)
                # single bet
                bets = [('single bet on {}'.format(num), [number], bet)]
                text = 'split bet on {}-{}'
                # up split
                if num > 3:
                    bets.append((text.format(num, num - 3), [number, str(num - 3)], bet))
                elif self.layout == 'french':
                    if num:
                        bets.append(('split bet on 0-{}'.format(num), ['0', number], bet))
                elif num:
                    if num != 1:
                        bets.append(('split bet on 00-{}'.format(num), ['00', number], bet))
                    if num != 3:
                        bets.append(('split bet on 0-{}'.format(num), ['0', number], bet))
                # down splits
                if num < 34:
                    if num:
                        bets.append((text.format(num, num + 3), [number, str(num + 3)], bet))
                    elif self.layout == 'french':
                        for down in range(1, 3):
                            bets.append(('split bet on 0-{}'.format(num), ['0', number], bet))
                    elif number == '0':
                        bets.append(('split bet on 0-1', ['0', '1'], bet))
                        bets.append(('split bet on 0-2', ['0', '2'], bet))
                    elif number == '00':
                        bets.append(('split bet on 00-2', ['00', '2'], bet))
                        bets.append(('split bet on 00-3', ['00', '3'], bet))
                # right splits
                if num % 3:
                    bets.append((text.format(num, num + 1), [number, str(num + 1)], bet))
                # left splits
                if num % 3 != 1:
                    bets.append((text.format(num - 1, num), [number, str(num - 1)], bet))
                # street
                if num % 3:
                    end = num + 3 - (num % 3)
                else:
                    end = num
                if num:
                    targets = [str(n) for n in range(end - 2, end + 1)]
                    bets.append(('street bet on {}-{}-{}'.format(*targets), targets, bet))
                # trio / basket / top line
                if num < 4:
                    sub_bets = [('trio bet on 0-1-2', ['0', '1', '2'], bet)]
                    if self.layout == 'french':
                        sub_bets.append(('trio bet on 0-2-3', ['0', '2', '3'], bet))
                        sub_bets.append(('basket bet', ['0', '1', '2', '3'], bet))
                    if self.layout == 'american':
                        sub_bets.append(('trio bet on 00-2-3', ['00', '2', '3'], bet))
                        sub_bets.append(('trio bet on 0-00-2', ['0', '00', '2'], bet))
                        sub_bets.append(('top line bet', ['0', '00', '1', '2', '3'], bet))
                    bets.extend([bet for bet in sub_bets if number in bet[1]])
                # up left corner
                text = 'corner bet on {}-{}'
                if num > 3 and num % 3 != 1:
                    targets = [str(n) for n in (num - 4, num - 3, num - 1, num)]
                    bets.append((text.format(num - 4, num), targets, bet))
                # up right corner
                if num > 3 and num % 3:
                    targets = [str(n) for n in (num - 3, num - 2, num, num + 1)]
                    bets.append((text.format(num - 3, num + 1), targets, bet))
                # down right corner
                if num < 34 and num % 3:
                    targets = [str(n) for n in (num, num + 1, num + 3, num + 4)]
                    bets.append((text.format(num, num + 4), targets, bet))
                # down left corner
                if num < 34 and num % 3 != 1:
                    targets = [str(n) for n in (num - 1, num, num + 2, num + 3)]
                    bets.append((text.format(num - 1, num + 3), targets, bet))
                text = 'double street bet on {}-{}'
                # up double street
                if num > 3:
                    targets = [str(n) for n in range(end - 5, end + 1)]
                    bets.append((text.format(end - 5, end), targets, bet))
                # down double street
                if num < 34:
                    targets = [str(n) for n in range(end - 2, end + 4)]
                    bets.append((text.format(end - 2, end + 3), targets, bet))
                # progressive betting
                if progressive:
                    prog_bets = []
                    for text, targets, bet in bets:
                        prog_bets.append((text, targets, bet * len(targets)))
                    bets = prog_bets
                # check bet against what player has
                total_bet = sum([bet for text, targets, bet in bets])
                if total_bet > self.scores[self.human.name]:
                    self.human.tell('You do not have enough bucks for the total bet.')
                else:
                    # Maket the bets.
                    self.bets.extend(bets)
                    self.scores[self.human.name] -= total_bet
            else:
                # Warning for an invalid number.
                self.human.tell('That number is not in the current layout.')
        return True

    def do_corner(self, arguments):
        """
        Make a bet on a square of numbers. (bool)

        Parameters:
        arguments: The number to bet on and the bet. (str)
        """
        # Check the bet.
        numbers, bet = self.check_bet(arguments)
        # Check for two numbers.
        if numbers and self.check_two_numbers(numbers, 'corner'):
            # Check for a valid corner.
            low, high = sorted([int(x) for x in numbers.split('-')])
            if high - low == 4 and low % 3:
                # Make the bet.
                self.scores[self.human.name] -= bet
                targets = [str(number) for number in (low, low + 1, high - 1, high)]
                self.bets.append(('corner bet on {}'.format(numbers), targets, bet))
            else:
                message = '{} and {} are not the low and high of a square of numbers.'
                self.human.tell(message.format(low, high))
        return True

    def do_double(self, arguments):
        """
        Make a bet on two consecutive rows of numbers. (bool)

        Parameters:
        arguments: The range to bet on and the bet. (str)
        """
        # Handle extra words and aliases.
        words = arguments.lower().split()
        if words[0] in ('street', 'line'):
            arguments = ' '.join(words[1:])
        # Check the bet.
        numbers, bet = self.check_bet(arguments)
        # Check for two numbers.
        if numbers and self.check_two_numbers(numbers, 'double street'):
            # Check for valid double street.
            low, high = sorted([int(x) for x in numbers.split('-')])
            if high - low == 5 and not high % 3:
                # Make the bet.
                self.scores[self.human.name] -= bet
                targets = [str(number) for number in range(low, high + 1)]
                self.bets.append(('double street bet on {}'.format(numbers), targets, bet))
        return True

    def do_dozen(self, arguments):
        """
        Bet on a consecutive dozen. (bool)

        Parameters:
        arguments: The dozen and the bet. (str)
        """
        # Check the bet.
        dozen, bet = self.check_bet(arguments)
        if dozen:
            # Get the numbers in the dozen.
            targets = []
            if dozen.lower() in ('1', 'p', 'f'):
                targets = [str(number) for number in range(1, 13)]
            elif dozen.lower in ('2', 'm', 's'):
                targets = [str(number) for number in range(12, 25)]
            elif dozen.lower in ('3', 'd', 't'):
                targets = [str(number) for number in range(24, 37)]
            if targets:
                # Make the bet.
                self.scores[self.human.name] -= bet
                self.bets.append(('dozen bet on {}'.format(dozen), targets, bet))
            else:
                # Warn the user if the dozen is invalid.
                self.human.tell('That is not a valid dozen. Please use 1/2/3, P/M/D, or F/S/T.')
        return True

    def do_even(self, arguments):
        """
        Bet on the the even numbers. (bool)

        Parameters:
        arguments: The amount to bet. (str)
        """
        # Check the bet.
        numbers, bet = self.check_bet('even {}'.format(arguments))
        if numbers:
            # Make the bet.
            self.scores[self.human.name] -= bet
            self.bets.append(('even bet', [str(number) for number in range(2, 37, 2)], bet))
        return True

    def do_final(self, arguments):
        """
        Bet on numbers ending in a particular digit. (bool)

        Parameters:
        arguments: The final number and the amount to bet. (str)
        """
        # Check the bet.
        number, bet = self.check_bet(arguments)
        if number:
            # Check the digit.
            if number in '1234567890':
                # Get the numbers to bet on.
                numbers = [n for n in self.numbers if n.endswith(number) and n not in '00']
                # Check the full bet.
                full_bet = bet * len(numbers)
                if full_bet > self.scores[self.human.name]:
                    # Warn if user can't afford the full bet.
                    self.human.tell('You do not have enough bucks for the full bet.')
                else:
                    # Make the bets.
                    for number in numbers:
                        self.bets.append(('single bet on {}'.format(number), [number], bet))
                    self.scores[self.human.name] -= self.bet
            else:
                self.human.tell('That is not a valid final digit.')
        return True

    def do_high(self, arguments):
        """
        Bet on the the high half of the range. (bool)

        Parameters:
        arguments: The amount to bet. (str)
        """
        # Check the bet.
        numbers, bet = self.check_bet('high {}'.format(arguments))
        if numbers:
            # Make the bet.
            self.scores[self.human.name] -= bet
            self.bets.append(('high bet', [str(number) for number in range(19, 37)], bet))
        return True

    def do_layout(self, arguments):
        """
        Show the current layout. (bool)

        Parameters:
        arguments: The ignored arguments to the command. (str)
        """
        if self.layout == 'american':
            text = '\n  0  |  00  \n'
        else:
            text = '\n      0     \n'
        for number in range(1, 37):
            if str(number) in self.red:
                text += ' {:2} '.format(number)
            else:
                text += '({:2})'.format(number)
            if not number % 3:
                text += '\n'
        self.human.tell(text + '\nred (black)')
        return True

    def do_low(self, arguments):
        """
        Bet on the the low half of the range. (bool)

        Parameters:
        arguments: The amount to bet. (str)
        """
        numbers, bet = self.check_bet('low {}'.format(arguments))
        if numbers:
            self.scores[self.human.name] -= bet
            self.bets.append(('low bet', [str(number) for number in range(1, 19)], bet))
        return True

    def do_neighbors(self, arguments):
        """
        Make a neighbors of zero bet or a 'and the neighbors' bet. (bool)

        Parameters:
        arguments: The amount to bet. (str)
        """
        int_args = self.int_re.findall(arguments)
        if len(int_args) == 2:
            number, bet = self.check_bet(' '.join(int_args))
            self.neighborhood(number, 5, bet)
        elif self.layout == 'french' and int_args:
            numbers, bet = self.check_bet('neighbors {}'.format(int_args[0]))
            if bet * 9 > self.scores[self.human.name]:
                self.human.tell('You do not have enough money for the full bet.')
            elif numbers:
                self.bets.append(('trio bet on 0-2-3', ['0', '2', '3'], bet * 2))
                self.bets.append(('split bet on 4-7', ['4', '7'], bet))
                self.bets.append(('split bet on 12-5', ['12', '15'], bet))
                self.bets.append(('split bet on 18-21', ['18', '21'], bet))
                self.bets.append(('split bet on 19-22', ['19', '22'], bet))
                self.bets.append(('corner bet on 25-29', ['25', '26', '28', '29'], bet * 2))
                self.bets.append(('split bet on 32-35', ['32', '35'], bet))
                self.scores[self.human.name] -= 9 * bet
        elif int_args:
            self.human.tell('This bet is only available on the French layout.')
        else:
            self.human.tell('You must provide an ammount to bet.')
        return True

    def do_niner(self, arguments):
        """
        Make a bet on a neighborhood of niner. (bool)

        Parameters:
        arguments: the number in the center and the bet. (str)
        """
        number, bet = self.check_bet(arguments)
        self.neighborhood(number, 9, bet)

    def do_odd(self, arguments):
        """
        Bet on the the odd numbers. (bool)

        Parameters:
        arguments: The amount to bet. (str)
        """
        numbers, bet = self.check_bet('odd {}'.format(arguments))
        if numbers:
            self.scores[self.human.name] -= bet
            self.bets.append(('odd bet', [str(number) for number in range(1, 37, 2)], bet))
        return True

    def do_orphans(self, argument):
        """
        Bet on the orphans: the numbers not in the neighbors or the thirds. (bool)

        Parameters:
        arguments: The amount to bet. (str)
        """
        numbers, bet = self.check_bet('orphans {}'.format(argument))
        if bet * 5 > self.scores[self.human.name]:
            self.human.tell('You do not have enough money for the full bet.')
        elif numbers:
            self.bets.append(('single bet on 1', ['1'], bet))
            self.bets.append(('split bet on 6-9', ['6', '9'], bet))
            self.bets.append(('split bet on 14-17', ['14', '17'], bet))
            self.bets.append(('split bet on 17-20', ['17', '20'], bet))
            self.bets.append(('split bet on 31-34', ['31', '34'], bet))
            self.scores[self.human.name] -= 5 * bet
        return True

    def do_prime(self, arguments):
        """
        Make a bet on all but two prime numbers. (bool)

        Parameters:
        arguments: The primes to exclude and the bet. (str)
        """
        if arguments.lower() == 'twins':
            arguments = '2-23'
        numbers, bet = self.check_bet(arguments)
        if numbers and self.check_two_numbers(numbers, 'split'):
            low, high = sorted([int(x) for x in numbers.split('-')])
            primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
            if low in primes and high in primes and low != high:
                primes.remove(low)
                primes.remove(high)
                self.scores[self.human.name] -= bet
                self.bets.append(('prime bet excluding {}'.format(numbers), primes, bet))
            else:
                self.human.tell('{} and {} are not distinct prime numbers.'.format(low, high))
        return True

    def do_quit(self, arguments):
        """
        Stop playing before losing all your money. (bool)

        Parameters:
        arguments: The number of the hand to hit. (str)
        """
        self.flags |= 4
        if self.scores[self.human.name] > self.stake:
            self.win_loss_draw[0] = 1
            self.force_end = 'win'
        elif self.scores[self.human.name] < self.stake:
            self.win_loss_draw[1] = 1
            self.force_end = 'draw'
        else:
            self.win_loss_draw[2] = 1
            self.force_end = 'loss'
        return False

    def do_red(self, arguments):
        """
        Bet on red. (bool)

        Parameters:
        arguments: The amount to bet. (str)
        """
        numbers, bet = self.check_bet('red {}'.format(arguments))
        if numbers:
            self.scores[self.human.name] -= bet
            self.bets.append(('red bet', self.red, bet))
        return True

    def do_remove(self, arguments):
        """
        Remove a bet. (bool)

        Parameters:
        arguments: the number of the bet to remove. (str)
        """
        if not arguments.strip():
            arguments = str(len(self.bets))
        if arguments.strip().isdigit():
            bet_index = int(arguments) - 1
            if bet_index < len(self.bets):
                self.scores[self.human.name] += self.bets[bet_index][2]
                self.human.tell('The {} was removed.'.format(self.bets[bet_index][0]))
                self.bets.remove(self.bets[bet_index])
            else:
                self.human.tell('There are not that many bets.')
        else:
            self.human.tell('You must specify the bet with a postive integer.')
        return True

    def do_seven(self, arguments):
        """
        Make a bet on a neighborhood of seven. (bool)

        Parameters:
        arguments: the number in the center and the bet. (str)
        """
        number, bet = self.check_bet(arguments)
        self.neighborhood(number, 7, bet)

    def do_snake(self, arguments):
        """
        Zig zag bet from 1 to 34. (bool)

        Parameters:
        arguments: The amount to bet. (str)
        """
        numbers, bet = self.check_bet('snake {}'.format(arguments))
        if numbers:
            self.scores[self.human.name] -= bet
            targets = ['1', '5', '9', '12', '14', '16', '19', '23', '27', '30', '32', '34']
            self.bets.append(('snake bet', targets, bet))
        return True

    def do_spin(self, arguments):
        """
        Spin the wheel. (bool)

        Parameters:
        arguments: The ignored arguments to the command. (str)
        """
        for spin in range(random.randint(3, 5)):
            self.human.tell('Spinning...')
            time.sleep(1)
        self.human.tell('Clickety clackity...')
        time.sleep(1)
        winner = random.choice(self.numbers)
        self.human.tell('The winning number is {}.'.format(winner))
        self.pay_out(winner)

    def do_split(self, arguments):
        """
        Make a bet on a two adjacent numbers. (bool)

        Parameters:
        arguments: The number to bet on and the bet. (str)
        """
        numbers, bet = self.check_bet(arguments)
        if numbers and self.check_two_numbers(numbers, 'split'):
            low, high = sorted([int(x) for x in numbers.split('-')])
            valid = (low and high and abs(high - low) == 1 and min(low, high) % 3)
            valid = valid or (low and high and abs(high - low) == 3)
            valid = valid or (self.layout == 'american' and numbers in ('0-1', '0-2', '00-2', '00-3'))
            valid = valid or (self.layout == 'french' and numbers in ('0-1', '0-2', '0-3'))
            if valid:
                self.scores[self.human.name] -= bet
                self.bets.append(('split bet on {}'.format(numbers), numbers.split('-'), bet))
            else:
                self.human.tell('{} and {} are not adjacent on the layout.'.format(low, high))
        return True

    def do_straight(self, arguments):
        """
        Make a bet on a single number. (bool)

        Parameters:
        arguments: The numbers to bet on and the bet. (str)
        """
        number, bet = self.check_bet(arguments)
        if number:
            if number not in self.numbers:
                self.human.tell('That number is not in this layout.')
            else:
                self.scores[self.human.name] -= bet
                self.bets.append(('straight bet on {}'.format(number), [number], bet))
        return True

    def do_street(self, arguments):
        """
        Make a bet on a three number row. (bool)

        Parameters:
        arguments: The number to bet on and the bet. (str)
        """
        number, bet = self.check_bet(arguments)
        if number:
            numbers = number.split('-')
            end = int(numbers[-1])
            if end % 3:
                self.human.tell('A valid street must end in a multiple of three.')
            else:
                text = '{}-{}-{}'.format(end - 2, end - 1, end)
                self.scores[self.human.name] -= bet
                self.bets.append(('street bet on {}'.format(text), text.split('-'), bet))
        return True

    def do_third(self, arguments):
        """
        Make a third of the wheel bet. (bool)

        Parameters:
        arguments: The amount to bet. (str)
        """
        int_args = self.int_re.findall(arguments)
        if int_args:
            numbers, bet = self.check_bet('third {}'.format(int_args[-1]))
            full_bet = bet * 6
            if '5-8-10-11' in arguments or 'ferrari' in arguments.lower():
                full_bet = bet * 10
            if full_bet > self.scores[self.human.name]:
                self.human.tell('You do not have enough money for the full bet.')
            elif numbers:
                self.bets.append(('split bet on 5-8', ['5', '8'], bet))
                self.bets.append(('split bet on 10-11', ['10', '11'], bet))
                self.bets.append(('split bet on 13-16', ['13', '16'], bet))
                self.bets.append(('split bet on 23-24', ['23', '24'], bet))
                self.bets.append(('split bet on 27-30', ['27', '30'], bet))
                self.bets.append(('split bet on 33-36', ['33', '36'], bet))
                if '5-8-10-11' in arguments:
                    self.bets.append(('single bet on 5', ['5'], bet))
                    self.bets.append(('single bet on 8', ['8'], bet))
                    self.bets.append(('single bet on 10', ['10'], bet))
                    self.bets.append(('single bet on 11', ['11'], bet))
                elif 'ferrari' in arguments.lower():
                    self.bets.append(('single bet on 8', ['8'], bet))
                    self.bets.append(('single bet on 11', ['11'], bet))
                    self.bets.append(('single bet on 23', ['23'], bet))
                    self.bets.append(('single bet on 30', ['30'], bet))
                self.scores[self.human.name] -= full_bet
        else:
            self.human.tell('You must give an amount to bet.')
        return True

    def do_top(self, arguments):
        """
        Make a five number bet incluidng the zeros. (bool)

        Parameters:
        arguments: The ammount to bet. (str)
        """
        words = arguments.split()
        if words[0].lower() != 'line':
            words = ['line'] + words
        numbers, bet = self.check_bet(' '.join(words))
        if numbers and self.layout == 'american':
            self.scores[self.human.name] -= bet
            self.bets.append(('top line bet', ('0', '00', '1', '2', '3'), bet))
        elif numbers:
            self.human.tell('That bet can only be made on an American layout.')
        return True

    def do_trio(self, arguments):
        """
        Make a bet on a zero and two numbers next to it. (bool)

        Parameters:
        arguments: The number to bet on and the bet. (str)
        """
        numbers, bet = self.check_bet(arguments)
        if numbers:
            if self.layout == 'american':
                valid = numbers in ('0-1-2', '0-00-2', '00-2-3')
            else:
                valid = numbers in ('0-1-2', '0-2-3')
            if valid:
                self.scores[self.human.name] -= bet
                self.bets.append(('trio bet on {}'.format(numbers), numbers.split('-'), bet))
            else:
                self.human.tell('That is not a valid trio on this layout.')
        return True

    def do_zero(self, arguments):
        """
        Make a zero game bet. (bool)

        Parameters:
        arguments: The amount to bet. (str)
        """
        int_args = self.int_re.findall(arguments)
        if self.layout == 'french' and int_args:
            numbers, bet = self.check_bet('zero {}'.format(int_args[-1]))
            full_bet = bet * 4
            if 'naca' in arguments.lower():
                full_bet = bet * 5
            if full_bet > self.scores[self.human.name]:
                self.human.tell('You do not have enough money for the full bet.')
            elif numbers:
                self.bets.append(('split bet on 0-3', ['0', '3'], bet))
                self.bets.append(('split bet on 12-15', ['12', '15'], bet))
                self.bets.append(('single bet on 26', ['26'], bet))
                self.bets.append(('split bet on 32-35', ['32', '35'], bet))
                if 'naca' in arguments.lower():
                    self.bets.append(('single bet on 19', ['19'], bet))
                self.scores[self.human.name] -= full_bet
        elif int_args:
            self.human.tell('This bet is only available on the French layout.')
        else:
            self.human.tell('You must give an amount to bet.')

    def game_over(self):
        """Determine the end of game. (bool)"""
        if self.scores[self.human.name] == 0:
            self.win_loss_draw[1] = 1
            return True
        else:
            return False

    def handle_options(self):
        """Handle the game options. (None)"""
        self.layout = 'american'
        self.numbers = [str(number) for number in range(37)]
        self.stake = 100
        self.max_bet = 10
        self.uk_rule = False
        if self.raw_options.lower() == 'none':
            pass
        elif self.raw_options:
            self.flags |= 1
            for word in self.raw_options.lower().split():
                if word == 'american':
                    self.layout = 'american'
                elif word == 'french':
                    self.layout = 'french'
                elif word == 'uk-rule':
                    self.uk_rule = True
                elif '=' in word:
                    option, value = word.split('=')
                    if option == 'stake':
                        if value.isdigit():
                            self.stake = int(value)
                        else:
                            self.human.tell('Invalid value for stake= option: {!r}'.format(value))
                    elif option == 'max-bet':
                        if value.isdigit():
                            self.stake = int(value)
                        else:
                            self.human.tell('Invalid value for max-bet= option: {!r}'.format(value))
                    else:
                        self.human.tell('Invalid option for roulette: {}=.'.format(option))
                else:
                    self.human.tell('Invalid option for roulette: {}.'.format(word))
        else:
            if self.human.ask('Would you like to change the options? ') in utility.YES:
                self.flags |= 1
                query = 'What stake do you want to start with? '
                self.stake = self.human.ask_int(query, low = 1, default = 100, cmd = False)
                query = 'French or American (return for American)? '
                layouts = ['french', 'american']
                self.layout = self.human.ask_valid(query, valid = layouts, default = 'american')
                query = 'Should the UK rule (1/2 back on lost 1:1 bets) be in effect? '
                self.uk_rule = self.human.ask(query) in utility.YES
        if self.layout == 'american':
            self.numbers.append('00')

    def neighborhood(self, number, width, bet):
        """
        Bet on adjacent numbers on the wheel. (None)

        Parameters:
        number: The center of the neighborhood. (str)
        width: How many numbers there are in the neighborhood. (int)
        bet: The amount of each bet. (int)
        """
        if bet * width > self.scores[self.human.name]:
            self.human.tell('You do not have enough money for the full bet.')
        elif number:
            if number in self.numbers:
                if self.layout == 'french':
                    wheel = self.french
                else:
                    wheel = self.american
                location = wheel.index(number)
                for index in range(location - width // 2, location + width // 2 + 1):
                    slot = wheel[index % len(wheel)]
                    self.bets.append(('single on {}'.format(slot), [slot], bet))
                self.scores[self.human.name] -= width * bet

    def pay_out(self, winner):
        """
        Payout all bets. (None)

        Parameters:
        winner: The winning number. (str)
        """
        total_winnings = 0
        for text, target, bet in self.bets:
            if winner in target:
                self.human.tell('Your {} won!'.format(text))
                winnings = bet * (36 // len(target))
                self.human.tell('You won {} bucks!'.format(winnings))
                self.scores[self.human.name] += winnings
                total_winnings += winnings
            else:
                self.human.tell('Your {} lost.'.format(text, target))
                if self.uk_rule and len(target) == 18:
                    self.scores[self.human.name] += bet // 2
        self.bets = []
        if total_winnings:
            self.human.tell('Your total winnings this spin were {} bucks.'.format(total_winnings))
        else:
            self.human.tell('You did not win anything this spin.')

    def player_turn(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        player.tell('\nYou have {} bucks.'.format(self.scores[player.name]))
        move = player.ask('Enter a bet or spin: ')
        return self.handle_cmd(move)

    def set_up(self):
        """Set up the game. (None)"""
        self.scores = {self.human.name: self.stake}
        self.bets = []

