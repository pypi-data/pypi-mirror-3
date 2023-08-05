# -*- coding: utf-8 -
import readline
from authentication import authenticate
from exceptions import CommandNotFound
from sys import exit
from imp import find_module
from os import listdir
from getpass import getpass
from modules import simple_module_factory
from metadata import COMMANDS

LOGIN_RETRY_MAX = 3

class Shell(object):
    def __init__(self):
        self.module = None
        self.module_commands = None
        self.module_list = None
        self.build_module_list()
        self.parse_system_commands(COMMANDS)
        self.login()

    def message_of_service(self):
        """ Message of service """
        return """
    -----------------------------------------------------------------------
    Thanks for choosing Aliyun product. This shell environment is for you
    to interact with our public services. More details please use "help".
    -----------------------------------------------------------------------
"""

    def parse_system_commands(self, commands):
        self.system_commands = dict()

        field_list = ['name', 'function', 'description']
        for item in commands:
            command = dict(zip(field_list, item))
            self.system_commands[command['name']] = command

    def parse_module_commands(self, commands):
        self.module_commands = dict()

        field_list = ['name', 'function', 'description']
        for item in commands:
            command = dict(zip(field_list, item))
            self.module_commands[command['name']] = command

    def help(self, args):
        """ Help description """

        target = args.strip()[5:]

        if target:
            if target in self.system_commands:
                output = "\n%s\t\t%s\n" % (self.system_commands[target]['name'], self.system_commands[target]['description'])
            elif self.module_commands and target in self.module_commands:
                output = "\n%s\t\t%s\n" % (self.module_commands[target]['name'], self.module_commands[target]['description'])
            else:
                output = """
Nothing found
Please try to run 'help' for a list of all accessible topics
"""
        else:
            output = """
System Commands
------------------------------------
"""
            for key in self.system_commands:
                output += "%s\t\t%s\n" % (self.system_commands[key]['name'], self.system_commands[key]['description'])

            if self.module_commands:
                output += """
Module Commands
------------------------------------
"""
                for key in self.module_commands:
                    output += "%s\t\t%s\n" % (self.module_commands[key]['name'], self.module_commands[key]['description'])
        
        return output

    def prompt(self):
        prompt = 'aliyun'
        if self.module:
            prompt += '::%s' % (self.module.metadata.NAME)
        prompt += '> '
        return prompt

    def build_module_list(self):
        ignore, pathname, ignore = find_module('aliyun')
        self.module_list = [package
            for package in listdir('%s/modules' % (pathname))
            if not package.endswith(('.py', '.pyc', '.pyo'))
        ]

    def list(self, args):
        output = "Available modules:\n"
        output += '\n'.join(self.module_list)
        return output

    def load(self, args):
        module = args.split()[1]
        if module in self.module_list:
            self.module = simple_module_factory(module)
            self.parse_module_commands(self.module.metadata.COMMANDS)
            output = "\n%s" % (self.module.metadata.MESSAGE)
        else:
            output = "%s: does not exist" % (module)
             
        return output

    def unload(self, args):
        self.module = None
        self.module_commands = None

    def quit(self, args):
        raise EOFError()

    def exit(self, args):
        self.quit(args)

    def process_input(self, input): 
        output = ''
        items = input.split()
        command = items[0]
        # System commands always get priority
        if command in self.system_commands:
            output = getattr(self, self.system_commands[command]['function'])(input)
        elif self.module and command in self.module_commands:
            output += getattr(self.module.functions, self.module_commands[command]['function'])(input)
        else:
            raise CommandNotFound(command)

        return output

    def login(self):
        retry = 0
        while True:
            try:
                if retry >= LOGIN_RETRY_MAX:
                    print "Permission denied (login attemps have been reported)."
                    exit(1)

                username = raw_input('Username: ')
                if not username:
                    continue

                retry += 1
                password = getpass('Password: ')
                self.user = authenticate(username = username, password = password)

                if self.user is not None:
                    print self.user.get_last_login_message()
                    self.start_shell()
                else:
                    print "Permission denied, please try again."
            except KeyboardInterrupt:
                print 'Ctrl-C -- exit!\nAborted'
                exit(1)
            except EOFError:
                print "Permission denied, please try again."

    def start_shell(self):
        print self.message_of_service()
        
        while True:
            try:
                input = raw_input(self.prompt())
                if input:
                    output = self.process_input(input)
                    if output:
                        print output
                
            except CommandNotFound as e:
                print "%s: command not found" % (e.value)
                pass
            except KeyboardInterrupt:
                print 'Ctrl-C -- exit!\nAborted'
                exit(1)
            except EOFError:
                print 'Have a nice day ^____^'
                exit(0)
