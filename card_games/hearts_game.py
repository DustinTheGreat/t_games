"""
hearts_game.py

A game of Hearts.

Constants:
CREDITS: The credits for Hearts. (str)
RULES: The rules to Hearts. (str)

Classes:
HeartBot: A simple bot for Hearts. (player.Bot)
Hearts: A game of Hearts. (game.Game)
"""


import itertools
import random
import re

from .. import cards
from .. import game
from .. import player
from .. import utility


CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
In the standard four player game, 13 cards are dealt to each player. Each
player chooses three cards to pass to their right, and recieves three cards
from their left.

The player to the left of the dealer starts by playing a card. Each player in
turn must play a card, matching the suit of the first card if they can. Whoever
plays the highest card in the suit of the first card (the suit led) wins the
trick and all of the cards.

When all the cards are played the round is scored. Each heart won in a trick
scores one point, and the Queen of Spades scores 13 points. Note that points
are bad: you want to have a low score. Cards that give points are called
penalty cards. If one player manages to get all of the penalty cards, they
shoot the Moon. Instead of getting 26 points, they get no points and every
other player gets 26 points.

After scoring the round, the deal shifts to the left, and a new hand is dealt.
The game ends when anyone's score goes over 100 points. Whoever has the least
points at that time wins the game.

Options:
all-break (ab): Hearts may not lead a trick before a penalty card has been
    played.
break-hearts (bh): Hearts may not lead a trick before a heart has been played.
easy= (ez=): The number of easy bots to play against.
end= (e=): The points one players needs to stop the game, defaults to 100.
extras= (x=): How do deal with extra cards where there are not four players.
    Valid settings are:
    ditch (d): Ditch low cards from Clubs and Diamonds to even out hands.
    first (f): The extra cards form a kitty that goes to the winner of the
        first trick.
    heart (h): The extra cards form a kitty that goes to the winner of the
        first heart.
    jokers (j): Jokers are added to the deck to even out the hands.
heart-score= (hs=): How hearts are scored. Valid setting are:
    face (f): Hearts score 1, face cards score more: J = 2, Q = 3, K = 4, A =5.
    one (o): Hearts score one point each.
    pips (p): Hearts score the number of pips on them, face cards and the ace
        score 10 points.
    rank (r): Hearts score their rank in points, with J = 11, Q = 12, K = 13,
        and A = 14.
jokers-follow (jf): Jokers may not lead tricks.
joker-points (jp): Jokers score one point each.
lady-score= (lp=): The points scored for the QS. Defaults to 13, sometimes it
    is 0 or 25.
low-club (lc): The player with the lowest club in the deck (typically 2C) must
    start the first trick of each hand.
keep-spades: Players may not pass the Queen, King, or Ace of Spades.
moon= (m=): How shooting the Moon is scored. Valid settings are:
    old (o): Every player that didn't shoot gains 26 points.
    new (n): The shooting player loses 26 points.
    auto (a): 'Old' unless that would end the game, in which case 'new'.
no-tricks= (nt=): The number of points taken off if a player wins no tricks.
num-pass= (np=): The number of cards passed.
pass-dir= (pd=): The direction in which cards are passed. Valid settings are:
    central (c): Everyone passes to the center. The cards are reshuffled and
        dealt back to the players.
    dealer (d): Dealer's choice.
    left (l): Pass to the left.
    left-right (lr): Alternate passing to the left and right.
    lran: Cards are passed left, then right, then across, then there is a round
        without passing. Rinse and repeat.
    not (n): Cards are not passed at all.
    right (r): Pass to the right (the default).
    right-left (rl): Alternate passing to the right and left.
    rot-left (@): Each round pass to the left of the player you passed to last
        round. Start to the left, and when passing to yourself just don't pass.
    scatter (s): Each player passes one other card to each other player.
"""

class HeartBot(player.Bot):
    """
    A simple bot for Hearts. (player.Bot)

    Attribute:
    hand: The player's cards in the game. (cards.Hand)

    Methods:
    pass_cards: Determine which cards to pass. (list of cards.Card)
    pass_count: Determine how many cards to pass with dealer's choice. (int)
    pass_direction: Determine which direction to pass w/ dealer's choice. (str)
    play: Play a card to start or add to a trick. (card.Card)

    Overridden Methods:
    ask
    ask_int
    set_up
    tell
    """

    def ask(self, prompt):
        """
        Get a response from the bot. (str)

        Parameters:
        prompt: The question to ask the bot. (str)
        """
        # Handle passing.
        if 'want to pass' in prompt:
            return ' '.join(str(card) for card in self.pass_cards())
        # Handle passing cards.
        elif prompt.startswith('What is'):
            card = str(self.play())
            return card
        # Handle dealer's choice of pass direction.
        elif prompt.startswith('What direction'):
            return self.pass_direction()
        # Handle everything else.
        else:
            return super(HeartBot, self).ask(prompt)

    def ask_int(self, prompt, low = None, high = None, valid = [], default = None, cmd = True):
        """
        Get an integer response from the human. (int)

        Parameters:
        prompt: The question asking for the interger. (str)
        low: The lowest acceptable value for the integer. (int or None)
        high: The highest acceptable value for the integer. (int or None)
        valid: The valid values for the integer. (container of int)
        default: The default choice. (int or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        if prompt.startswith('How many cards'):
            self.hand = self.game.hands[self.name]  # This may be asked during game setup, before bot setup.
            return self.pass_count(low, high)
        else:
            return super(HeartBot, self).ask(prompt)

    def pass_cards(self):
        """Determine which cards to pass. (list of card.Card)"""
        # Get rid of high spades.
        if self.game.keep_spades:
            to_pass = []
        else:
            to_pass = [card for card in self.hand if card in ('QS', 'KS', 'AS')]
        # Get rid of high hearts
        hearts = [card for card in self.hand if card.suit == 'H']
        hearts.sort(key = lambda card: card.rank_num, reverse = True)
        to_pass.extend(hearts)
        # If that's not enough, get rid of other high cards.
        if len(to_pass) < self.game.num_pass:
            other = [card for card in self.hand if card not in to_pass]
            other.sort(key = lambda card: card.rank_num, reverse = True)
            to_pass.extend(other)
        return to_pass[:self.game.num_pass]

    def pass_count(self, low, high):
        """
        Determine how many cards to pass with dealer's choice. (int)

        Parameters:
        low: The lowest acceptable value for the integer. (int or None)
        high: The highest acceptable value for the integer. (int or None)
        """
        # Pass just enough to get rid of the nasty cards.
        high_hearts = len([card for card in self.hand.cards if card.suit == 'H' and card.rank_num > 10])
        high_spades = len([card for card in self.hand.cards if card.suit == 'S' and card.rank_num > 11])
        return max(low, min(high, high_hearts + high_spades))

    def pass_direction(self):
        """Determine which direction to pass cards with dealer's choice. (str)"""
        # Who cares, pass randomly.
        return random.choice(('left', 'right', 'across'))

    def play(self):
        """Play a card to start or add to a trick. (card.Card)"""
        # !! refactor
        # Handle continuing a trick.
        if self.game.trick:
            # Get the cards matching the suit led.
            trick_starter = self.game.trick.cards[0]
            trick_cards = [card for card in self.game.trick if card.suit == trick_starter.suit]
            trick_max = sorted(trick_cards, key = lambda card: card.rank_num)[-1]
            point_cards = [card for card in self.game.trick if card.suit == 'H' or card == 'QS']
            if self.game.joker_points:
                point_cards.extend([card for card in self.game.trick if card.rank == 'X'])
            last_player = len(self.game.trick) + 1 == len(self.game.players)
            playable = [card for card in self.hand if card.suit == trick_starter.suit]
            if playable:
                # Get the playable cards that lose.
                playable.sort(key = lambda card: card.rank_num)
                losers = [card for card in playable if card.rank_num < trick_max.rank_num]
                # Play the highest possible loser, or the lowest possible card in hopes of losing.
                if losers and 'QS' in losers:
                    card = 'QS'
                elif losers and last_player and not point_cards:
                    card = playable[-1]
                    if card == 'QS' and len(playable) > 1:
                        card = playable[-2]
                elif losers:
                    card = losers[-1]
                elif last_player:
                    card = playable[-1]
                    if card == 'QS' and len(playable) > 1:
                        card = playable[-2]
                elif playable[0] == 'QS' and len(playable) > 1:
                    card = playable[1]
                else:
                    card = playable[0]
            else:
                # Get rid of the queen if you can.
                if 'QS' in self.hand:
                    card = 'QS'
                # Otherwise get rid of hearts if you can.
                else:
                    hearts = [card for card in self.hand if card.suit == 'H']
                    hearts.sort(key = lambda card: card.rank_num)
                    if hearts:
                        card = hearts[-1]
                    else:
                        # If you have no penalty cards, get rid of the highest card you can.
                        card = sorted(self.hand.cards, key = lambda card: card.rank_num)[-1]
            self.game.human.tell('{} plays the {}.'.format(self.name, card))
        else:
            # Open with the lowest card you have in the hopes of losing.
            self.hand.cards.sort(key = lambda card: card.rank_num)
            play_index = 0
            card = self.hand.cards[play_index]
            # Don't lead with jokers if it's banned.
            while self.game.jokers_follow and card.rank == 'X':
                play_index += 1
                card = self.hand.cards[play_index]
            # Don't lead with hearts if they're not broken.
            while not self.game.hearts_broken and card.suit == 'H':
                play_index += 1
                card = self.hand.cards[play_index]
            # Avoid leading the QS.
            if card == 'QS' and play_index < len(self.hand.cards) - 1:
                card = self.hand.cards[play_index + 1]
            self.game.human.tell('{} opens with the {}.'.format(self.name, card))
        return card

    def set_up(self):
        """Set up the bot. (None)"""
        # Create a shortcut to your hand for easier programming.
        self.hand = self.game.hands[self.name]

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        # Mute.
        pass


class Hearts(game.Game):
    """
    A game of Hearts. (game.Game)

    Attributes:
    all_break: A flag for any penalty card breaking hearts. (bool)
    break_hearts: A flag for hearts needing to be played before leading. (bool)
    breakers: The cards that can break hearts. (set of cards.Card)
    dealer: The next player to deal cards. (player.Player)
    deck: The deck of cards used in the game. (cards.Deck)
    easy: The number of easy bots in the game. (int)
    end: How many points end the game. (int)
    extras: How to handle extra cards in the deck. (str)
    hands: The players' hands of cards. (dict of str: cards.Hand)
    heart_score: How the hearts should be scored. (str)
    heart_points: The points scored by each rank of hearts. (dict of str: int)
    hearts_broken: A flag that hearts can lead. (bool)
    jokers_follow: A flag for jokers being unable to lead tricks. (bool)
    joker_points: A flag for jokers being worth a point. (bool)
    keep_spades: A flag preventing the passing of high spades. (bool)
    lady_points: How many points the QS scores. (int)
    low_club: The club that must lead each round. (cards.Card or False)
    num_pass: The number of cards each player passes. (int)
    pass_dir: The direction(s) that cards are passed. (generator)
    passes: The cards passed by each player. (dict of str: cards.Hand)
    phase: Whether the players are passing cards or playing tricks. (str)
    taken: The cards from the tricks each player has taken. (dict)
    trick: The cards in the current trick. (cards.Hand)
    tricks: The number of trick played so far. (int)
    this_pass: Then direction to pass cards for this hand. (str)

    Class Attributes:
    card_re: A regular expression detecting cards. (re.SRE_Pattern)
    pass_aliases: Aliases of pass-dir option settings. (dict of str: str)
    pass_dirs: The directions to pass for pass-dire settings. (dict)

    Methods:
    deal: Deal the cards to the players. (None)
    dealers_choice: Generator for dealer's choice of passing. (generator)
    do_pass: Pass one or more cards to another player. (bool)
    do_play: Play a card, to either start or contribute to a trick. (bool)
    handle_opt_player: Handle the player option settings for this game. (None)
    handle_opt_deal: Handle the deal option settings for this game. (None)
    handle_opt_pass: Handle the passing option settings for this game. (None)
    handle_opt_play: Handle the play option settings for this game. (None)
    handle_opt_player: Handle the player option settings for this game. (None)
    handle_opt_score: Handle the scoring option settings for this game. (None)
    pass_cards: Handle the actual passing of the cards between players. (None)
    score_players: Score each player's hand. (dict, str)
    score_round: Score one deck's worth of tricks. (None)
    set_dealer: Determine the first dealer for the game. (None)
    set_pass: Set up the passing of cards for this hand. (None)
    trick_winner: Determine who won the trick. (None)

    Overridden Methods:
    game_over
    handle_options
    player_action
    set_up
    """

    aka = ['Black Lady', 'Black Maria', 'Black Widow', '<3']
    aliases = {'p': 'play'}
    card_re = re.compile(r'\s*[x123456789tjqka][cdhs]\s*', re.IGNORECASE)
    categories = ['Card Games']
    credits = CREDITS
    name = 'Hearts'
    num_options = 15
    pass_aliases = {'l': 'left', 'r': 'right', 'rl': 'right-left', 'lr': 'left-right', '@': 'rot-left',
        'c': 'central', 'd': 'dealer', 'n': 'not', 's': 'scatter'}
    pass_dirs = {'left': ('left',), 'right': ('right',), 'left-right': ('left', 'right'),
        'right-left': ('right', 'left'), 'rot-left': (), 'central': ('center',), 'dealer': (),
        'not': ('not',), 'lran': ('left', 'right', 'across', 'not'), 'scatter': ('scatter',)}
    rules = RULES

    def deal(self):
        """Deal the cards to the players. (None)"""
        # Deal the cards out equally, leaving any extras aside.
        self.deck.shuffle()
        player_index = (self.players.index(self.dealer) + 1) % len(self.players)
        for player in itertools.cycle(self.players[player_index:] + self.players[:player_index]):
            self.hands[player.name].draw()
            if player == self.dealer and len(self.deck.cards) < len(self.players):
                break
        for hand in self.hands.values():
            hand.cards.sort(key = lambda card: (card.suit, card.rank_num))
        self.human.tell('{} deals.'.format(self.dealer))
        # Eldest hand starts, and is the next dealer.
        self.dealer = self.players[player_index]
        self.hearts_broken = not (self.break_hearts or self.all_break)
        #print('dealer set to {}.'.format(self.dealer))

    def dealers_choice(self):
        """Generator for dealer's choice of passing. (generator)"""
        # Set the valid choices.
        valid_dirs = ('left', 'right', 'not', 'center', 'scatter', 'across')
        if len(self.players) not in (4, 6):
            valid_dirs = valid[:-1]
        valid_text = 'Please choose {}.'.format(utility.oxford(valid_dirs, 'or'))
        # Generate the direction and the pass count.
        while True:
            # Get the dealer for this deal (self.dealer is dealer for next deal at this point)
            dealer = self.players[self.players.index(self.dealer) - 1]
            dealer.tell('\nYour hand is: {}.'.format(self.hands[dealer.name]))
            # Get a valid direction.
            while True:
                pass_dir = dealer.ask('What direction shoud cards be passed? ')
                pass_dir = self.pass_aliases.get(pass_dir, pass_dir)
                if pass_dir in valid_dirs:
                    break
                dealer.error('{!r} is not a valid choice.'.format(pass_dir))
                dealer.error(valid_text)
            # Get or calculate the pass count.
            if pass_dir == 'scatter':
                self.num_pass = len(self.players) - 1
            elif pass_dir == 'not':
                self.num_pass = 0
            else:
                self.num_pass = dealer.ask_int('How many cards should be passed? ', low = 1, high = 4)
            # Yield the direction.
            yield pass_dir

    def do_pass(self, arguments):
        """
        Pass one or more cards to another player.
        """
        # Get the player and their hand.
        player = self.players[self.player_index]
        hand = self.hands[player.name]
        #print('{} passes {} from {}.'.format(player, arguments, hand))
        # Get the actual card objects.
        cards = [card.strip().upper() for card in self.card_re.findall(arguments)]
        # Make sure all of the cards are in their hand and legal.
        error = False
        for card in cards:
            if card not in hand:
                player.error('You do not have the {}.'.format(card))
                error = True
            elif self.keep_spades and card in ('QS', 'KS', 'AS'):
                player.error('You may not pass the {}.'.format(card))
                error = True
        if error:
            return True
        else:
            # Shift the cards to their passing stack.
            for card in cards:
                hand.shift(card, self.passes[player.name])
            # If everyone has set up a passing stack, actually pass the cards.
            if all(self.passes.values()):
                self.pass_cards()
                self.phase = 'trick'
                # Set the first player.
                if self.low_club:
                    for player in self.players:
                        if self.low_club in self.hands[player.name]:
                            break
                    self.player_index = self.players.index(player) - 1
                else:
                    self.player_index = self.players.index(self.dealer) - 1

    def do_play(self, arguments):
        """
        Play a card, to either start or contribute to a trick.  (p)
        """
        # Get the player and their hand.
        player = self.players[self.player_index]
        hand = self.hands[player.name]
        #print(player.name, hand)
        # Check for a valid card.
        if self.card_re.match(arguments):
            card_text = arguments.upper()
        else:
            player.error('{!r} is not a card in the deck.'.format(arguments))
            return True
        # Check for valid timing.
        if self.phase != 'trick':
            player.error('This is not the right time to play cards.')
            return True
        # Check for possession of the card.
        elif card_text not in hand:
            player.error('You do not have the {} to play.'.format(card_text))
            return True
        to_play = hand.cards[hand.cards.index(card_text)]
        if self.trick:
            # Check that the card follows suit, or that the player is void in that suit.
            trick_suit = self.trick.cards[0].suit
            if to_play.suit != trick_suit and list(filter(lambda card: card.suit == trick_suit, hand)):
                player.error('You must play a card of the suit led.')
                return True
            hand.shift(to_play, self.trick)
        else:
            # Get the player's playable cards.
            playable = hand.cards[:]
            if self.jokers_follow:
                playable = [card for card in playable if card.rank != 'X']
            if not self.hearts_broken:
                playable = [card for card in playable if card.suit != 'H']
            # Validate the card they are leading with.
            if to_play.rank == 'X' and self.jokers_follow and playable:
                player.error('You cannot lead with a joker.')
                return True
            if to_play.suit == 'H' and not self.hearts_broken and playable:
                player.error('You cannot lead with a heart until they are broken.')
                return True
            hand.shift(card_text, self.trick)

    def game_over(self):
        """Determine if the game is over. (bool)"""
        # Check for someone breaking the "winning" score.
        if max(self.scores.values()) >= self.end:
            # Get the scores of interest.
            human_score = self.scores[self.human.name]
            winning_score = min(self.scores.values())
            # Calculate the humans win/loss/draw.
            for name, score in self.scores.items():
                if score > human_score:
                    self.win_loss_draw[0] += 1
                elif score < human_score:
                    self.win_loss_draw[1] += 1
                elif name != human_score:
                    self.win_loss_draw[2] += 1
                # Tell the human who won.
                if score == winning_score:
                    self.human.tell('{} wins with {} points.'.format(name, score))
            # Set the number turns to the number of tricks.
            self.turns = self.tricks
            # Discard the last deal in case they want to play again.
            for hand in self.hands.values():
                hand.discard()
            return True
        else:
            return False

    def handle_opt_deal(self):
        """Handle the deal option settings for this game. (None)"""
        if self.extras[0] == 'd':
            ditch_stack = ['3D', '3C', '2D', '2C']
            while len(self.deck.cards) % len(self.players):
                self.deck.force(ditch_stack.pop())
        elif self.extras[0] == 'f':
            self.kitty = 'first'
        elif self.extras[0] == 'h':
            self.kitty = 'heart'
        elif self.extras[0] == 'j':
            suits = itertools.cycle('CD')
            while len(self.deck.cards) % len(self.players):
                self.deck.cards.append(cards.Card('X', next(suits)))

    def handle_opt_pass(self):
        """Handle the passing option settings for this game. (None)"""
        if not self.num_pass:
            self.num_pass = 3 if len(self.players) < 5 else 2
        self.pass_dir = self.pass_aliases.get(self.pass_dir, self.pass_dir)
        self.not_warning = (self.pass_dir != 'not')
        if self.pass_dir == 'scatter':
            self.num_pass = len(self.players) - 1
        if self.pass_dir == 'rot-left':
            dirs = ['left-{}'.format(player_index) for player_index in range(1, len(self.players) + 1)]
            self.pass_dir = itertools.cycle(tuple(['left'] + dirs[1:-1] + ['not']))
        elif self.pass_dir == 'dealer':
            self.pass_dir = self.dealers_choice()
        else:
            self.pass_dir = itertools.cycle(self.pass_dirs[self.pass_dir])

    def handle_opt_play(self):
        """Handle the play option settings for this game. (None)"""
        if self.low_club:
            clubs = [card for card in self.deck.cards if card.suit == 'C']
            clubs.sort(key = lambda card: card.rank_num, reverse = True)
            self.low_club = clubs.pop()
            while self.jokers_follow and self.low_club.rank == 'X':
                self.low_club = clubs.pop()

    def handle_opt_player(self):
        """Handle the player option settings for this game. (None)"""
        self.players = [self.human]
        if self.easy > 5:
            self.option_set.errors.append('There can be at most five bots in the game.')
        for bot in range(self.easy):
            self.players.append(HeartBot(taken_names = [player.name for player in self.players]))

    def handle_opt_score(self):
        """Handle the scoring option settings for this game. (None)"""
        self.heart_points = {rank: 1 for rank in self.deck.ranks[1:]}
        if self.heart_score[0] == 'f':
            self.heart_points.update({'J': 2, 'Q': 3, 'K': 4, 'A': 5})
        elif self.heart_score[0] == 'p':
            self.heart_points = {rank: min(10, score) for score, rank in enumerate(self.deck.ranks)}
            self.heart_points['A'] = 10
        elif self.heart_score[0] == 'r':
            self.heart_points = {rank: score for score, rank in enumerate(self.deck.ranks)}
            self.heart_points['A'] = 14
        self.max_score = sum(self.heart_points.values()) + self.lady_points
        self.breakers = set([card for card in self.deck.cards if card.suit == 'H'])
        if self.all_break:
            self.breakers.add('QS')
        if self.joker_points:
            jokers = [card for card in self.deck.cards if card.rank == 'X']
            self.max_score += len(jokers)
            if self.all_break:
                self.breakers.update(jokers)
        if self.bonus:
            self.bonus = cards.Card(*self.bonus)
            self.max_score -= 10

    def handle_options(self):
        """Handle the option settings for this game. (None)"""
        super(Hearts, self).handle_options()
        self.handle_opt_player()
        # Set up the deck.
        self.deck = cards.Deck(ace_high = True)
        self.kitty = ''
        self.handle_opt_deal()
        self.handle_opt_pass()
        self.handle_opt_play()
        self.handle_opt_score()

    def pass_cards(self):
        """Handle the actual passing of the cards between players. (None)"""
        # Handle passing to the center.
        if self.this_pass == 'center':
            center = []
            for player in self.players:
                center.extend(self.passes[player.name].cards)
                self.passes[player.name].cards = []
            random.shuffle(center)
            for player in itertools.cycle(self.players):
                self.hands[player.name].cards.append(center.pop())
                if not center:
                    break
        # Handle scatter passing.
        elif self.this_pass == 'scatter':
            for pass_from in self.players:
                for pass_to in self.players:
                    if pass_from != pass_to:
                        self.hands[pass_to.name].cards.append(self.passes[pass_from.name].cards.pop(0))
        # Handle passing from player to player.
        else:
            for pass_from in self.players:
                pass_to = self.pass_to[pass_from.name]
                #print('passing from {} to {}'.format(pass_from, pass_to))
                self.hands[pass_to].cards.extend(self.passes[pass_from.name].cards)
                self.passes[pass_from.name].cards = []
        human_got = self.hands[self.human.name].cards[-self.num_pass:]
        pass_text = utility.oxford(human_got, word_format = 'the {}')
        self.human.tell('You were passed {}.'.format(pass_text))
        # Sort the hands.
        for hand in self.hands.values():
            hand.cards.sort(key = lambda card: (card.suit, card.rank_num))

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Handle passing.
        if self.phase == 'pass':
            # Get the cards to pass.
            player.tell('\nYour hand is: {}.'.format(self.hands[player.name]))
            if self.this_pass == 'scatter':
                pass_text = utility.oxford([other.name for other in self.players if other != player])
            else:
                pass_text = self.pass_to[player.name]
            query = '\nWhich {} do you want to pass to {}? '
            move = player.ask(query.format(utility.number_plural(self.num_pass, 'card'), pass_text))
            # If the correct number of cards are found, pass them.
            if len(self.card_re.findall(move)) == self.num_pass:
                return self.do_pass(move)
            else:
                # If incorrect number of cards, try to run a command.
                return self.handle_cmd(move)
        # Handle playing tricks
        elif self.phase == 'trick':
            # Display the game status.
            if self.trick:
                player.tell('The trick to you is: {}.'.format(self.trick))
            else:
                self.human.tell('')  # Make sure tricks are blocked out in the ouput.
                player.tell('You lead the trick.')
            player.tell('Your hand is: {}.'.format(self.hands[player.name]))
            if self.low_club and self.low_club in self.hands[player.name]:
                text = 'You must play the {1}.' if player == self.human else '{0} plays the {1}.'
                self.human.tell(text.format(player, self.low_club))
                move = self.low_club.up_text
            else:
                move = player.ask('What is your play? ')
            if self.card_re.match(move):
                # Handle card text as plays.
                go = self.do_play(move)
                # Check for the trick being finished.
                if len(self.trick) == len(self.players):
                    self.tricks += 1
                    self.trick_winner()
                return go
            else:
                # Handle other text as commands.
                return self.handle_cmd(move)

    def score_players(self):
        """
        Score each player's hand. (dict, str)

        The return value is a dictionary of the raw points scored, and the name of the
        shooter, if any.
        """
        round_points = {}
        shooter = ''
        for player in self.players:
            # Count the scoring cards.
            hearts, heart_points, lady, jokers = 0, 0, 0, 0
            bonus = None
            for card in self.taken[player.name]:
                if card.suit == 'H':
                    hearts += 1
                    heart_points += self.heart_points[card.rank]
                elif card == 'QS':
                    lady += 1
                elif card.rank == 'X':
                    jokers += 1
                elif card == self.bonus:
                    bonus = card
            # Calculate and store the unadjusted points.
            player_points = heart_points + self.lady_points * lady
            if self.joker_points:
                player_points += jokers
            if self.bonus and bonus:
                player_points = max(0, player_points - 10)
            round_points[player.name] = player_points
            # Display the card counts and points.
            score_text = '{} had {} {}'.format(player.name, hearts, utility.plural(hearts, 'heart'))
            score_bits = ['{} {}'.format(hearts, utility.plural(hearts, 'heart'))]
            if lady:
                score_bits.append('the Queen of Spades')
            if self.joker_points and jokers:
                score_bits.append('{} {}'.format(jokers, utility.plural(jokers, 'joker')))
            if bonus:
                score_bits.append('the {}'.format(bonus.name))
            point_text = '{} {}'.format(player_points, utility.plural(player_points, 'point'))
            base_text = '{} had {}, for {} this round.'
            score_text = base_text.format(player.name, utility.oxford(score_bits), point_text)
            self.human.tell(score_text)
            # Inform and record any sucessful shooter.
            if player_points == self.max_score and (bonus or not self.bonus):
                self.human.tell('{} shot the moon!'.format(player.name))
                shooter = player.name
            # Check for taking no tricks.
            if not self.taken[player.name] and self.no_tricks:
                text = '{} gets {} points taken off for winning no tricks.'
                self.human.tell(text.format(player.name, self.no_tricks))
                round_points[player.name] = -self.no_tricks
        return round_points, shooter

    def score_round(self):
        """Score one deck's worth of tricks. (None)"""
        self.human.tell('')
        # Calculate the points this round for each player.
        round_points, shooter = self.score_players()
        # Adjust the round points if anyone shot the moon.
        if shooter:
            moon_value = self.max_score + 10 * bool(self.bonus)
            auto_old = self.moon[0] == 'a' and max(self.scores.values()) + moon_value < self.end
            if self.moon[0] == 'o' or auto_old:
                for player in round_points:
                    if player == shooter:
                        round_points[player] = 0
                    else:
                        round_points[player] += moon_value
            else:
                round_points[shooter] = -moon_value
        # Adjust and display the overall points.
        self.human.tell('\nOverall Scores:')
        for player in self.players:
            self.scores[player.name] = max(self.scores[player.name] + round_points[player.name], 0)
            self.human.tell('{}: {}'.format(player, self.scores[player.name]))

    def set_dealer(self):
        """Determine the first dealer for the game. (None)"""
        # Deal a card to each player, keeping track of the max rank and who was dealt it.
        self.deck.shuffle()
        max_rank = -1
        players = self.players[:]
        max_players = []
        player_index = 0
        self.human.tell('')
        while True:
            # Deal the card.
            card = self.deck.deal(up = True)
            self.deck.discards.append(card)
            self.human.tell('{} was dealt the {}.'.format(players[player_index], card))
            # Track the max rank.
            if card.rank_num == max_rank:
                max_players.append(players[player_index])
            elif card.rank_num > max_rank:
                max_rank = card.rank_num
                max_players = [players[player_index]]
            player_index += 1
            # Check for unique winner.
            if player_index == len(players):
                if len(max_players) == 1:
                    self.dealer = max_players[0]
                    break
                else:
                    # Redeal to any tied players.
                    if max_rank == 14:
                        # Correct rank index for aces.
                        max_rank = 2
                    self.human.tell("\nThere was a tie of {}'s.".format(self.deck.ranks[max_rank]))
                    max_rank = -1
                    players = max_players
                    max_players = []
                    player_index = 0

    def set_options(self):
        """Set the possible options for the game. (None)"""
        # Get a card verifier.
        def is_card(text):
            return len(text) == 2 and text[0] in cards.Card.ranks and text[1] in cards.Card.suits
        # Set the bot options.
        self.option_set.add_option('easy', ['ez'], int, 3, valid = range(5),
            question = 'How many easy bots do you want to play against (return for 3)? ')
        # Set the deal/card options.
        self.option_set.add_option('extras', ['x'], default = 'ditch',
            valid = ('d', 'ditch', 'f', 'first', 'h', 'heart', 'j', 'joker'),
            question = 'How should extra cards be handled (return for ditch them)? ',
            error_text = 'Please choose ditch, first, heart, or joker.')
        self.option_set.add_option('jokers-follow', ['jf'],
            question = 'Should jokers not be allowed to lead? bool')
        self.option_set.add_option('joker-points', ['jp'],
            question = 'Should jokers score one point each? bool')
        # Set the pass options.
        self.option_set.add_option('keep-spades', ['ks'],
            question = 'Should passing QS, KS, and AS be banned? bool')
        self.option_set.add_option('num-pass', ['np'], int, 0, valid = range(5),
            question = 'How many cards should be passed (return for 3, 2 with 5+ players)? ')
        self.option_set.add_option('pass-dir', ['pd'], default = 'right',
            valid = ('r', 'right', 'l', 'left', 'rl', 'right-left', 'lr', 'left-right', 'lran', 'rot-left',
            '@', 'central', 'c', 'dealer', 'd', 'not', 'n', 'scatter', 's'),
            question = 'In what direction should cards be passed (return for right)? ')
        # Set the play options.
        self.option_set.add_option('all-break', ['ab'],
            question = 'Should hearts not be able to lead until a penalty card is played? bool')
        self.option_set.add_option('break-hearts', ['bh'],
            question = 'Should hearts not be able to lead until a heart is played otherwise? bool')
        self.option_set.add_option('bonus', ['b'], str.upper, '', check = is_card,
            question = 'What card should remove up to 10 points from your score (return for none)? ')
        self.option_set.add_option('low-club', ['lc'],
            question = 'Should the lowest club lead the first trick of each deal? bool')  # !! interaction with kitty
        # Set the score options.
        self.option_set.add_option('heart-score', ['hs'], str.lower, 'one',
            valid = ('o', 'one', 'p', 'pip', 'r', 'rank', 'f', 'face'),
            question = 'How should hearts be scored (one, face, pip or rank, return for one)? ')
        self.option_set.add_option('lady-score', ['ls'], int, 13, valid = range(0, 50),
            target = 'lady_points',
            question = 'How much should the Queen of Spades score (return for 13)? ')
        self.option_set.add_option('moon', ['m'], str.lower, 'old',
            valid = ('a', 'auto', 'n', 'new', 'o', 'old'),
            question = 'How should shooting the Moon be scored (new, auto, or return for old)? ')
        self.option_set.add_option('no-tricks', ['nt'], int, 0, valid = range(0, 25),
            question = 'How many points should be taken off if a player wins no tricks? ')
        self.option_set.add_option('end', ['e'], int, 100, valid = range(50, 1000),
            question = 'How many points for one player should end the game (return for 100)? ')

    def set_pass(self):
        """Set up the passing of cards for this hand. (None)"""
        # Set the game tracking to passing.
        self.phase = 'pass'
        self.this_pass = next(self.pass_dir)
        # Check for not passing.
        if self.this_pass == 'not':
            if self.not_warning:
                self.human.tell('\nThere is no passing this round.')
            self.phase = 'trick'
            return None
        # Translate the pass direction into passees.
        if self.this_pass == 'left':
            pass_to = self.players[1:] + self.players[:1]
        elif self.this_pass == 'right':
            pass_to = self.players[-1:] + self.players[:-1]
        elif self.this_pass == 'across':
            offset = len(self.players) // 2
            pass_to = self.players[offset:] + self.players[:offset]
        elif self.this_pass.startswith('left-'):
            offset = int(self.this_pass.split('-')[1])
            pass_to = self.players[offset:] + self.players[:offset]
        # Set up the passing dictionary.
        if self.this_pass == 'center':
            self.pass_to = {pass_from.name: 'the center' for pass_from in self.players}
        elif self.this_pass == 'scatter':
            self.pass_to = {pass_from.name: self.this_pass for pass_from in self.players}
        else:
            self.pass_to = {passer.name: passee.name for passer, passee in zip(self.players, pass_to)}

    def set_up(self):
        """Set up the game. (None)"""
        # Set up hands, including pseudo-hands for holding various sets of cards.
        self.hands = {player.name: cards.Hand(self.deck) for player in self.players}
        self.passes = {player.name: cards.Hand(self.deck) for player in self.players}
        self.taken = {player.name: cards.Hand(self.deck) for player in self.players}
        self.trick = cards.Hand(self.deck)
        # Handle the initial deal
        self.set_dealer()
        self.deal()
        # Set up the tracking variables.
        self.set_pass()
        self.tricks = 0

    def trick_winner(self):
        """Determine who won the trick. (None)"""
        # Find the winning card.
        trick_suit = self.trick.cards[0].suit
        suit_cards = [card for card in self.trick if card.suit == trick_suit]
        winning_card = sorted(suit_cards, key = lambda card: card.rank_num)[-1]
        card_index = self.trick.cards.index(winning_card)
        # Find the winning player.
        winner_index = (self.player_index + 1 + card_index) % len(self.players)
        winner = self.players[winner_index]
        # Handle the win.
        self.human.tell('\n{} won the trick with the {}.'.format(winner, winning_card))
        self.taken[winner.name].cards.extend(self.trick.cards)
        # Handle any kitty.
        if self.deck.cards:
            kitty_win = self.kitty == 'first'
            kitty_win = kitty_win or 'heart' and [card for card in self.trick.cards if card.suit == 'H']
            if kitty_win:
                self.taken[winner.name].cards.extend(self.deck.cards)
                text = 'You won {} from the kitty.'
                winner.tell(text.format(utility.oxford(self.deck.cards, word_format = 'the {0.up_text}')))
                if winner != self.human:
                    self.human.tell('{} won the kitty.')
                self.deck.cards = []
        # Check for breaking hearts.
        if not self.hearts_broken and self.breakers.intersection(self.trick):
                self.hearts_broken = True
        # Clear the trick.
        self.trick.cards = []
        # Check for the end of the round.
        if not self.hands[self.human.name]:
            self.score_round()
            if max(self.scores.values()) < self.end:
                for hand in self.taken.values():
                    hand.discard()
                self.deal()
                self.set_pass()
        else:
            self.player_index = winner_index - 1
