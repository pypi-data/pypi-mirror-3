class descriptions(object):
    intro = "You are Cohn Jonnor. You are the leader of the resistance. Your squad was captured by the enemy a few blocks away from your hidden base, on a rescue mission. It's only a matter of time before the clinkers discover your woman, Emeline, and what's left of the human race.\nYou seem to be in a spaceship of some sort. Your objective is to get off the ship, so you can alert your buddies of the search party before they are found."


    characters = {'Cohn Jonnor': 'Leader of the resistance. Protagonist. Received military training. Married to Emeline',
              'Emeline': 'Daughter of the president of the United States. Beautiful. No military training. Married to Cohn Jonnor.',
              'Alf' : 'The leader of the clinkers, an alien mafia. A renegade group of aliens that seeks to destroy capitalism, and replace it with an agricultural economy. They are excellent farmers.'}

    rooms_list = ['start_room', 'laser_room','strip_room','clue_room','guess_room','farm_room','guard_room','alf_room','answer_room','beast_room']

    start_room = "You are in an empty room, with four sides."
    laser_room = "There is a laser gun in here."
    strip_room = "There are strange markings on the walls. There are fresh animal droppings on the floor, as well as a small tunnel\n"
    clue_room  = "There is an empty satchel on the ground of this room, but it feels heavy."
    guess_room = "There is a strange device mounted on the northern wall. It has a big red button on it."
    farm_room  = "There are chickens and cows in here."
    guard_room = "As you walk in you spot a guard. You barrel roll into a haystack before he sees you. He seems friendly enough."
    alf_room   = "Alf, the alien farmer mafia leader, is sound asleep in his bed."
    answer_room = "There is an engraved text on the wall."
    beast_room = "There is a giant box in front of the eastern exit."

    answer = "The answer is 42."

    def guide(self,pos):

        sym = {
            'start_room': " ",
            'laser_room': " ",
            'strip_room': " ",
            'clue_room' : " ",
            'guess_room': " ",
            'farm_room' : " ",
            'guard_room': " ",
            'alf_room'  : " ",
           'answer_room': " ",
            'beast_room': " "
        }
        sym[pos] = "*"

        print "------------|"
        print "  %s | %s | %s |" % (sym['alf_room'],sym['guard_room'],sym['farm_room'])
        print "------------|"
        print "        | %s |" % sym['guess_room']
        print "-------------------------"
        print "| %s | %s | %s | %s | %s | %s |" % (sym['strip_room'],sym['laser_room'],sym['start_room'],sym['clue_room'],sym['beast_room'],sym['answer_room'])
        print "-------------------------"
        sym[pos] = " "



