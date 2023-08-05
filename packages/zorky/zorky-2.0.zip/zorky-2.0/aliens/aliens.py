#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        Aliens
# Purpose:     Text based adventure game
#
# Author:      Jose Luis Naranjo Gomez
#
# Created:     05/12/2011
# Copyright:   (c) Jose Luis Naranjo Gomez 2011
# License:     GPL
#-------------------------------------------------------------------------------

from descriptions import descriptions
from random import randint
from sys import exit
import lexicon
import guess_game
import behemoth_battle
from sneak import sneak
import aliens_tests
def dead(why):
    print "MISSION FAILED\n"
    print "="*72
    print why
    print "Try Again!"
    print "Thanks for playing!"
    print "\t-Luis (Developer)"

    exit(0)

def win(why):
    print "MISSION ACCOMPLISHED\n"
    print '='*72
    print why
    print "Success! You escaped! Congratulations!"
    print "Thanks for playing!"
    print "\t-Luis (Developer)"
    exit(0)

class rooms(object):

    def resets(self):
        reset = {
            'laser': False,
            'laser_grabbed': False,
            'lock' : True,
            'behemoth': True,
            'animal': True,
            'guard': True
        }
        return reset

    def start_room(self, dec):
#Finished
        
        if dec == 'north':
            return 'guess_room'
            
        if dec == 'west':
            return 'laser_room'
            
        if dec == 'east':
            return 'clue_room'
            
        else:
            return 'start_room'

    def laser_room(self, dec):
#Finished
        if dec =='laser' and variable['laser_grabbed'] == True:
            
            print "You can't pick up the laser anymore!"
            
        if dec == 'laser' and variable['laser'] == True:
            
            print "You already have a laser!"
            print "You can't grab another one!"
            return 'laser_room'
        
        
        if dec == 'laser' and variable['laser'] == False and variable['laser_grabbed'] == False:
            
            variable['laser'] = True
            variable['laser_grabbed'] = True
            
            print "You picked up the laser!"
            

        if dec == 'west':
            return 'strip_room'
            
        if dec == 'east':
            return 'start_room'
            
        else:
            return 'laser_room'
            
    def strip_room(self, dec):
#Finished        
        if dec == 'peek':
            
            print "You peek into the tunnel."
            print "You hear a terrible shriek, and you find yourself face to"
            print "face with an ugly little critter."""
            

            if variable['laser'] == False:
                print "He bites you and then scampers off!"
                health['player'] -= 1
                print "You have %d health points remaining." % health['player']
            
            if variable['laser'] == True:
                print "He grabs your laser and scampers off!"
                variable['laser'] = False
                return 'strip_room'
            
        if dec == 'east':
            return 'laser_room'
            
        else:
            return 'strip_room'
            
    def clue_room(self, dec):
#Finished - needs text
        if dec == 'clue':
            
            print "The number you are seeking is from 'A Hitchiker's Guide to the Galaxy'"
            print ", the answer to the universe."
            return 'clue_room'

        if dec == 'east':
            return 'beast_room'
            
        if dec == 'west':
            return 'start_room'
            
        else:
            return 'clue_room'

    def guess_room(self, dec):
#Finished
        if dec == 'cheat':
            variable['lock'] = False
            print "Door unlocked."
            return 'guess_room'
            
        if dec == 'button':
            result = guess_game.guess()
            
            if result == 'lose' or result == 'tie':
                
                print "Sorry! The lock stays."
                return 'guess_room'
            
            if result == 'win':
                
                variable['lock'] = False
                print "The door is unlocked."
                return 'guess_room'
            
        if dec == 'north' and variable['lock'] == False:
            return 'farm_room'
        
        if dec == 'north' and variable['lock'] == True:
            print "Sorry! That door is locked!"
            return 'guess_room'

        if dec == 'south':
            return 'start_room'

        else:
            return 'guess_room'

    def farm_room(self, dec):
#Finished
        if dec == 'kill':
            print "\nYou ought to be ashamed of yourself."
            variable['animal'] = False
            return 'farm_room'
        
        if dec == 'south':
            return 'guess_room'
            
        if dec == 'west':
            return 'guard_room'

        else:
            return 'farm_room'

    def guard_room(self, dec):
#Finished
        if dec == 'cheat':
            variable['guard'] = False
            print "Guard eliminated."
            return 'guard_room'
        if dec == 'talk':
            if variable['animal'] == False:
                print "\nGuard:\tHey! You're the one that killed my animals!"
                c
                print "Guard:\tI'll teach you a lesson you'll never forget!"
                raw_input("\nHit ENTER to continue dialogue\n")
                print "You:\tI'm sorry!"
                raw_input("\nHit ENTER to continue dialogue\n")
                print "Guard:\tSorry won't cut it!"
                raw_input("\nHit ENTER to continue dialogue\n")
                health['player'] -= 1
                print "You have %d health points remaining." % health['player']
                return 'guard_room'
        
            if variable['animal'] == True and variable['behemoth'] == True:
                print "\nGuard:\tHey. I know the boss wants you locked up."
                print "Guard:\tBut if you do me a favor, I'll let you through."
                print "Guard:\tI need you to kill the beast that is stored in the box."
                print "Guard:\tHe's in a room south-east of here."
                print "Guard:\tDo you want me to take you there?"
                
                teleport = raw_input("> ")
                
                print "\nGuard:\tRemember, if you don't kill him, you don't get through!"
                
                if 'yes' in teleport:
                    return 'beast_room'
                else:
                    return 'guard_room'
                
                
            
            if variable['animal'] == True and variable['behemoth'] == False:
                print "\nGuard:\tGood! You slayed the beast!"
                print "Guard:\tI'll just take a lunch break now..."
                variable['guard'] = False
                
        if dec == 'kill' and variable['laser'] == True:
            print "You killed the guard with your laser!"
            print "\nYour laser is broken now."
            variable['laser'] = False
            variable['guard'] = False
            return 'guard_room'
        
        if dec == 'kill' and variable['laser'] == False:
            dead("The guard murdered you.")
        
        
        if dec == 'sneak':
            result = sneak()
            if result == 'succeed':
                print "\n You successfully sneaked past the guard!"
                return 'alf_room'
            if result == 'fail':
                dead("The guard caught you and killed you.")
        
        
        if dec == 'west' and variable['guard'] == False:
            return 'alf_room'
            
        if dec == 'west' and variable['guard'] == True:
            dead("The guard saw you trying to bust the door open.\nHe killed you on the spot.")
        
        if dec == 'east':
            return 'farm_room'
            
        else:
            return 'guard_room'

    def alf_room(self, dec):
        
        if dec == 'kill':
            
            if variable['laser'] == True:
                win("You killed Alf!\nYou command his goons to drop you off at your base, from his P.A. system.")
                
            if variable['laser'] == False:
                print """You move in closer to Alf, to prepare for the kill.
As you prepare to strike him, he wakes up and trips the secret alarm.
But he was too late. You managed to kill him.
As soon as you finished executing Alf, his small army of soldiers flooded room."""
                dead("You were executed.")
        
        if dec == 'talk':
            
            print "Alf:\tAh, Cohn Jonnor. I'm surprised you've made it this far."
            raw_input("\nHit ENTER to continue dialogue.\n")
            
            if variable['laser'] == True:
                print "Cohn:\tI could kill you right now."
                print "Cohn:\tI'm armed."
                print "Cohn:\tLet me off this ship right now."
                raw_input("\nHit ENTER to continue dialogue.\n")
                
                print "Alf:\tAllright Allright. I'll drop you off somewhere."
                print "Alf:\tJust don't do anything stupid."
                raw_input("\nHit ENTER to continue\n")
                win("Alf dropped you off at your base!")
                
            if variable['laser'] == False:
                print "Cohn:\tLet me off this ship."
                raw_input("\nHit ENTER to continue dialogue.\n")
                if variable['animal'] == False:
                    print "Alf:\tMy pleasure."
                    print "*Alf opens a trap door below you."
                    dead("You fell to your death.")
                
                else:
                    print "Alf:\tNever!"
                    print "*Alf attacks you!"
                    health['player'] -= 1
                    print "You have %d hit points left." % health['player']
                    if health['player'] <= 0:
                        dead("You ran out of health!")
                        
                    print "Alf:\tI'll let you off if you can answer my riddle."
                    print "Alf:\tWhat is the answer to the universe?"
                    guess = raw_input("> ")
                    answer = '42'
                    if guess == answer:
                        win("You answered Alf's riddle correctly, and he let you free!")
                    if guess != answer:
                        dead("You answered Alf's riddle incorrectly, and he had you beheaded!")
        if dec == 'east':
            return 'guard_room'
            
        else:
            return 'alf_room'

    def answer_room(self, dec):
#Finished
        if dec == 'read':
            print "'%s'" % descriptions.answer
            return 'answer_room'
        if dec == 'west':
            return 'beast_room'
            
        else:
            return 'answer_room'

    def beast_room(self,dec):
#Finished
        if dec == 'cheat' and variable['behemoth'] == True:
            print "Behemoth deactivated."
            variable['behemoth'] = False
            return 'beast_room'
        
        if dec == 'behemoth' and variable['behemoth'] == False:
            print "You've already slayed the beast!"
            print "The box is empty, you can get past it now."
            return 'beast_room'
        
        if dec == 'behemoth' and variable['behemoth'] == True:
            print "A behemoth emerges from the box and attacks you!"
            result = behemoth_battle.behemoth()
            
            if result == 'alive':
                print "You slayed the beast!"
                variable['behemoth'] = False
                return 'beast_room'
            
            if result == 'dead':
                dead("The beast slayed you!")
                
            
            if result == 'escape':
                print "YOU BARELY ESCAPED WITH YOUR LIFE."
                health['player'] -= 1
                print "You have %d health points left." % health['player']
                return 'beast_room'
            
            return 'beast_room'
        
        if dec == 'east' and variable['behemoth'] == False:

            return 'answer_room'
        
        if dec == 'east' and variable['behemoth'] == True:
            print "The box is in your way!"
            return 'beast_room'

        if dec == 'west':

            return 'clue_room'
        else:
        
            return 'beast_room'
ROOMS = {
    'start_room': [rooms().start_room,  descriptions.start_room],
    'laser_room': [rooms().laser_room,  descriptions.laser_room],
    'strip_room': [rooms().strip_room,  descriptions.strip_room],
    'clue_room' : [rooms().clue_room,   descriptions.clue_room],
    'guess_room': [rooms().guess_room,  descriptions.guess_room],
    'farm_room': [rooms().farm_room,    descriptions.farm_room],
    'guard_room': [rooms().guard_room,  descriptions.guard_room],
    'alf_room': [rooms().alf_room,  descriptions.alf_room],
    'answer_room': [rooms().answer_room,    descriptions.answer_room],
    'beast_room': [rooms().beast_room,  descriptions.beast_room],
    'resets': [rooms().resets,    None]
}


def runner(map, start):
    next = start

    while True:
        #next = room name
        #room is the room's function without the '()'
        #info is the room's description (str)
        
        if health['player'] <= 0:
            dead('You ran out of health')
            
        room = map[next][0]
        info = map[next][1]

        descriptions().guide(next)
        print info
        words = raw_input("> ")

        dec = lexicon.scanner(next,words)
        
        if dec == 'wall':
            print "You can't go there, there is a wall!"
            runner(ROOMS,next)

        next = room(dec)

        print "\n____________________________\n"


variable = rooms().resets() #variable is a dictionary with all of the global variables, which is returned by the reset method of rooms.

def start():
    aliens_tests.test()
    print descriptions.intro
    print "TIPS:"
    print "\t1)You have two hitpoints. If you run out, you die."
    print "\n\t2)Use compass words to navigate between rooms.\n"
    runner(ROOMS,'start_room')

health = {'player': 2}

if __name__ == '__main__':
    start()
