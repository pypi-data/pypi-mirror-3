# Copyright (c) 2011-2012, 30loops.net
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of 30loops.net nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL 30loops.net BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""Utility functions for the thirty command line tool."""

import sys
import json
import platform

from collections import OrderedDict
from libthirty import documents
from libthirty.logbook import LogBookHandler

# Decorator for cli-args
def arg(*args, **kwargs):
    def _decorator(func):
        # Because of the sematics of decorator composition if we just append
        # to the options list positional options will appear to be backwards.
        func.__dict__.setdefault('arguments', []).insert(0, (args, kwargs))
        return func
    return _decorator


def occurence(string):
    if string.lower() in 'all':
        occurence = 'all'
    else:
        try:
            occurence = int(string)
        except ValueError:
            sys.stderr.write('Occurence needs to be either a number or all.')
            sys.exit(1)

    return occurence


def colorize(msg, color):
    if color in "green":
        colorcode = 32
    elif color in "red":
        colorcode = 31
    else:
        colorcode = 30

    if platform.system() in 'Windows':
        return msg
    else:
        return '\033[%sm%s\033[0m' % (colorcode, msg)


def format_logbook_message(msg):
    if msg['loglevel'] == 1:
        # normal message
        if sys.stdout.isatty:
            if msg['message'][:1].isupper():
                    formatted_message = colorize('\n--> %s' % msg['message'], "green")
            else:
                formatted_message = colorize(msg['message'], "green")
        else:
            formatted_message = "Info (%s): %s" % (
                msg['asctime'], msg['message'])
    if msg['loglevel'] == 3:
        # we catch an error
        if sys.stderr.isatty:
            formatted_message = colorize('\n%s' % msg['message'], "red")
        else:
            formatted_message = "Error (%s): %s" % (
                msg['asctime'], msg['message'])

    return formatted_message

def _poll_logbook(uuid):
    import time

    lbh = LogBookHandler(uuid)
    firstrun = True
    while True:
        messages = lbh.fetch()
        for msg in messages:
            if msg['loglevel'] == 1:
                sys.stdout.write(format_logbook_message(msg))
            elif msg['loglevel'] == 3:
                sys.stderr.write(format_logbook_message(msg))
        if lbh.status in 'finished':
            sys.stdout.write('\n')
            break
        if lbh.status in 'error':
            sys.stderr.write('\n')
            break
        if not firstrun:
            sys.stdout.write(colorize(".", "green"))
            sys.stdout.flush()
        firstrun = False
        time.sleep(2)

def _format_output(obj):
    return json.dumps(obj, indent=4)

def _format_logoutput(obj):
    output = []
    for message in obj['messages']:
        item = "[%s]%s\n" % (message['timestamp'], message['message'])
        if message['severity'] in "Error":
            output.append(colorize(item, "red"))
        else:
            output.append(colorize(item, "green"))

    output = ''.join(output)
    return output

def _format_error(error):
    return json.dumps(error, indent=4)

def _get_document(label):
    try:
        Document = getattr(documents, label)
    except AttributeError:
        sys.stderr.write("Unknown resource label.")
        sys.stderr.flush()

    return Document

class OutputFormatter(object):
    def info(self, msg):
        msg = self._format_info(msg)
        sys.stdout.write(colorize(msg, "green"))
        sys.stdout.flush()

    def error(self, msg):
        msg = self._format_error(msg)
        sys.stderr.write(colorize(msg, "red"))
        sys.stderr.flush()

    def debug(self, msg):
        msg = self._format_debug(msg)
        sys.stdout.write(colorize(msg, "gray"))
        sys.stdout.flush()


class ResourceOutputFormatter(OutputFormatter):
    def _format_info(self, msg):
        if isinstance(msg, dict):
            obj = self._format_resource(msg)
            return self._dict_to_string(obj)
        else:
            return "%s\n" % msg

    def _format_resource(self, msg):
        header_fields = ['name', 'variant', 'label', 'flavor']

        # We wanna output the different fields in a certain order:
        #  1) the header fields
        #  2) normal fields
        #  3) relations (dicts)
        #  4) collections (lists)
        output = OrderedDict()
        relations = OrderedDict()
        collections = OrderedDict()

        # Filter out the header fields of this resource, if available
        for field in header_fields:
            if field in msg:
                output[field] = msg[field]
                del(msg[field])

        for k, v in msg.iteritems():
            if isinstance(v, dict):
                # related resources
                relations[k] = self._format_resource(v)
            elif isinstance(v, list):
                # collections
                if len(v) < 1:
                    # We don't wanna output empty collections
                    continue
                collections[k] = []
                for item in v:
                    collections[k].append(self._format_resource(item))
            else:
                output[k] = v
        if len(collections) >= 1:
            relations.update(collections)
        if len(relations) >= 1:
            output.update(relations)

        # OrderedDict can't update if the dict is empty. Thats why the
        # following line doesn work
        #output.update(relations.update(collections))
        if len(collections) >= 1:
            relations.update(collections)
        if len(relations) >= 1:
            output.update(relations)

        return output

    def _format_error(self, msg):
        return self._format_info(msg['error'])

    def _format_debug(self, msg):
        return self._format_info(msg)

    def _dict_to_string(self, obj, depth=0, bullet=False):
        output = ""
        wedge = "    "

        for k, v in obj.iteritems():
            if isinstance(v, OrderedDict):
                output += "%s%s\n" % (wedge*depth, k)
                output += self._dict_to_string(v, depth+1)
            elif isinstance(v, list):
                output += "%s%s\n" % (wedge*depth, k)
                for item in v:
                    output += self._dict_to_string(item, depth+1, bullet=True)
            else:
                spacing = wedge * depth
                # We check here if we should add a bullet point
                if bullet and len(spacing) > 0 and k in 'name':
                    spacing = bytearray(spacing)
                    spacing[-3] = '-'
                    spacing[-2] = '-'
                    bullet = False
                    spacing = str(spacing)
                output += "%s%s: %s\n" % (spacing, k, v)

        return output


class RawOutputFormatter(OutputFormatter):
    def _format_info(self, msg):
        return json.dumps(msg)

    def _format_error(self, msg):
        return self._format_info(msg)

    def _format_debug(self, msg):
        return self._format_info(msg)

