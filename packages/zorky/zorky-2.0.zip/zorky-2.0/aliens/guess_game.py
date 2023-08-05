from random import randint


def run():
    answer = randint(1,10)
    ai_guess = randint(1,10)
    print "The AI guessed: %d" % ai_guess
    guess = raw_input("Guess: ")
    
    try:
        guess = int(guess)
    except:
        print "You need to enter a number."
        print "Try again.\n"
        guess()
    
    
    if cmp((abs(guess)-answer),(abs(ai_guess)-answer)) == 1:
        print "Your guess was closer!"
        
        return 'win'
    
    if cmp((abs(guess)-answer),(abs(ai_guess)-answer)) == -1:
        print "The AI's guess was closer!"
        return 'lose'
    
    if cmp((abs(guess)-answer),(abs(ai_guess)-answer)) == 0:
        print "You both guessed the same digit!"
        return 'tie'
    

    
def guess():
    print "\nThe button lights up and the button pops off."
    print "A hidden screen is unveiled."
    print "The screen reads:\n"
    print "\tI'm thinking of a number between 1 and 10."
    print "\tIf your guess is closer than the AI's,"
    print "\tI will pop open the lock, and you will be able to pass.\n"
    return run()

