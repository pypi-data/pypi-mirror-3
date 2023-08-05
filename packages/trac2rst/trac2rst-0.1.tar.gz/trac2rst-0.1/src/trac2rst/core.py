#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import sys
import optparse
import re


def wrap(text, top='', botton=''):
    text = text.strip()
    text_len = len(text.decode('utf-8'))
    if top:
        top = top * text_len + '\n'
    if botton:
        botton = '\n' + botton * text_len + '\n'
    return '%s%s%s' % (top, text, botton)

def indentation_level(line):
    lenght = len(line)
    c = 0
    while c < lenght:
        if line[c] in [' ', '\n', '\t']:
            c = c + 1
        else:
            break
    return c

def set_indentation(line, number=2):
    "Remove previous indentation, and set indentation to number"
    spaces = indentation_level(line)
    if spaces == number:
        return line
    return number * ' ' + line[spaces:]

def is_list_item(line):
    spaces = indentation_level(line)
    if spaces:
        if len(line) > spaces + 2:
            char1 = line[spaces]
            char2 = line[spaces +1 ]
            if (char1 in ['*', '-'] and char2 == ' '):
                return 'bullets'
            if  (char1.isdigit() and char2 == '.'):
                return 'numerated'
    else:
        if len(line) > 2:
            char1 = line[0]
            char2 = line[1]
            if (char1 in ['*'] and char2 == ' '):
                return 'bullets'
            if  (char1.isdigit() and char2 == '.'):
                return 'numerated'
    return False

def re_group(raw_name, raw_exp):
    return r'(?P<' + raw_name + r'>' + raw_exp + r')'


TEXT_CONTENT = r'[a-zA-Z0-9_ áéíóúAÉÍÓÚÑñ:\(\)/]+'
HEADERS = [(re.compile(r'=\s*(?P<header>' + TEXT_CONTENT + r')\s*='), '*', '*'),
           (re.compile(r'==\s*(?P<header>' + TEXT_CONTENT + r')\s*=='), '', '='),
           (re.compile(r'===\s*(?P<header>' + TEXT_CONTENT + r')\s*==='), '', '-'),
           (re.compile(r'====\s*(?P<header>' + TEXT_CONTENT + r')\s*===='), '', '+'),
          ]
INLINERS = [(re.compile(r"'''(?P<text>" + TEXT_CONTENT + r")'''"), '**'),  # '''
            (re.compile(r"''(?P<text>" + TEXT_CONTENT + r")''"), '*'),     # ''
            (re.compile(r"//(?P<text>" + TEXT_CONTENT + r")//"), '*'),    # //
           ]

# TODO: we do NOT support yet: CamelCase, http://www.edgewall.com/ [wiki:Herramientas/dvcs-autosync]
# Suported
# [http://www.google.es Enlace a google]
# [wiki:Herramientas/Kablink Una wiki]


def http_link(m, path='wiki/'):
    global options
    return options.tracurl + path + m.group(1)

def make_rest_link(text, link):
    return "`%s <%s>`_" % (text, link)

def make_link():
    pass

LINK_CONTENT = r'[a-zA-Z0-9_\-áéíóúAÉÍÓÚÑñ/:\.]+' # no space allowed
WIKI = r'wiki:"?' + re_group(r'wiki', LINK_CONTENT) + r'"?'
TICKET = r'ticket:' + re_group(r'ticket', r'\d+')
TICKET2 =  r'#' + re_group(r'ticket', r'\d+')
CHANGESET = r'\[' + re_group(r'changeset', r'\d+') + r'\]'
CHANGESET2 = r'r' + re_group(r'changeset', r'\d+')
REPORT = r'\{' + re_group(r'report', r'\d+') + r'\}'
PROCESSOR = r"\#\!.*"
PROCESSOR_RE = re.compile(PROCESSOR)

# (re, replacement)
LINKS = [
    (re.compile(r'\[' + WIKI + r'\]'), lambda m :  make_rest_link('wiki %s' % m.group(1), http_link(m, 'wiki/'))),
    (re.compile(r'\[' + TICKET + r'\]'), lambda m :  make_rest_link('ticket %s' % m.group(1), http_link(m, 'ticket/'))),
    # Resolve links
    (re.compile(r'\[' + WIKI ), lambda m : '[' + http_link(m, 'wiki/')),
    (re.compile(r'\[' + TICKET), lambda m : '[' + http_link(m, 'ticket/')),

    (re.compile(WIKI ), lambda m : make_rest_link('wiki %s' % m.group(1), http_link(m, 'wiki/'))),
    (re.compile(TICKET), lambda m : make_rest_link('ticket %s' % m.group(1), http_link(m, 'ticket/'))),
    (re.compile(TICKET2), lambda m : make_rest_link('ticket %s' % m.group(1), http_link(m, 'ticket/'))),
    (re.compile(CHANGESET), lambda m : make_rest_link('revision %s' % m.group(1), http_link(m, 'changeset/'))),
    (re.compile(CHANGESET2), lambda m : make_rest_link('revision %s' % m.group(1), http_link(m, 'changeset/'))),
    (re.compile(REPORT ), lambda m : make_rest_link('informe %s' % m.group(1), http_link(m, 'report/'))),
    (re.compile(r'\[' + # [
                re_group(r'link', LINK_CONTENT) +
                r' ' + # space
                re_group(r'text', TEXT_CONTENT) +
                r'\]' # ]
                ), "`\g<text> <\g<link>>`_"),
    (re.compile(r'\[' + # [
             re_group(r'link', LINK_CONTENT) +
             r'\]' # ]
             ), "`\g<link> <\g<link>>`_"),
]


SKIP = ['[[PageOutline]]\n']

indentation_levels = []
def process_line(line, linebefore=''):
    global indentation_levels
    result = line
    if line in SKIP:
        logging.debug('Skiping: %s' % line)
        return ''

    # Process Headers
    for exp, top, botton in HEADERS:
        match = exp.match(line)
        if match:
            result = wrap(match.group('header'), top=top, botton=botton)
            return  result

    # Process inlines
    for exp, char in INLINERS:
        repl = '%s\g<text>%s' % (char, char)
        result = exp.sub(repl, result)

    # Process links
    for re, rpl in LINKS:
        result = re.sub(rpl, result)

    # Preformatted text
    line_striped = line.strip()
    if line_striped == '{{{':
        logging.error('Preformatted text found. Please do the correct indentation')
        return '\n::\n'
    if line_striped == '}}}':
        return '\n'
    if PROCESSOR_RE.match(line_striped):
        # Delete #!python
        return ''


    # Process lists
    if is_list_item(line):
        if not is_list_item(linebefore):
            indentation_levels = [0]
            result = set_indentation(result, 0)
            result = '\n' + result
        else:
            if indentation_level(line) > indentation_level(linebefore):
                indentation_levels = indentation_levels + [3]
                result = set_indentation(result, indentation_levels[-1])
                result = '\n' + result  # nested lists
            elif indentation_level(line) < indentation_level(linebefore):
                indentation_levels = indentation_levels[:-1]
                result = set_indentation(result, indentation_levels[-1])
                result = '\n' + result  # nested lists
            else:
                result = set_indentation(result, indentation_levels[-1])
                # Same level list.
        # We use always auto-enumerated
        # In trac you can set the same number not in reST
        # 1. este cero sera un uno
        # 1. este cero sera un dos
        if is_list_item(line) == 'numerated':
            index = indentation_level(result)
            result = result[:index] + '#' + result[index+1:]
    else:
        if indentation_levels:
                indentation_levels = []


    return result


def process(input, output):
    with input:
        linebefore = ''
        for line in input:
            output.write(process_line(line, linebefore))
            linebefore = line


def main():
    usage = """
%prog [options] < trac_wiki_text > rst_text

    """
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-q', '--quiet',
                  dest='quiet',
                  help='Supress non error input',
                  default=False,
                  action='store_true')
    parser.add_option('-v', '--verbose',
                  dest='verbose',
                  help='Vebose output (debug mode)',
                  default=False,
                  action='store_true')
    parser.add_option("-i", "--input",
                  dest="input",
                  help="Intput filename",
                  metavar="FILE.txt")
    parser.add_option("-o", "--output",
                  dest="output",
                  help="Output filename",
                  metavar="FILE.rst")
    parser.add_option("-u", "--url",
                  dest="tracurl",
                  default='',
                  help="Trac url. Used for tickets, changeset and wiki links")
    global options
    (options, args) = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, stream=sys.stderr)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if options.quiet:
        logger.setLevel(logging.WARN)
    elif options.verbose:
        logger.setLevel(logging.DEBUG)

    input = sys.stdin
    if options.input:
        input = open(options.input)

    output = sys.stdout
    if options.output:
        output = open(options.output, "w")

    process(input, output)

if __name__ == '__main__':
    main()
