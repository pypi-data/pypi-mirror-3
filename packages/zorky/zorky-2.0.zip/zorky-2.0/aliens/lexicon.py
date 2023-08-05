from sys import exit

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


alt_compass = 'left down up right'.split()
compass = ['north','south','east','west']
convert = {
    'up': 'north',
    'down': 'south',
    'left': 'west',
    'right': 'east'
}

def scanner(level,words):
    
    if 'exit' in words or 'end' in words:
        print "\nThanks for playing!"
        print "\t-Luis (Developer)"
        exit(0)
    
    if words == 'cheat' or words == 'unlock':
        return 'cheat'
 
    if 'tits' in words:
        print "I like tits too."
    words = words.split()


    for word in words: #returns wall or direction
    
        if word in compass:
            
            if word in walls[level]:
                return 'wall'

            return word

        if word in alt_compass:

            if word in alt_walls[level]:

                return 'wall'

            return convert[word]


    if level == 'clue_room': #returns clue
        
        for each in 'satchel bag container purse manpurse it object thing'.split():
            
            if each in words:
                
                for every in ['pick','grab','lift','get']:
                    
                     if every in words:
                         
                         return 'clue'

    if level == 'answer_room': #returns read
        if 'read' in words:
            for each in 'it text engraving stuff wall'.split():
                if each in words:
                    return 'read'

    if level == 'laser_room': #returns laser
        
        for each in ['pick','grab','lift','get']:
        
            if each in words:
                
                for every in ['it','laser','up']:
                    
                    if every in words:
                        return 'laser'
        
    if level == 'strip_room': #returns peek
        
        for each in 'peek look check crawl duck'.split():
            
            if each in words:
                for every in 'there it tunnel tunel tunell in'.split():
                    if every in words:
                        return 'peek'
    
    if level == 'guess_room': #returns button
        
        for each in ['push','press','hit']:
            if each in words:

                if 'button' in words or 'it' in words:
                    return 'button'
                

    if level == 'farm_room': #returns kill
        for each in 'kill slay eat assassinate exterminate execute chop food annhilate'.split():
            if each in words:
                for every in 'them it all chick chickens cows animals animal cow beast thing flesh meat'.split():
                    if every in words:
                        return 'kill'

    if level == 'guard_room': #returns talk, kill, or sneak
        for each in 'talk spring approach get exit jump leave'.split(): #returns talk
            if each in words:
                for every in 'guard him it out haystack hiding spot'.split():
                    if every in words:
                        return 'talk'

        for each in 'kill assassinate butcher execute murder jump attack shoot'.split(): #returns kill
            if each in words:
                for every in 'him guard it fucker obstacle her'.split():
                    if every in words:
                        return 'kill'
        
        for each in 'sneak slip creep run'.split(): #returns sneak
            if each in words:
                for every in 'him guard past'.split():
                    if every in words:
                        return 'sneak'
    if level == 'alf_room':
        for each in 'kill assassinate execute snuff strangle murder end'.split(): # returns kill
            if each in words:
                for every in 'him alf leader alien freak shit fuck'.split():
                    if every in words:
                        return 'kill'
        
        for each in 'talk wake converse alert'.split():
            if each in words:
                for every in 'him alf leader alien fool gangster farmer it'.split():
                    if every in words:
                        return 'talk'
    if level == 'beast_room': #returns behemoth
        
        for each in 'open check pry see break move crack peek kill'.split():
            
            if each in words:
                if 'box' in words or 'it' in words or 'container' in words:
                    
                    return 'behemoth'

alt_walls = {
    'start_room': ('down','asdfasdgasdfasdfasdfasdfasdfa'),
    'laser_room': ('up','down'),
    'strip_room': ('up','down','left'),
    'clue_room': ('up','down'),
    'guess_room': ('left','right'),
    'farm_room': ('up','right'),
    'guard_room': ('up','down'),
    'alf_room': ('up','left','down'),
    'answer_room': ('up','down','right'),
    'bright_room': ('up','down')
}
    
