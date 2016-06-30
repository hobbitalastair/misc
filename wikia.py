#!/usr/bin/python
""" Wikia simplifier.

    Requires the python-requests package.

    Author: Alastair Hughes
    Contact: <hobbitalastair at yandex dot com>
"""

import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from html.parser import HTMLParser
import re
import time

# Whitelist/blacklist fields for cleaning the page.
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
            'close',
            'WikiNav',
            'toc',
            ),
        }
TAG_BLACKLIST = {'script', 'noscript', 'link', 'meta'}
DATA_BLACKLIST = {'Wikia', 'Advertisement'}


class Tag:
    """ Recursive HTML tag representation """

    def __init__(self, tag, attrs=[]):
        """ Initialise self """
        self.tag = tag
        self.attrs = {key: value for key, value in attrs}
        self.data = []  # List of associated data/children.

    def __str__(self):
        """ Return a string representation of the given tag """
        attrs = "".join((' {}="{}"'.format(key, value)
            for key, value in self.attrs.items()))
        if len(self.data) != 0:
            # We have data!
            return "<{tag}{attrs}>{data}</{tag}>\n".format(tag=self.tag, 
                    attrs=attrs,
                    data="".join((str(d) for d in self.data)))
        # No data.
        return "<{tag}{attrs}/>".format(tag=self.tag, attrs=attrs)

    def __repr__(self):
        """ Return a representation of self """
        return "<{}, {}, {}>".format(self.tag, self.attrs, self.data)

    def __eq__(self, other):
        """ Compare, using the tag """
        if type(other) == Tag:
            return self.tag == other.tag
        elif type(other) == str:
            return self.tag == other
        return False


class TagTreeGenerator(HTMLParser):
    """ Tag tree generator for HTML """

    def __init__(self, *args, **kargs):
        """ Initialise self """
        super().__init__(*args, **kargs)
        self.stack = []

    def handle_starttag(self, tag, attrs):
        """ Handle start tags """
        self.stack.append(Tag(tag, attrs))

    def handle_endtag(self, tag):
        """ Handle end of tags """

        # Find all children of this tag.
        if self.stack[-1].tag != tag and tag in self.stack:
            # The unterminated tag is in the stack; assume that "higher" tags
            # are it's children.
            children = []
            while self.stack[-1].tag != tag: children.append(self.stack.pop())
            self.stack[-1].data += reversed(children)

    def handle_startendtag(self, tag, attrs):
        """ Handle combined start+end tags """
        self.stack.append(Tag(tag, attrs))

    def handle_data(self, data):
        """ Save the data encountered """
        stripped = data.strip("\t\n")
        if len(self.stack) > 0 and len(stripped) != 0:
            self.stack[-1].data.append(stripped)


def ignore(tag):
    """ Return true if we ignore this tag """
    if tag.tag in TAG_BLACKLIST: return True
    for d in tag.data:
        if type(d) == str and d in DATA_BLACKLIST:
            return True
    for attr_list, response in ((WHITELIST_ATTRS, False),
            (BLACKLIST_ATTRS, True)):
        for key, value in tag.attrs.items():
            if key in attr_list:
                for match in attr_list[key]:
                    for v in value.split():
                        if re.fullmatch(match, v) != None:
                            return response
    return False


def clean(tag):
    """ Clean the given page, assumed to be in tree form.
        This assumes that all Wikia pages follow approximately the same form...
    """

    children = []
    for child in tag.data:
        if type(child) == Tag:
            if ignore(child): continue # Ignore children.
            # Recurse.
            child = clean(child)
            # Check if we bail.
            if child is None: break
            if 'Forum Activity' in child.data: return None

            # Ignore empty tags.
            if child.tag in {'div', 'p'} and len(child.data) == 0:
                continue
            # Make images load the image directly.
            if child.tag == "img" and 'data-src' in child.attrs:
                child.attrs['src'] = child.attrs['data-src']
        children.append(child)
    tag.data = children
    return tag


def gen_handler(wiki, stale=60*60*24):
    """ Generate a handler for the given wiki.
        By default, content is considered stale after 24 hours; 'stale' is
        given in seconds.
    """

    # We cache pages in a dict.
    # Each entry is a list: [time, content, content-type].
    cache = {}

    class WikiaHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            """ Get a stripped version of the wikia page """

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
                # HTML; parse, clean and return.
                html = TagTreeGenerator()
                html.feed(page.text)
                if len(html.stack) > 0:
                    tree = clean(html.stack[-1])
                    out = bytes(str(tree), page.encoding)
                else:
                    # Invalid HTML?
                    self.log_error("Invalid HTML for page '%s'", self.path)
                    out = bytes(page.text, page.encoding)
            else:
                # Otherwise, bail.
                out = page.content

            # Send and cache.
            send(page.status_code, out, page.headers['content-type'])
            cache[self.path] = [cur_time, out, page.headers['content-type']]

    return WikiaHandler
        

if __name__ == "__main__":
    # Run a server.

    # Parse the arguments.
    import sys
    usage = "{}: [--ip <ip>] [--port <port>] <wiki>".format(sys.argv[0])
    WIKI = None
    IP = "127.0.0.1"
    PORT = 8000
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ('-h', '--help'):
            print(usage)
            exit(0)
        elif arg in ('--ip', '--port'):
            if len(sys.argv) > i + 1:
                i += 2
                if arg[2:] == 'ip':
                    IP = sys.argv[i + 1]
                elif arg[2:] == 'port':
                    try:
                        PORT = int(sys.argv[i + 1])
                    except ValueError:
                        print("Expected an int for the port, got {}".format( \
                                sys.argv[i + 1]))
            else:
                print(usage)
                print("Argument '{}' not followed by a value".format(arg))
                exit(1)
        elif WIKI == None:
            WIKI = arg
            i += 1
        else:
            print(usage)
            print("Unknown argument '{}'!".format(arg))
            exit(2)
    if WIKI == None:
        print(usage)
        print("No wiki given!")
        exit(3)

    # Start the server.
    httpd = HTTPServer((IP, PORT), gen_handler(WIKI))
    httpd.serve_forever()
