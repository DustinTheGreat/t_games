"""
thoughtful_game.py

Okay: When you undo a move, you want the blocked index to revert to what it was
before that move was made. So you want the blocked index at the same point as
a given move to be the one after that move was made.

Classes:
Thoughtful: A game of Thoughtful Solitaire. (solitaire.Solitaire)
"""


import t_games.card_games.solitaire_games.solitaire_game as solitaire


CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
Thoughtful Solitaire is an open version of Klondike, so all card are dealt face
up. As in Klondike, you can build any card on the top of a tableau pile onto
another tableua card this the opposite color and one rank higher. You can move
complete stacks built in that way as well. The top card of any tableau pile may
also sorted to the foundations going up and in suit. Empty lanes may be filled
with a king.

In addition there are eight reserve piles. The top card from any reserve pile
may be built to the tableau or sorted to the foundations as stated above.
However, once you pull a card from a reserve pile, all the reserve piles to the
left of that reserve pile will be blocked (as indicated by an XX at the bottom
of the pile). They can be unblocked with the turn command. This simulates going
through the stock three cards at a time as in normal Klondike.
"""


class Thoughtful(solitaire.Solitaire):
    """
    A game of Thoughtful Solitaire. (Solitaire)

    Attributes:
    blocked_index: The index of the rightmost blocked reserve pile. (int)

    Methods:
    turn_transfer: Move a card while undoing a turn move. (None)

    Overridden Methods:
    do_turn
    reserve_text
    set_checkers
    set_options
    set_up
    transfer
    """

    aka = ['Thoughtful', 'ThSo']
    credits = CREDITS
    name = 'Thoughtful Solitaire'
    rules = RULES

    def do_turn(self, arguments):
        """
        Turn cards from the stock into the waste. (t)

        This command takes no arguments. The cards in the reserved are moved left from
        the bottom up until all piles (except maybe the last one) have three cards.
        """
        start_moves = len(self.moves)
        # Get the first pile needing cards.
        for pile_index, pile in enumerate(self.reserve):
            if len(pile) < 3:
                start_pile = pile_index
                break
        # Get the first pile to the right with cards.
        end_pile = start_pile + 1
        for pile_index, pile in enumerate(self.reserve[end_pile:], start = end_pile):
            if pile:
                end_pile = pile_index
                break
        # Loop through the remaining cards.
        undo = 0
        while end_pile < self.options['num-reserve']:
            # Move the next card to the stack needing one.
            self.transfer([self.reserve[end_pile][0]], self.reserve[start_pile], undo_ndx = undo)
            # Update the undo count so it's treated as one move.
            undo += 1
            # Update the end pile.
            while end_pile < self.options['num-reserve'] and not self.reserve[end_pile]:
                end_pile += 1
            # Update the start pile if necessary.
            if len(self.reserve[start_pile]) == 3:
                start_pile += 1
                # Start pile and end pile can't be the same pile, it will reverse itself infinitely.
                if start_pile == end_pile:
                    end_pile += 1
                    while end_pile < self.options['num-reserve'] and not self.reserve[end_pile]:
                        end_pile += 1
        # how to deal with turns that don't move anything?
        # you have to be able to do it, and it has to change the blocked_index.
        if start_moves == len(self.moves):
            pile_index = -1
            try:
                while not self.reserve[pile_index]:
                    pile_index = -1
            except IndexError:
                self.human.error('There is nothing to turn.')
                return True
            self.transfer([self.reserve[pile_index][0]], self.reserve[pile_index])
        self.blocked_index = -1
        self.blocked_history[-1] = -1

    def do_undo(self, arguments):
        """
        Undo one or more previous moves. (u)

        If this command is called with no arguments, one move is undone. If an integer
        argument is given, that many moves are undone.
        """
        super(Thoughtful, self).do_undo(arguments)
        self.blocked_history = self.blocked_history[:len(self.moves)]
        if self.blocked_history:
            self.blocked_index = self.blocked_history[-1]
        else:
            self.blocked_index = -1

    def reserve_text(self):
        """Generate text for the reserve piles. (str)"""
        # Set up a blank reserve.
        max_reserve = max([len(pile) for pile in self.reserve])
        reserve_lines = [['  ' for pile in self.reserve] for row in range(max_reserve)]
        # Fill in the cards.
        for pile_index, pile in enumerate(self.reserve):
            for card_index, card in enumerate(pile):
                reserve_lines[card_index][pile_index] = str(card)
        if self.blocked_index != -1:
            reserve_lines.append(['XX'] * (self.blocked_index + 1))
        # Format and return as a string.
        return '\n'.join(['{}'.format(' '.join(line)) for line in reserve_lines])

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        super(Thoughtful, self).set_checkers()
        # Set the game specific rules checkers.
        self.build_checkers = [solitaire.build_unblocked]
        self.lane_checkers = [solitaire.lane_king, solitaire.lane_unblocked]
        self.pair_checkers = [solitaire.pair_down, solitaire.pair_alt_color]
        self.sort_checkers = [solitaire.sort_ace, solitaire.sort_up, solitaire.sort_unblocked]
        # Set the dealers (deal_reserve_n won't match Klondike deal, make new dealer?)
        self.dealers = [solitaire.deal_klondike, solitaire.deal_reserve_n(24, True), solitaire.deal_open]

    def set_options(self):
        """Define the options for the game. (None)"""
        self.options = {'num-reserve': 8}

    def set_up(self):
        """Set up the game. (None)"""
        super(Thoughtful, self).set_up()
        self.blocked_index = -1
        self.blocked_history = []

    def transfer(self, move_stack, new_location, track = True, up = True, undo_ndx = 0):
        """
        Move a stack of cards from one game location to another. (None)

        This handles the card's knowledge of where it is and tracking game moves.

        Parameters:
        move_stack: The stack of cards to move. (list of Card)
        new_location: The new game location for the cards. (list of Card)
        track: A flag for tracking the move. (bool)
        up: A flag for the cards being face up. (bool)
        undo_ndx: Nominally how many undos there are to do. (int)
        """
        old_location = move_stack[0].game_location
        if new_location in self.reserve and old_location in self.reserve and not track:
            self.turn_transfer(move_stack, new_location)
        else:
            super(Thoughtful, self).transfer(move_stack, new_location, track, up, undo_ndx)
            if track:
                # Check by id() to avoid matching empty lists across areas.
                if not undo_ndx and id(old_location) in [id(pile) for pile in self.reserve]:
                    self.blocked_index = self.reserve.index(old_location) - 1
                while self.blocked_index > -1 and not self.reserve[self.blocked_index]:
                    self.blocked_index -= 1
                self.blocked_history.append(self.blocked_index)

    def turn_transfer(self, move_stack, new_location):
        """
        Move a card while undoing a turn move. (None)

        This version prepends the card to the new_location rather than appending it.

        Parameters:
        move_stack: The stack of cards to move. (list of Card)
        new_location: The new game location for the cards. (list of Card)
        """
        # Record the move.
        old_location = move_stack[0].game_location
        # Move the cards.
        for card in move_stack:
            old_location.remove(card)
            new_location.insert(0, card)
        # Reset location tracking.
        for card in move_stack:
            card.game_location = new_location
