"""
grail_quest_game.py

An Oregon Trail style game based on Monty Python and the Holy Grail.

Constants:
CREDITS: The credits for the game. (str)
INITIAL_PURCHASES: The text shown before making the initial purchases. (str)
RULES: The rules of the game. (str)

Classes:
OregonTrail: A game of travelling the Oregon Trail. (game.Game)
"""


import datetime
import random
import time

import t_games.game as game
import t_games.utility as utility


CREDITS = """
Original Program and Design: Don Rawitsch, Bill Heinemann, and
    Paul Dillenberger with the Minnesota Educational Computing Consortium.
Python Programming: Craig "Ichabod" O'Brien
"""

INITIAL_PURCHASES = """
You have $700 to spend on the following items:

    * Oxen: You can spend 200 to 300 gold on your steeds. The more you spend,
      the faster you'll go, because you have better animals.
    * Food: The more you have, the less chance there is of getting sick.
    * Bullets: $1 buys a box of 50 bullets. You will need bullets for
      attacks by animals and bandits, and for hunting food.
    * Clothing: This is especially important for the cold weather you will
      face in the mountains.
    * Miscellaneous Supplies: This includes medicine and other things you
      will need for sickness and emergency repairs.
"""

RULES = """
This program simulates a quest over the Oregon Trail from Independence,
Missouri to the Oregon City. You family of five will complete the quest in five
to six months -- if you make it alive.

At the beginning you will need to provision for the trip. You can spend all of
your money at the start of the quest, or you can save some of your gold to
spend at forts along the way when you run low on supplies. However, items
cost more at the forts. You can also go hunting along the way to get more
food.

Whenever you have to use your trusty rifle along the way you will see the words
'type bang'. The faster you type 'bang' and hit the return key, the better luck
you'll have with your rifle.

In general, the commands each day are stop (at the fort, if you see one), hunt
(for food), or continue (without stopping).
"""

TACTICS = """
What are your tactics:
    1) Attack,
    2) Retreat,
    3) Continue on your way,
    4) or Circle the wagons?
"""


class GrailQuest(game.Game):
    """
    A game of travelling the Oregon Trail. (game.Game)

    Class Attributes:
    credits_order: The various credits texts in the order to show. (list of str)
    diseases: The diseases you can catch. (list of str)
    eat_map: Eating responses and their integer value. (dict of str: int)
    hazards: The probabilities and names of the hazards. (list of float, str)
    months: The names of the months of the year. (list of str)
    tactics_map: The tactics aliases with the name in the code. (dict of str: str)

    Attributes:
    bullets: The number of bullets left. (int)
    clothes: The quality of the clothing. (int)
    food: The amount of food left. (int)
    fort_option: A flag for a fort being near enough to visit. (bool)
    mileage: The total miles travelled. (int)
    miscellaneous: The quality of the miscellaneous goods. (int)
    money: How much money the player has left. (int)
    oxen: The quality of the oxen. (int)

    Methods:
    bandit_attack: Handle the bandit attack hazard. (None)
    broken_arm: Handle the broken arms hazard. (None)
    broken_wagon: Handle broken wagon hazard. (None)
    check_hazards: Check for hazardous events along the way. (None)
    cold_weather: Handle cold weather. (None)
    contaminated_water: Handle the contaminated water hazard. (None)
    date_format: Format the current date. (str)
    do_continue: Continue on for maximum speed. (bool)
    do_hunt: Hunt for food. (bool)
    do_stop: Stop at a fort to buy things. (bool)
    eat: Give the player a choice of how much food to eat. (None)
    get_bang: Get the time taken to type bang as a percentage of the max. (float)
    hail_storm: Handle the hail storm hazard. (None)
    heavy_fog: Handle the heavy fog hazard. (None)
    heavy_rain: Handle the heavy rain hazard. (None)
    illness_check: Determine how bad an illness is. (None)
    mountains: Check for passing through mountain ranges. (None)
    obituary: Tell the player they are dead, in case they didn't notice. (None)
    peasants: Handle the peasants hazard. (None)
    poisonous_bunny: Handle the poisonous bunny hazard. (None)
    purchases: Allow the user to make purchases. (None)
    rider_combat: Shoot it out with the riders. (bool)
    riders: Handle random encounters on the road. (None)
    riders_friendly: Handle encounters with friendly riders. (None)
    riders_hostile: Handle encounters with hostile riders. (None)
    river_fording: Handle the river fording hazard. (None)
    show_inventory: Show the current consumables. (None)
    show_status: Show the current game status. (None)
    son_wanders: Handle the peripatetic son hazard. (None)
    steed_shot: Handle the steed getting shot hazard. (None)
    steed_wanders: Handle a steed wandering off hazard. (None)
    victory: Display the victory text. (None)
    wagon_fire: Handle the wagon fire hazard. (None)
    wild_animals: Handle the wild animals hazard. (None)

    Overridden Methods:
    game_over
    player_action
    set_up
    """

    aka = ['ortr']
    aliases = {'c': 'continue', 'fort': 'stop', 'h': 'hunt', 's': 'stop'}
    categories = ['Adventure Games']
    credits = CREDITS
    diseases = ['measles', 'dysentery', 'typhoid', 'cholera', 'pneumonia']
    eat_map = {'p': 1, 'poorly': 1, '1': 1, 'm': 2, 'moderately': 2, '2': 2, 'w': 3, 'well': 3, '3': 3}
    hazards = ((0.06, 'broken_wagon'), (0.11, 'steed_shot'), (0.13, 'broken_arm'),
        (0.15, 'steed_wanders'), (0.17, 'son_wanders'), (0.22, 'contaminated_water'),
        (0.32, 'heavy_rain'), (0.35, 'bandit_attack'), (0.37, 'wagon_fire'), (0.42, 'heavy_fog'),
        (0.44, 'poisonous_bunny'), (0.54, 'river_fording'), (0.64, 'wild_animals'), (0.69, 'cold_weather'),
        (0.95, 'hail_storm'))
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
        'October', 'November', 'December']
    name = 'Quest for the Grail'
    tactics_map = {'1': 'charge', '2': 'run', '3': 'continue', '4': 'defend', 'b': 'defend',
        'build': 'defend', 'badger': 'defend', 'c': 'charge', 'r': 'run', 'w': 'continue',
        'wander': 'continue', 'whistle': 'continue'}

    def bandit_attack(self):
        """Handle the bandit attack hazard. (None)"""
        # Shoot the bullets.
        self.human.tell('Bandits attack!')
        speed = self.get_bang()
        self.bullets -= int(speed * 140)
        # Check for remaining bullets.
        if self.bullets < 1:
            self.human.tell('You ran out of bullets. They got plenty of money.')
            self.money = int(self.money / 3)
        # Handle bad shots.
        if speed > 0.15 or self.bullets < 1:
            self.human.tell('You got shot in the leg and they took one of your oxen.')
            self.human.tell('You better let the doctor look at that.')
            self.injury = 'an attack by bandits'
            self.miscellaneous -= 5
            self.oxen -= 20
        # Handle good shots.
        else:
            self.human.tell("Smoothest sword in the isles, you got 'em!")

    def broken_arm(self):
        """Handle the broken arm hazard. (None)"""
        self.human.tell('Bad news. Your daughter broke her arm.')
        self.human.tell('You had to stop and use supplies to make a sling.')
        self.mileage -= 5 + random.randrange(4)
        self.miscellaneous -= 2 + random.randrange(3)

    def broken_wagon(self):
        """Handle broken wagon hazard. (None)"""
        self.human.tell('One of your wagons breaks down. You lose time and supplies fixing it.')
        self.mileage -= 15 + random.randrange(5)
        self.miscellaneous -= 15

    def check_hazards(self):
        """Check for hazardous events along the way. (None)"""
        # Where in the nine hells did he get this formula from?
        mileage_mod = (self.mileage / 100.0 - 4) ** 2
        if random.random() * 10 <= (mileage_mod + 72) / (mileage_mod + 12) - 1:
            self.riders()
            if self.death:
                return None
        # Check for other events.
        event_check = random.random()
        for cumulative_probability, hazard_name in self.hazards:
            if event_check < cumulative_probability:
                self.human.tell()
                getattr(self, hazard_name)()
                break
        else:
            # If no other events, either illness or peasants.
            if random.random() < 1 - (self.eating_choice - 1) * 0.25:
                self.illness_check()
            else:
                self.indians()
        # Check for mountains.
        self.mountains()
        self.human.ask('Press Enter to continue: ')
        # Rest negative values.
        if self.miscellaneous < 1:
            self.miscellaneous = 0
        if self.food < 1:
            self.food = 0
        if self.bullets < 1:
            self.bullets = 0
        if self.clothing < 1:
            self.clothing = 0

    def cold_weather(self):
        """Handle cold weather. (None)"""
        self.human.tell('Brrrr! Cold weather!')
        # Check for clothing.
        if self.clothing > 22 + random.randrange(4):
            self.human.tell('You have enough clothing.')
        # Otherwise you freeze.
        else:
            self.human.tell("You don't have enough clothing.")
            self.illness_check()

    def contaminated_water(self):
        """Handle the contaminated water hazard. (None)"""
        self.human.tell('The water is unsafe. You spend time finding a clean spring.')
        self.mileage -= 2 + random.randrange(10)

    def date_format(self):
        """
        Format the current date. (str)

        Needed because date.strftime doesn't work before 1900.
        """
        # Get the ordinal for the day of the month.
        digit = self.date.day % 10
        if self.date.day in (11, 12, 13):
            ordinal = 'th'
        elif digit == 1:
            ordinal = 'st'
        elif digit == 2:
            ordinal = 'nd'
        elif digit == 3:
            ordinal = 'rd'
        else:
            ordinal = 'th'
        # Format the date as text.
        parts = (self.months[self.date.month], self.date.day, ordinal, self.date.year)
        return '{} {}{}, {} A.D.'.format(*parts)

    def do_continue(self, arguments):
        """
        Continue on for maximum speed. (c)
        """
        return False

    def do_hunt(self, arguments):
        """
        Hunt for food. (h)

        You need to have at least 40 bullets to hunt.
        """
        # Check for sufficient bullets.
        if self.bullets < 40:
            self.human.error('Tough, you need more bullets to go hunting.')
            return True
        shot = self.get_bang()
        # Really fast gets the food.
        if shot < 0.15:
            self.human.tell('RIGHT BETWEEN THE EYES! You got a big one!')
            self.food += random.randint(52, 57)
            self.bullets -= random.randint(10, 13)
        # Otherwise how fast you are determines your chance of getting food.
        elif random.random() < shot:
            self.human.tell('Sorry, no luck today.')
        else:
            self.human.tell('Nice shot, right through the neck. Feast tonight!')
            self.food += 48 - int(2 * shot)
            self.bullets -= 10 - int(3 * shot)
        self.mileage -= 45

    def do_stop(self, arguments):
        """
        Stop at a fort to buy things. (s, fort)
        """
        # Check for the fort command being invalid
        if not self.fort_option:
            self.human.tell('What fort?')
            return True
        # Enjoy storming the fort!
        else:
            modifier = random.random() / 2 + 0.5
            self.purchases(modifier)
            self.mileage -= 45
            return False

    def eat(self):
        """Give the player a choice of how much food to eat. (None)"""
        # Check for starvation.
        if self.food < 13:
            self.human.tell('You run out of food.')
            self.death = 'starvation'
            return False
        # Get the user's choice.
        options = '\nDo you wish to eat:\n    (1) Poorly\n    (2) Moderately\n    (3) or Well? '
        while True:
            choice = self.human.ask(options).lower()
            if choice in self.eat_map:
                # Convert the choice to integer and process it.
                self.eating_choice = self.eat_map[choice]
                meal = 8 + 5 * self.eating_choice
                if meal < self.food:
                    self.food -= meal
                    break
                else:
                    self.human.error("You can't eat that well.")
            else:
                self.human.error('Sorry, come again?')

    def game_over(self):
        """Check for the end of the game (death or success). (bool)"""
        if self.mileage >= 2040 or self.turns > 17:
            self.win_loss_draw = [1, 0, 0]
            self.victory()
        elif self.death:
            self.win_loss_draw = [0, 1, 0]
            self.obituary()
        else:
            return False
        return True

    def get_bang(self):
        """Get the time taken to type bang as a percentage of the max. (float)"""
        # Get the time.
        start = time.time()
        self.human.ask('Type bang: ')
        taken = time.time() - start
        # Return the percentage of the maximum.
        return min(taken / self.max_bang, 1)

    def hail_storm(self):
        """Handle the hail storm hazard. (None)"""
        self.human.tell('Hail storm damages your supplies.')
        self.mileage -= 5 + random.randrange(10)
        self.bullets -= 200
        self.miscellaneous -= 4 + random.randrange(3)

    def heavy_fog(self):
        """Handle the heavy fog hazard. (None)"""
        self.human.tell('You get lost in heavy fog.')
        self.mileage -= 10 + random.randrange(5)

    def heavy_rain(self):
        """Handle the heavy rain hazard. (None)"""
        # Convert to cold weather later in the year.
        if self.mileage > 950:
            self.cold_weather()
        else:
            # Update the user.
            self.human.tell('It rains hard for several days. You lose time and supplies.')
            # Update the consumables.
            self.food -= 10
            self.bullets -= 500
            self.miscellaneous -= 15
            self.mileage -= 5 + random.randrange(10)

    def illness_check(self):
        """Determine how bad an illness is. (None)"""
        # Eating well helps you get a mild, treatable illness.
        if random.randint(1, 100) < 10 + 35 * (self.eating_choice - 1):
            self.human.tell('You have contracted a mild illness. You have to use some medicine.')
            self.mileage -= 5
            self.miscellaneous -= 2
        # Otherwise there is a chance of a serious but treatable illness.
        elif random.randint(1, 100) < 40 / 4 ** (self.eating_choice - 1):
            self.human.tell('You have contracted a serious illness. You have to use some medicine.')
            self.mileage -= 5
            self.miscellaneous -= 5
        # If the illness is not easily treatable, you get one needing Brother Maynard's attention.
        else:
            self.human.tell('You get extremely ill and must stop for medical attention.')
            self.miscellaneous -= 10
            self.illness = 'illness'
        # If you don't have enough medicine, Brother Maynard will have to treat it.
        if self.miscellaneous < 1:
            self.death = 'illness'

    def mountains(self):
        """Check for passing through mountain ranges. (None)"""
        if self.mileage > 950:
            # Another one of his weird functions.
            mileage_mod = ((self.mileage / 100 - 15) ** 2 + 72) / ((self.mileage / 100 - 15) ** 2 + 12)
            # Check for mountains
            if random.random() * 10 <= 9 - mileage_mod:
                self.human.tell('\nYou have entered rugged mountains.')
                # Check for getting lost.
                if random.random() < 0.1:
                    self.human.tell('You got lost, and spent valuable time trying to find the trail.')
                    self.mileage -= 60
                # Check for steeds falling.
                elif random.random() < 0.11:
                    self.human.tell('One of your steeds fell, losing time and supplies.')
                    self.mileage = max(self.mileage - 20 - random.randrange(30), 0)
                    self.bullets = max(self.bullets - 200, 0)
                # Otherwise it just gets slow.
                else:
                    self.human.tell('The going gets slow.')
                    self.mileage -= 45 + random.randrange(5)
                # The first mountains are the Black Mountains.
                if not self.black_mountains:
                    self.black_mountains = True
                    # Check of a blizzard in the black mountains.
                    if random.random() < 0.2:
                        self.human.tell('You made it safely through the Black Mountains.')
                        if self.mileage < 1700 or self.mount_etna:
                            if self.mileage < 950:
                                self.black_moutains_mileage = True
                    else:
                        self.human.tell('Blizzard in the Black Mountains, time and supplies lost.')
                        self.blizzard = True
                        self.food = max(self.food - 25, 0)
                        self.miscellaneous = max(self.miscellaneous - 10, 0)
                        self.bullets = max(self.bullets - 300, 0)
                        self.mileage -= 30 + random.randrange(40)
                        if self.clothing < 18 + random.randrange(2):
                            self.illness_check()

    def obituary(self):
        """Tell the player they are dead, in case they didn't notice. (None)"""
        # List the cause of death.
        if self.death == 'illness':
            self.death = random.choice(self.diseases)
        self.human.tell('\nYou died from {}.'.format(self.death))
        # Ask a few meaningless questions.
        self.human.tell('There are a few formalities we must go through.')
        answer = self.human.ask('Would you like a minister? ')
        answer = self.human.ask('Would you like a fancy funeral? ')
        if answer.lower() in utility.YES and self.gold < 200:
            self.human.tell("Too bad, you can't afford one.")
        answer = self.human.ask('Would you like use to inform your next of kin? ')
        # Give the condolences.
        self.human.tell('\nWe thank you for this information and we are sorry you did not')
        self.human.tell('manage to find the Holy Grail. Better luck next time.')
        self.human.tell('\n                 Sincerely,')
        self.human.tell('                 Holy Grail Manufacturing and Distribution, Inc.')

    def peasants(self):
        """Handle the peasants hazard. (None)"""
        self.human.tell('\nSome helpful peasants take time out of their busy day mucking filth and')
        self.human.tell('discussing anarcho-syndicalist communes to help you find some food.')
        self.food += 14
        self.human.tell('As you leave you hear one of them muttering something about fairy tale')
        self.human.tell('junkets at tax-payer expense for worthless political appointees.')

    def player_action(self, player):
        """
        Handle a player's action during a turn. (bool)

        Parameters:
        player: The player whose turn it is. (player.Player)
        """
        # Check for medical issues.
        bill = 0
        if self.illness and self.injury:
            bill = 40
        elif self.illness or self.injury:
            bill = 20
        if bill:
            self.human.tell("\nBrother Maynard requests a donation of {} gold.".format(bill))
            if bill > self.gold:
                # If you can't pay the bill, you die. How medieval. Or American.
                self.human.tell("Unfortunately, you don't have enough money to pay him.")
                if self.illness:
                    self.death = 'illness'
                else:
                    self.death = self.injury
                return False
            else:
                # Pay the bill and reset the tracking variables.
                self.gold -= bill
                self.injury = False
                self.illness = False
        # Get the player's action.
        self.show_status()
        action = self.human.ask('\nWhat would you like to do (stop/continue/hunt)? ')
        go = self.handle_cmd(action)
        if not go and not self.force_end and not self.death:
            # Handle the end of the turn.
            self.eat()
            self.mileage += 200 + (self.steeds + self.coconuts - 220) // 5 + random.randrange(10)
            self.check_hazards()
            self.fort_option = not self.fort_option
            self.date += self.fortnight
        return go and not self.death

    def poisonous_bunny(self):
        """Handle the poisonous bunny hazard. (None)"""
        # Update the user.
        self.human.tell('You kill a poisonous bunny rabbit after it bites you.')
        # Update the consumables.
        self.bullets -= 10
        self.miscellaneous -= 5
        # If there is not enough medicine, you die.
        if self.miscellaneous < 1:
            self.human.tell('You die from a rabbit bite because you have no medicine.')
            self.death = 'a poisonous rabbit bite'
        else:
            self.human.tell('You have to use some supplies to stop the venom.')

    def purchases(self, modifier = None):
        """
        Allow the user to make purchases. (None)

        Parameters:
        modifier: The fort cost modifier. (float or None)
        """
        if modifier is None:
            self.human.tell(INITIAL_PURCHASES)
            # Purchase steeds.
            query = 'How much would you like to spend on steeds? '
            self.steeds = self.human.ask_int(query, low = 180, high = 270, default = 0, cmd = False)
            self.gold -= self.steeds
        # Purchase coconuts.
        query = 'How much would you like to spend on coconuts? '
        if modifier is None:
            new_coconuts = self.human.ask_int(query, low = 20, high = 30, default = 0, cmd = False)
            modifier = 1
        else:
            new_coconuts = self.human.ask_int(query, low = 0, high = 3, default = 0, cmd = False)
        self.gold -= new_coconuts
        self.coconuts += int(new_coconuts * modifier)
        # Purchase food.
        query = 'How much would you like to spend on food? '
        new_food = self.human.ask_int(query, low = 0, high = self.gold, default = 0, cmd = False)
        self.gold -= new_food
        self.food += int(new_food * modifier)
        # Purchase bullets.
        query = 'How much would you like to spend on bullets? '
        new_bullets = self.human.ask_int(query, low = 0, high = self.gold, default = 0, cmd = False)
        self.gold -= new_bullets
        self.bullets += int(new_bullets * modifier * 50)
        # Purchase clothing.
        query = 'How much would you like to spend on clothing? '
        new_clothing = self.human.ask_int(query, low = 0, high = self.gold, default = 0, cmd = False)
        self.gold -= new_clothing
        self.clothing += int(new_clothing * modifier)
        # Purchase miscellaneous supplies.
        query = 'How much would you like to spend on miscellaneous supplies? '
        new_miscellaneous = self.human.ask_int(query, low = 0, high = self.gold, default = 0, cmd = False)
        self.gold -= new_miscellaneous
        self.miscellaneous += int(new_miscellaneous * modifier)
        # Inform the player of the balance.
        self.human.tell('\nAfter your purchases, you have {} pieces of gold left.'.format(self.gold))

    def rider_combat(self, speed):
        """
        Shoot it out with the riders. (bool)

        Parameters:
        speed: How fast the user typed 'bang'. (float)
        """
        if speed < 0.15 and self.bullets:
            self.human.tell('Nice shooting, you drove them off.')
        elif speed > 0.6:
            self.human.tell('Lousy shooting. You got run through with a sword.')
            self.human.tell("You'll have to see Brother Maynard about that.")
            self.injury = 'an attack by riders'
        else:
            self.human.tell('Kind of slow, there, but you manage.')

    def riders(self):
        """Handle random encounters on the road. (None)"""
        # Warn the player of riders.
        self.human.tell('\nYou see riders ahead.')
        hostile = random.random() < 0.8
        if hostile:
            self.human.tell('They appear hostile.')
        # Get the player's tactics.
        while True:
            raw_tactics = self.human.ask(TACTICS.rstrip() + ' ')
            tactics = raw_tactics.lower().split()[0]
            tactics = self.tactics_map.get(tactics, tactics)
            if tactics in ('charge', 'run', 'continue', 'defend'):
                break
            self.human.error('Oh, the old {!r} trick, eh? Not this time boyo.'.format(raw_tactics))
        # Check for actual hostility.
        if random.random() < 0.2:
            hostile = not hostile
        # Handle hostile riders.
        if hostile:
            self.riders_hostile(tactics)
        # Handle friendly riders.
        else:
            self.riders_friendly(tactics)

    def riders_friendly(self, tactics):
        """
        Handle encounters with friendly riders. (None)

        Parameters:
        tactics: The user's tactical decision. (str)
        """
        # Any tactics besides walking on past are a loss.
        if tactics == 'run':
            self.mileage += 15
            self.steeds = max(self.steeds - 9, 0)
            self.coconuts = max(self.coconuts - 1, 0)
        elif tactics == 'attack':
            self.mileage -= 5
            self.bullets = max(self.bullets - 100, 0)
        elif tactics == 'defend':
            self.mileage -= 20
        self.human.tell('The riders were friendly.')

    def riders_hostile(self, tactics):
        """
        Handle encounters with hostile riders. (None)

        Parameters:
        tactics: The user's tactical decision. (str)
        """
        # Handle running away (set losses).
        if tactics == 'run':
            self.mileage += 20
            self.miscellaneous = max(self.miscellaneous - 15, 0)
            self.bullets = max(self.bullets - 150, 0)
            self.steeds = max(self.steeds - 36, 0)
            self.coconuts = max(self.coconuts - 4, 0)
        # Handle charging (losses based on speed)
        elif tactics == 'charge':
            speed = self.get_bang()
            self.bullets = max(self.bullets - int(speed * 275) - 80, 0)
            self.rider_combat(speed)
        # Handle defending (trade miscellaneous for bullets)
        elif tactics == 'defend':
            speed = self.get_bang()
            self.bullets = max(self.bullets - int(speed * 200) - 80, 0)
            self.miscellaneous = max(self.miscellaneous - 15, 0)
            self.rider_combat(speed)
        # Handle continuing on (running away withotu steed loss).
        elif tactics == 'continue':
            if random.random() < 0.8:
                self.bullets = max(self.bullets - 150, 0)
                self.miscellaneous = max(self.miscellaneous - 15, 0)
            else:
                self.human.tell('The riders did not attack.')
        # Check for casualties.
        if not self.bullets:
            self.human.tell('You ran out of bullets and got massacred.')
            self.death = 'an attack by riders'

    def river_fording(self):
        """Handle the river fording hazard. (None)"""
        self.human.tell('One of your steeds loses his baggage fording a river.')
        self.human.tell('Spam and clothing are lost.')
        self.food -= 30
        self.clothing -= 20
        self.mileage -= 20 + random.randrange(20)

    def set_up(self):
        """Set up the game. (None)"""
        self.credits_index = 0
        # Set purchasables.
        self.bullets = 0
        self.clothing = 0
        self.coconuts = 0
        self.miscellaneous = 0
        self.food = 0
        self.steeds = 0
        self.minstrels = False
        # Set tracking variables.
        self.date = datetime.date(932, 4, 12)
        self.fortnight = datetime.timedelta(days = 14)
        self.fort_option = True
        self.fort_index = 0
        self.eating_choice = 0
        self.gold = 700
        self.max_bang = 7
        self.mileage = 0
        self.illness = False
        self.injury = ''
        self.death = ''
        self.felt_better = False
        self.blizzard = False
        self.black_mountains = False
        self.mount_etna = False
        self.historian = False
        self.purchases()

    def show_inventory(self):
        """Show the current consumables. (None)"""
        self.human.tell('You have:')
        self.human.tell('{} cans of food,'.format(self.food))
        self.human.tell('{} bullets,'.format(self.bullets))
        self.human.tell('{} gold pieces worth of clothing,'.format(self.clothing))
        self.human.tell('{} gold pieces worth of miscellaneous supplies,'.format(self.miscellaneous))
        self.human.tell('{} coconuts, and'.format(self.coconuts))
        self.human.tell('{} pieces of gold.'.format(self.gold))

    def show_status(self):
        """Show the current game status. (None)"""
        # Show the date.
        self.human.tell('\nToday is {}'.format(self.date_format()))
        # Show any warnings.
        if self.food < 12:
            self.human.tell('You better do some hunting or buy food soon!')
        if self.coconuts < 11:
            self.human.tell('Your steeds have just about beaten those coconuts to death.')
        if self.fort_option:
            self.human.tell('You can see a fort in the distance.')
        # Show the distance travelled.
        self.human.tell('You have travelled {} miles.\n'.format(self.mileage))
        # Show the available supplies.
        self.show_inventory()

    def son_wanders(self):
        """Handle the peripatetic son hazard. (None)"""
        self.human.tell("Your son wanders off. You lose time searching for him.")
        self.mileage -= 10

    def steed_shot(self):
        """Handle the steed getting shot hazard. (None)"""
        self.human.tell('One of your steeds was shot by an arrow with a plot device tied to it.')
        self.human.tell('This will slow you down the rest of your trip.')
        self.mileage -= 25
        self.steeds -= 18
        self.coconuts -= 2

    def steed_wanders(self):
        """Handle a steed wandering off hazard. (None)"""
        self.human.tell('A steed wanders off looking for coconuts dropped by spbullets.')
        self.human.tell('You have to spend time looking for it.')
        self.mileage -= 17

    def victory(self):
        """Display the victory text. (None)"""
        if self.historian:
            # Arrest the user if they killed the historian.
            self.human.tell('\nThe police are waiting for you at the Holy Grail, and arrest you')
            self.human.tell('for the wanton murder of an innocent historian.')
            self.win_loss_draw = [0, 1, 0]
        else:
            # Otherwise they win the game.
            self.human.tell('\nCongratulations! You found the Holy Grail!')
            self.human.tell('Be sure to read all warnings and directions. May not be legal in all states.')
            self.human.tell('Hand wash only, do not put in the microwave.\n')
            self.show_inventory()
            # Score based on how fast they got to Castle Aaaarrrggghhh.
            if self.mileage < 2040:
                self.scores[self.human.name] = 1
            else:
                self.scores[self.human.name] = 20 - self.turns

    def wagon_fire(self):
        """Handle the wagon fire hazard. (None)"""
        # Update the user.
        self.human.tell('One of your wagons catches on fire.')
        self.human.tell('You lost food and supplies.')
        # Update the consumables.
        self.food -= 40
        self.bullets -= 400
        self.miscellaneous -= random.randrange(8) + 3
        self.mileage -= 15

    def wild_animals(self):
        """Handle the wild animals hazard. (None)"""
        self.human.tell('Wild animals attacks!')
        speed = self.get_bang()
        # Check for bullets.
        if self.bullets < 40:
            self.human.tell('You were low on bullets and the wolves overpowered you.')
            else:
                self.death = 'a wolf attack'
        # Otherwise base result on speed.
        elif speed < 0.45:
            self.human.tell("Nice shootin' pardner. They did not get much.")
        else:
            self.human.tell('Slow on the draw. They got at your food and clothes.')
        # Update consumables.
        self.bullets -= int(140 * speed)
        self.clothing -= int(30 * speed)
        self.food -= int(55 * speed)

