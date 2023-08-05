# -*- coding: utf-8 -*-

NAME = "moye"
VERSION = "1.0"
MESSAGE = """
    -----------------------
    Greetings, this is Moye and you rock.
    -----------------------
"""

COMMANDS = (
    (
        'drop',
        'query',
        "DROP SOMETHING",
    ),
    (
        'show',
        'query',
        "SHOW STUFF",
    ),
    (
        'create',
        'query',
        "CREATE BURGERS",
    ),
    (
        'insert',
        'query',
        "INSERT OVERWRITE",
    ),
    ( 
        'test',
        '/test',
        "Test this command",
    ), 
    (
        'exam',
        '/exam',
        "Examine this command",
    ),
    (
        'myfunc',
        'moye.myfunc',
        "Run stuff locally using module defined function",
    ),
    (
        'go_moye',
        'go_moye',
        "I am ready to go",
    ),
)
