# -*- coding=utf-8 -*-
"""

"""



from alex_console import menu
from alex_console import selectors



def main():
    
    
    test_menu = menu.Menu()
    test_menu.add_voice('A', 'Chose A')
    test_menu.add_voice('B', 'Chose B')
    test_menu.add_voice('C', 'Chose C')
    
    user_selection = test_menu.show()                        
    
    if user_selection == menu.COMMAND_EXIT:
        print 'Exit'
    else:
        print 'User has select: %s' % user_selection
    
    
    raw_input('Press any key to close...')
    
    
if __name__ == '__main__':
    main()
    
    
    
    
    
    
    