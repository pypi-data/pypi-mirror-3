# -*- coding=utf-8 -*-
"""

"""



import consolemenu



def main():
    
    
    test_menu = menu.Menu()

    user_selection = test_menu.show( {'1':'selezione 1', '2':'selezione 2'}, 'Main menu')                        
    
    if user_selection == menu.COMMAND_EXIT:
        print 'Exit'
    else:
        print 'User has select: %s' % user_selection
    
    
    raw_input('Press any key to close...')
    
    
if __name__ == '__main__':
    main()
    
    
    
    
    
    
    