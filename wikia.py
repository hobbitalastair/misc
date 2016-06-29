#!/usr/bin/python
""" Wikia simplifier.

    TODO: Be more aggresive cleaning; write a stylesheet.

    Requires the python-requests package.

    Author: Alastair Hughes
    Contact: <hobbitalastair at yandex dot com>
"""

import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from html.parser import HTMLParser
import re
import time

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

def gen_handler(wiki, stale=60*60*24):
    """ Generate a handler for the given wiki """

    # We cache pages in a dict.
    # Each entry is a list: [time, content, content-type].
    cache = {}

    class WikiaHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            """ Write a stripped version of the wiki """

            def send(status, content, content_type):
                """ Send the result """
                self.send_response(status)
                self.send_header('content-type', content_type)
                self.end_headers()
                self.wfile.write(content)

            cur_time = time.time()
            if self.path in cache and cache[self.path][0] + stale > cur_time:
                # We use the cached page.
                _, content, content_type = cache[self.path]
                self.log_message("%s", "Cached: {}".format(self.path))
                send(200, content, content_type)
                return

            # Get the page.
            self.log_message("%s", "Preparing {}...".format(self.path))
            page = requests.get("http://" + wiki + self.path)

            # Prepare the response.
            if page.headers['content-type'].split(";")[0] == "text/html":
                # HTML; clean and return.
                cleaner = WikiaCleaner()
                cleaner.feed(page.text)
                out = bytes("".join(cleaner.result), page.encoding)
            else:
                # Otherwise, bail.
                out = page.content

            # Send and cache.
            send(page.status_code, out, page.headers['content-type'])
            cache[self.path] = [cur_time, out, page.headers['content-type']]

    return WikiaHandler
        

if __name__ == "__main__":
    WIKI = "xwing-miniatures.wikia.com"
    httpd = HTTPServer(("127.0.0.1", 8000), gen_handler(WIKI))
    httpd.serve_forever()
