#!/usr/bin/python
""" Wikia simplifier.

    TODO: Cache cleaned pages; be more aggresive cleaning; write a stylesheet.

    Requires the python-requests package.

    Author: Alastair Hughes
    Contact: <hobbitalastair at yandex dot com>
"""

import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from html.parser import HTMLParser
import re

WIKI = "xwing-miniatures.wikia.com"

class Tag:
    """ HTML tag representation """

    def __init__(self, tag, attrs):
        """ Initialise self """
        self.tag = tag
        self.attrs = {key: value for key, value in attrs}
        self.data = None # Optionally can be a list.

    def __str__(self):
        """ Return a string representation of the given tag """
        attrs = "".join((' {}="{}"'.format(key, value)
            for key, value in self.attrs.items()))
        if self.data != None:
            # We have data!
            return "<{tag}{attrs}>{data}</{tag}>\n".format(tag=self.tag, 
                    attrs=attrs,
                    data="\n".join(*self.data))
        # No data.
        return "<{tag}{attrs}/>".format(tag=self.tag, attrs=attrs)

    def __eq__(self, other):
        """ Compare, using the tag """
        return self.tag == other.tag


class WikiaCleaner(HTMLParser):
    """ Cleaner for wikia.com pages """

    # Special tags.
    WRITE = 1
    END = 1
    # Ignore fields.
    WHITELIST_ATTRS = {
            'id': ['WikiaPage'],
            'class': ('mw-headline',
                'WikiaSiteWrapper',
                'WikiaPage.*',
                'WikiaMainContent.*',
                'WikiaArticle',
                )
            }
    BLACKLIST_ATTRS = {
            'id': ['Wikia.*'],
            'class': (
                'wikia.*',
                'Wikia.*',
                'wikia-ad',
                'editsection',
                'skiplinkcontainer',
                'hidden',
                'noprint',
                'global-navigation',
                'table-cell hubs-links', # TODO: Remove this?
                'account-navigation-container',
                'search-container',
                'start-wikia-container',
                'navbackground',
                'hiddenLinks',
                'tally',
                'talk',
                'main-page-tag-rcs',
                'pollAnswerVotes',
                'edited-by',
                'printfooter',
                'global-footer',
                'ajax-poll',
                'CategorySelect',
                'activityfeed',
                ),
            }
    TAG_BLACKLIST = {'script', 'noscript', 'link', 'meta'}

    def __init__(self, *args, **kargs):
        """ Initialise self """
        super().__init__(*args, **kargs)

        # We maintain a stack of tags.
        self.stack = [self.END]
        # We record wether or not we are writing.
        self.writing = True
        # Save the result.
        self.result = []

    def write(self, form, *args, end=''):
        """ Save the result """
        if self.writing: self.result.append(form.format(*args) + end)

    def format_tag(self, tag, attrs):
        contents = [tag]
        for key, value in attrs:
            contents.append(" {}=\"{}\"".format(key, value))
        return "".join(contents)

    def ignore(self, tag, attrs):
        """ Return true if we ignore this tag """
        if tag in self.TAG_BLACKLIST: return True
        for attr_list, response in ((self.WHITELIST_ATTRS, False),
                (self.BLACKLIST_ATTRS, True)):
            for key, value in attrs:
                if key in attr_list:
                    for match in attr_list[key]:
                        for v in value.split():
                            if re.fullmatch(match, v) != None:
                                return response
        return False

    def handle_starttag(self, tag, attrs):
        """ Handle start tags """

        # Check wether to ignore the tag.
        if self.ignore(tag, attrs) and self.writing:
            self.writing = False
            self.stack.append(self.WRITE)
        self.stack.append(tag)
        self.write("<{}>", self.format_tag(tag, attrs))

    def handle_endtag(self, tag):
        """ Handle end of tags """

        # Ignore mismatched tags.
        if len(self.stack) <= 1: return
        if self.stack[-1] != tag:
            # Bother; we have some tag that was not terminated.
            if tag in self.stack:
                # The tag is in the stack; pop off, ensuring to catch
                # any WRITE markers.
                while self.stack[-1] != tag:
                    if self.stack.pop() == self.WRITE:
                        self.writing = True

        self.write("</{}>", tag, end='\n')

        # Handle the stack.
        self.stack.pop()
        if self.stack[-1] == self.WRITE:
            self.stack.pop()
            self.writing = True

    def handle_startendtag(self, tag, attrs):
        """ Handle combined start+end tags """
        if not self.ignore(tag, attrs):
            self.write("<{}/>", self.format_tag(tag, attrs))

    def handle_data(self, data):
        self.write("{}", data)


class WikiaHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        """ Write a stripped version of the wiki """

        self.log_message("%s", "Sending {}...".format(self.path))

        # Get the page.
        page = requests.get("http://" + WIKI + self.path)
        self.log_message("%s", page.headers['content-type'])

        # Send the headers.
        self.send_response(page.status_code)
        self.send_header('content-type', page.headers['content-type'])
        self.end_headers()

        if page.headers['content-type'].split(";")[0] == "text/html":
            # HTML; clean and return.
            cleaner = WikiaCleaner()
            cleaner.feed(page.text)
            self.wfile.write(bytes("".join(cleaner.result), page.encoding))
        else:
            # Otherwise, bail.
            self.wfile.write(page.content)
        

if __name__ == "__main__":
    httpd = HTTPServer(("127.0.0.1", 8000), WikiaHandler)
    httpd.serve_forever()
