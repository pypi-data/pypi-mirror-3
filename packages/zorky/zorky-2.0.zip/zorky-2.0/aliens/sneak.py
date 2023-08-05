from random import randint

def sneak():
    correct = randint(1,3)
    guess = randint(1,3)
    #print "\nCorrect: %d" % correct
    #print "\nGuess: %d" % guess
    if guess != correct:
        return 'fail'
    if guess == correct:
        return 'succeed'
sneak()