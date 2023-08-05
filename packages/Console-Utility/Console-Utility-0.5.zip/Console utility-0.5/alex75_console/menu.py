# -*- coding: utf-8 -*-

"""
"""

import os



MAX_COMMAND_KEY_LEN = 5
MENU_COMMAND_TEMPLATE = '%5s -> %s'
COMMAND_EXIT = 'E'



#define Exceptions
class MenuError(Exception): pass
class MissingVoicesError(MenuError): pass
class DuplicateKeyError(MenuError): pass


def clear_console():
    try:
        # Windows
        os.system('cls')
    except:
        try:
        # basch (Linux and Mac)
            os.system('clear')
        except:
            pass


class Menu():
    """"""
    def __init__(self):
        pass

    def __str__(self):
        return "Menu class"


    def add_voice(self, key, text):
        #create dictionary if it is not also created
        if not hasattr(self, 'voices'):
            self.voices = {}
        
        #check if key also exists
        if self.voices.has_key(key):
            raise DuplicateKeyError, 'The key "%s" is already present' % key
        
        #check if key also exists (case-insensitive)
        for k in self.voices.iterkeys():
            if k.lower() == key.lower():
                raise DuplicateKeyError, 'The key "%s" is already present (keys names are case-insensitive)' % key
        
        self.voices[key] = text

    def show(self, voices=None, title=None, prompt=None, show_exit=True):
        """Show the menu with the given voices. 
        param @title = Show the title if given. 
        param @prompt = Show a default text to invite user to make a selection
        param @show_exit = Show "Exit" command if requested.
        Return the user selection
        """
        
        if not voices and not hasattr(self, 'voices'):
            error = 'No voices defined for menu'
            raise MissingVoicesError, error
            
        #use pre-assigned voices
        if not voices:
            voices = self.voices           
            
        else:
            #check if voices is a dictionary
            if not isinstance(voices, dict):
                raise ValueError, 'voices must be a dictionary'
                
            #check duplicate keys in passed dictionary (if key exists in lower and upper case)
            for k in voices.iterkeys():
                k_lower = k.lower()
                k_upper = k.upper()
            
                if k_lower != k_upper:
                    if voices.has_key(k_lower) and voices.has_key(k_upper):
                        raise DuplicateKeyError, 'The key "%s" is already present (keys names are case-insensitive)' % k
                

        # check that voice keys are all string (else cannot compare user input) 
        for key in voices.iterkeys():
            # old code: type(key) != str
            if not isinstance(key, str) or len(key) > MAX_COMMAND_KEY_LEN:
                error = "All keys must be strings with max length of %i chars." % MAX_COMMAND_KEY_LEN
                raise TypeError, error

        # check if voices contains "Exit" command and "Exit" command is required.
        if show_exit and voices.has_key(COMMAND_EXIT):
            error = 'Voice items cannot contain "Exit" command key (%s).' % COMMAND_EXIT
            raise ValueError, error

        # set a default prompt if not passed
        if not prompt:
            prompt = 'Make a selection: '


        retry_message = None  # message to explain cause that make selection not valid
        while True:
            #ref: http://stackoverflow.com/questions/2726343/how-to-create-ascii-animation-in-a-console-application-using-python-3-x

            error = None
            clear_console()
            menu_width = 30
            if title:
                
                #calculate left and right spaces
                left_spaces = ((menu_width-len(title))/2)
                pad_left = ' ' * left_spaces
                pad_right = ' ' * (menu_width-len(title)-left_spaces)            
                
                print '''\
--------------------------------
|%(pad_left)s%(title)s%(pad_right)s|
--------------------------------
                ''' % {'title':title, 'pad_left':pad_left, 'pad_right':pad_right}
    
            for command, description in voices.items():
                print MENU_COMMAND_TEMPLATE % (command, description)
                
            print MENU_COMMAND_TEMPLATE % (COMMAND_EXIT, "Exit")
    
            if retry_message:
                print retry_message
                
            selected_voice = raw_input(prompt)
    

            #if not voices.has_key(selected_voice):
            #	error = "Invalid value, retry..."		
            # make a case insensitive search of the key	
            found = False   
            for key in voices.iterkeys():
                if key.lower() == selected_voice.lower():
                    selected_voice = key
                    found = True
                    break 
    
            if not found:                
                error = "Invalid value, retry..."
                retry_message = "Value '%s' is not in the list." % selected_voice


            if not error:	
                self.last_selection = selected_voice 
                # return selected value
                return selected_voice
 
