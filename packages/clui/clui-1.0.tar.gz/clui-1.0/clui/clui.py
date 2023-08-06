#-------------------------------------------------------------------------------
# Name:        clui
# Purpose: Command Line User Interface
#
# Author:      Jose Luis Naranjo
#
# Created:     25/04/2012
# Copyright:   (c) jnaranjo 2012
# Licence:     GNU GPL3
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import re
import subprocess
from sys import platform
try:
    from colorama import Fore, Back, Style,init,deinit
    coloring = True
except ImportError:
    coloring = False

class color(object): #TODO: Move this class elsewhere
    "This class is used as backup to colorama"
    def __init__(self):
        default = ''
        self.BLACK = default
        self.RED = default
        self.GREEN = default
        self.YELLOW = default
        self.BLUE = default
        self.MAGENTA = default
        self.CYAN = default
        self.WHITE = default
        self.RESET = default
        self.DIM = default
        self.NORMAL = default
        self.BRIGHT = default
        self.RESET_ALL = default

if not coloring:
    Fore = Back = Style = color()
    init = deinit = color
    init()
        
TODO = """
Resolve dependency issues - what to do if colorama is unavailable?
UPDATE DOCUMENTATION
    Minimalistic "Hello, World clui?" (3-4 lines)

function.func_name for classes?

customize colors in colorama

recursive message?


DYNAMIC HELP COMMAND/FUNCTION

Remove colorama from requires list in setup.py?
"""


class base_clui(object):
    """This is the base class for a command line user interface.
    

You can control the style of the interface with the attributes **AND OR** parameters
provided in this class. *All are optional.* Some more than others."""

    def __init__(self,**kwargs):
        """The menu attribute is key here. All the 'add' method really does
        is add dictionaries to the options method, which are used to
        generate the :term:`clui`."""

        self.title = kwargs.pop('title', '')
        self.initial_message = kwargs.pop('initial_message', '')
        self.exit_words = kwargs.pop('exit_words', '^quit$ ^end$ ^exit$ ^leave$ ^bye$'.split())
        self.exit_message = kwargs.pop('exit_message', '')
        self.start_with_zero = kwargs.pop('start_with_zero',False)
        self.display_all_callables = kwargs.pop('display_all_callables',False)
        self.display_all_regex = kwargs.pop('display_all_regex',False)
        self.display_exit_words = kwargs.pop('display_exit_words',False)
        self.exit_callables = kwargs.pop('exit_callables',[])
        self.input_message = kwargs.pop('input_message','> ')
        self.condition = kwargs.pop('condition',True)
        self.condition_tests = kwargs.pop('condition_tests',[])
        self.buffer = kwargs.pop('buffer','')

        self.enable_clear = kwargs.pop('enable_clear',True)
        self.color = kwargs.pop('color',True) #TODO: Implement this or forget about it
        self.menu = [] #List of options for the clui to use
        self.looped = 0 #Gets a +1 for each loop. In case tracking the amount of loops is ever important.


    def __menu__(self):
        """Returns a string representation of what the menu should look like.
        

        Uses the boolean attributes for it's logic"""

        line = ''

        for option in self.menu: #List of options
            colored = Fore.MAGENTA + option['display_name'] + Fore.RESET
            line += "{index}: {display_name}".format(index=option['index'],display_name=colored)

            if option['display_callables'] or self.display_all_callables: #
            
                callables = []

                for function in option['callables']:
                    try:
                        callable_name = function.func_name #Only works for functions, unless specified attribute of a class
                    except AttributeError:
                        callable_name = str(function) #This will probably happen to classes
                    callables.append(callable_name)
                    #callables.append(str(function))
                    #line += '{callable_name}'.format(callable_name=callable_name)

                line +=  '\tCallables: ' +Fore.CYAN + str(callables)+ Fore.RESET 

            if option['display_regex'] or self.display_all_regex:
                #option['patterns'].append(option['display_name'])
                line += '\tPatterns: ' + Fore.CYAN + str(option['patterns']) + Fore.RESET
            line += "\n"

        return line

    def __call__(self,callables): #callables is a list of callables. Who would've guessed?
        buff = '-'*72
        for function in callables:
            if type(function) == int or type(function) == str or type(function) == float: #If its just a value, not a callable
                print Fore.GREEN + "\t'%s'\n" % function + Fore.RESET
            try:
                callable_name = function.func_name #Only works for functions
            except AttributeError:
                callable_name = str(function) #This will probably happen to classes
            if callable(function):
                print buff
                print Fore.GREEN + "\tEXECUTING '%s'...\n" % callable_name + Fore.RESET
                function()
                print buff

    def __chexit__(self,user_input,exit=False):
            
            for pattern in self.exit_words:# checking for exit words
                match = re.search(pattern,user_input)
                if match or exit:
                    self.condition=False
                    #to break the loop
                    self.__call__(self.exit_callables)
                    if self.exit_message:
                        print Fore.RED + Style.BRIGHT + self.exit_message + Fore.RESET + Style.RESET_ALL


    def __clear__(self):
        if platform == 'win32':
            command = 'cls'
        if platform == 'linux2' or platform == 'darwin':
            command = 'clear'
            
        subprocess.call(command)

    def add(self,**kwargs):
        """This method adds menu options to the menu.
        

        """
        callables = kwargs.pop('callables',None)
        patterns = kwargs.pop('patterns',None)
        display_name = kwargs.pop('display_name',None)
        display_callables = kwargs.pop('display_callables',False)
        display_regex = kwargs.pop('display_regex',False)

        try:
            backup_name = callables[0].func_name #The name of the first function defined in the list of callables.
        except AttributeError:
            backup_name = str(callables[0])

        if not display_name:
            display_name = backup_name

        if not patterns:
            patterns = ['^'+backup_name+'$']

        if self.start_with_zero:
            offset = 0

        if not self.start_with_zero:
            offset = 1
            
        index = len(self.menu)+offset # +1 to start menu with zero
        patterns.append('^'+str(index)+'$') # To make it regex-y


        option = {'callables':callables,
        'display_name':display_name,
        'patterns':patterns,
        'display_callables':display_callables,
        'display_regex':display_regex,
        'index':index}

        self.menu.append(option)

    def execute(self): #Playing with the idea of uesr defined while loop conditions, and callable tests for said conditions
        """Mainloop of the :term:`clui`. 
        
Only hit this after you have added all of the options for your menu.
It will enter a loop, and it will break in only three scenarios:

1) The user's input matches one of the :term:`exit words` patterns. 

2) One of the user defined :term:`condition tests` returns False

3) The user exists the terminal/shell

"""
        width = 70

        if self.title:
            #print Back.WHITE + Fore.BLACK + self.title.center(width) + Back.RESET+Fore.RESET #Title in white bg with black text
            print Style.BRIGHT + self.title.center(width) + Style.RESET_ALL #Bright text for the title!
            print '='*72+"\n"

        if self.initial_message:

            print Fore.YELLOW + self.initial_message.center(width) + Fore.RESET
            print ''

        if self.display_exit_words:
            print "Match one of the following regex patterns to escape:\n\n" + Fore.RED + str(self.exit_words) + Fore.RESET
            print ''
            
        for option in self.menu:
            display_name = option['display_name']
            option['patterns'].append('^'+display_name+'$')

        while self.condition:
            self.looped += 1

            #print '*'*72+"\n"
            print self.__menu__() #gen menu as string
            user_input = raw_input(self.input_message)
            if self.buffer: print self.buffer

            if (user_input == 'clear' or user_input == 'cls') and self.enable_clear:
                self.__clear__() #makes os call to clear the screen
                

            if self.condition_tests: #user defined tests
                for condition_test in self.condition_tests:
                    result = condition_test(user_input,self.looped)
                    try:
                        self.condition = result[0] #will work if a list or tuple is returned
                    except:
                        self.condition = result #If a string or bool is returned
                    
                    if (type(result) == list or type(result) == tuple) and len(result) > 1: #if the list is a tuple/list, and has more than one item (has a message).
                        if result[0]: color = Fore.CYAN #if true (test passed)
                        if not result[0]: color = Fore.RED# if false (test failed)
                        print color + '\n'.join(result[1:]) + Fore.RESET
                            
                    if not self.condition:
                        print Fore.RED + Style.BRIGHT + self.exit_message + Fore.RESET + Style.RESET_ALL #FIXME: This is copy and paste from the __chexit__ method.
                                                                                                         #For some reason this was double printing when I ran chexit

            print '' #Buffer line
            


            for option in self.menu: #checking menu option patterns
                for pattern in option['patterns']:
                    match = re.search(pattern,user_input)

                    if match:
                        self.__call__(option['callables'])
            
            self.__chexit__(user_input) #Check for exit words

deinit() #required for x-platform support by colorama
