#!/usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import OptionParser

import sys
import pushscreen


def parse_options():
    parser = OptionParser(
        usage=("pushscreen <channel> <content> [options]"))
    
    parser.add_option('--type',
        help="Specify the type of push. Currently supported: url, html, clear."
    )
    
    parser.add_option('--interactive',
        action="store_true",
        help="Enable touch interaction for that push in the app."
    )
    
    parser.add_option('--scrollable',
        action="store_true",
        help="Enable scrolling for that push in the app. Requires --interactive."
    )
    
    parser.add_option('--bounces',
        action="store_true",
        help="Enable rubber-band scrolling. Requires --scrolling."
    )
    
    parser.add_option('--zoomable',
        action="store_true",
        help="Enable zoom interaction for that push in the app."
    )
    
    parser.add_option('--javascript',
        dest="javascript",
        metavar="CODE",
        help="JavaScript code to execute in the context of the web view after loading."
    )
    
    parser.add_option('--ttl',
        metavar="SECONDS",
        help="Dismiss the push after the specified number of seconds."
    )
    
    opts, args = parser.parse_args()
    return parser, opts, args



def main():
    parser, options, arguments = parse_options()
    if len(arguments) != 2:
        parser.print_help()
        return
    channel_name, content = arguments
    
    if not options.type:
        if content[0:4] == 'http':
            options.type = 'url'
        elif content.lower() == 'clear':
            options.type = 'clear'
        else:
            options.type = 'html'
    if options.type not in ['url', 'html', 'clear']:
        parser.print_help()
        return
    
    push_args = dict([(opt, getattr(options, opt)) for opt in ['interactive', 'scrollable', 'bounces', 'zoomable', 'javascript', 'ttl'] if getattr(options, opt)])
    
    if options.type == 'url':
        push_args['url'] = content
    elif options.type == 'html':
        push_args['html'] = content
    elif options.type == 'clear':
        pass # No content
    
    channel = pushscreen.Channel(channel_name)
    channel.push(options.type, **push_args)
