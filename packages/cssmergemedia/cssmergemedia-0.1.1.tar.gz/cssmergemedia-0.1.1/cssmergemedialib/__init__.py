#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012 Adrien Kohlbecker
# Permission is hereby granted, free of
# charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom
# the Software is furnished to do so, subject to the following
# conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import optparse

import meta
import cssutils
import codecs

import logging

log = logging.getLogger()
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
log.addHandler(ch)
ch_fmt = logging.Formatter("%(levelname)s\t: %(message)s")
ch.setFormatter(ch_fmt)


def merge_media_queries(css_string, fout):

    media_rules = {}
    log.info('Parsing CSS string...')
    css = cssutils.parseString(css_string)
    log.info('Finished parsing. Now merging @media queries...')

    for rule in css.cssRules:
        if type(rule).__name__ == 'CSSMediaRule':
            try:
                combined_rule = media_rules[rule.media.mediaText]
                for child_rule in rule.cssRules:
                    combined_rule.add(child_rule)
            except KeyError:
                media_rules[rule.media.mediaText] = rule
                log.info("New @media query: %s" % rule.media.mediaText)

        else:
            if rule.cssText == None:
                continue
            fout.write(rule.cssText)
            fout.write('\n')

    for index in media_rules:
        fout.write(media_rules[index].cssText)
        fout.write('\n')

    log.info('Finished merging.')


def main(prog_args):

    parser = optparse.OptionParser(version=meta.__version__)

    parser.add_option('-i', '--input', action="store", type="string", dest="input", help="The CSS file you want to parse", metavar="FILE")
    parser.add_option('-o', '--output', action="store", type="string", dest="output", help="Where to write the output", metavar="FILE")
    parser.add_option('-q', '--quiet', action="store_false", dest="verbose", default=True, help="Don't print status messages to stdout")
    opt, args = parser.parse_args(prog_args)

    if not opt.input or not opt.output:
        log.error('Invalid arguments, see --help')
        sys.exit(1)

    if not opt.verbose:
        cssutils.log.setLevel(logging.FATAL)
        log.setLevel(logging.ERROR)

    fin = sys.stdin
    if opt.input:
        fin = codecs.open(opt.input, 'rb')
    css_string = fin.read()

    fout = sys.stdout
    if opt.output:
        fout = codecs.open(opt.output, 'w+b', 'utf-8')

    merge_media_queries(css_string, fout)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
