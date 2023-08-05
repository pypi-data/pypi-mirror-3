p1 = 'Cohn Jonnor'
p2 = 'Behemoth'
health = {p1: 100, p2: 100}
actions = ['attack','heal','nuke']
from random import randint
from sys import exit
def attack(p1,p2):
    damage = randint(20,40)
    health[p2] -= damage
    print "\n%s does %d damage to %s!\n" % (p1,damage,p2)
def heal(p1,p2):
    heal = randint(1,20)
    if health[p1] + heal < 100:
        health[p1] += heal
        print "\n%s healed by %d points!\n" % (p1,heal)
    else:    print "\nYou cannot heal this much!\n"
def menu(p1,p2):
    print "\n%s' turn!" % p1
    print "1: Attack\n2: Heal"
    print "Health: %d" % health[p1]
    dec = raw_input("> ")
    if dec == 'end' or dec =='exit':
        print "Goodbye!"
        exit(0)
    if dec == 'cheat':
        health[p2] = -1

    if dec == 'attack' or dec == '1':

        attack(p1,p2)
    if dec == 'heal' or dec == '2':

        heal(p1,p2)

def menu_ai(p1,p2):

    print "Behemoth\nHealth: %s\n" % health[p1]
    
    h = health[p1]
    h2 = health[p2]
    dec = 1
    if h < 55 and h2 < 50:
        dec = 2
    if h < 25:
        dec = 2
    if h > 50 or h2 < 50:
        dec = 1
    if h > 55:
        dec = 1

    if dec == 'attack' or dec == 1:
        print "Behemoth uses attack!"
        attack(p1,p2)
    if dec == 'heal' or dec == 2:
        print "Behemoth uses heal!"
        heal(p1,p2)

def behemoth():
    if health[p2] < 0:
        print "You slayed the beast!"
        return 'dead'
    if health[p1] < 0:
        return 'alive'
    while health[p1] > 0 and health[p2] > 0:
        if health[p2] < 0 or health[p1] < 0:
            break
        if health[p1] < 15:
            break
        print "---------------------------------------- "
        menu(p1,p2)

        if health[p2] < 0 or health[p1] < 0:
            break
        print "---------------------------------------- "
        raw_input("Hit ENTER for Behemoth's turn!")
        print "---------------------------------------- "
        menu_ai(p2,p1)

        if health[p2] < 0 or health[p1] < 0:
            break

    if health[p2] < 0:
        #print "You slayed the beast!"
        return 'alive'
    
    if health[p1] < 0:
        return 'dead'
    
    if health[p1] < 15:
        return 'escape'

      

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def pick_lock():
    print "In order to break the lock, you have to guess the correct number!"
    print "I'm thinking of a number between 1 and 10.\nWhat is it?"
    num = randint(1,10)
    print num
    decision   = raw_input("> ")


    try:
        if int(decision) == num:
            return 'correct'
        if int(decision) != num:
            return 'incorrect'
    except ValueError:
        print "You need to input a number between 1,10!"
        return 'incorrect'
    


