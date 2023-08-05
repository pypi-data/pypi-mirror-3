from nose.tools import *
from lexicon import *
from aliens import *

walls = {
    'start_room': ('south','asdfasdgasdfasdfasdfasdfasdfa'),
    'laser_room': ('north','south'),
    'strip_room': ('north','south','west'),
    'clue_room': ('north','south'),
    'guess_room': ('west','east'),
    'farm_room': ('north','east'),
    'guard_room': ('north','south'),
    'alf_room': ('north','west','south'),
    'answer_room': ('north','south','east'),
    'beast_room': ('north','south')
}





def test():
    lex()


class lex(object):
    def __init__(self):

        self.walls()
        self.compass()

    def walls(self):
        #These are impossible routes. Just checking to see that the lexicon is returning 'wall' for them. runner() in main.py will be able to handle these errors.
        assert_equal(scanner('start_room','south'), 'wall')

        assert_equal(scanner('laser_room','south'), 'wall')
        assert_equal(scanner('laser_room','north'), 'wall')

        assert_equal(scanner('strip_room','west'), 'wall')
        assert_equal(scanner('strip_room','south'), 'wall')
        assert_equal(scanner('strip_room','north'), 'wall')

        assert_equal(scanner('clue_room','north'), 'wall')
        assert_equal(scanner('clue_room','south'), 'wall')

        assert_equal(scanner('farm_room','north'), 'wall')
        assert_equal(scanner('farm_room','east'), 'wall')

        assert_equal(scanner('guard_room','north'), 'wall')
        assert_equal(scanner('guard_room','north'), 'wall')

        assert_equal(scanner('alf_room','north'), 'wall')
        assert_equal(scanner('alf_room','south'), 'wall')
        assert_equal(scanner('alf_room','west'), 'wall')

        assert_equal(scanner('answer_room','north'), 'wall')
        assert_equal(scanner('answer_room','south'), 'wall')
        assert_equal(scanner('answer_room','east'), 'wall')

        assert_equal(scanner('beast_room','north'), 'wall')
        assert_equal(scanner('beast_room','south'), 'wall')

        assert_equal(scanner('guess_room','east'), 'wall')
        assert_equal(scanner('guess_room','west'), 'wall')

#ROOMS = ('start_room', 'laser_room', 'strip_room', 'clue_room', 'farm_room', 'guard_room', 'alf_room', 'answer_room', 'beast_room','guess_room')

    def compass(self):
        #Checking lexicon scanner to see if it is returning 'north' from the string it got. The level is irrelevant for this test.
        assert_equal(scanner('start_room','go north fool north'),'north') 
        assert_equal(scanner('guess_room','travel south'), 'south') #used guess_room because start_room has a southern wall
        assert_equal(scanner('start_room', 'head west'), 'west')
        assert_equal(scanner('start_room','move east'),'east')

test()
