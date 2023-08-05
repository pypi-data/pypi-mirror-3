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
        'insert',
        'query',
        """
Syntax:
SELECT
    [ALL | DISTINCT | DISTINCTROW ]
      [HIGH_PRIORITY]
      [STRAIGHT_JOIN]
      [SQL_SMALL_RESULT] [SQL_BIG_RESULT] [SQL_BUFFER_RESULT]
      [SQL_CACHE | SQL_NO_CACHE] [SQL_CALC_FOUND_ROWS]
    select_expr [, select_expr ...]
    [FROM table_references
    [WHERE where_condition]
    [GROUP BY {col_name | expr | position}
      [ASC | DESC], ... [WITH ROLLUP]]
    [HAVING where_condition]
    [ORDER BY {col_name | expr | position}
      [ASC | DESC], ...]
    [LIMIT {[offset,] row_count | row_count OFFSET offset}]
    [PROCEDURE procedure_name(argument_list)]
    [INTO OUTFILE 'file_name'
        [CHARACTER SET charset_name]
        export_options
      | INTO DUMPFILE 'file_name'
      | INTO var_name [, var_name]]
    [FOR UPDATE | LOCK IN SHARE MODE]]

SELECT is used to retrieve rows selected from one or more tables, and
can include UNION statements and subqueries. See [HELP UNION], and
http://dev.mysql.com/doc/refman/5.1/en/subqueries.html.
""",
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
