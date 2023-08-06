"""An extension to Python Markdown that uses smartypants to provide
typographically nicer ("curly") quotes, proper ("em" and "en") dashes, etc.

USAGE:

import 
"""

from markdown.postprocessors import Postprocessor
from markdown.extensions import Extension

from smartypants import smartyPants


# NAMED ENTITIES CODE

# Most of the heavy-lifting is done by the smartypants module, but named HTML
# entities are much easier to comprehend than numeric entities, so while we're
# making the output typograpically prettier and more readable, let's take a
# little extra time to make the HTML prettier and more readable as well

import codecs
from htmlentitydefs import codepoint2name, name2codepoint
import re

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)
    
def named_entities(text):
    if isinstance(text, (UnicodeEncodeError, UnicodeTranslateError)):
        s = []
        for c in text.object[text.start:text.end]:

            if ord(c) in codepoint2name:
                s.append(u'&%s;' % codepoint2name[ord(c)])
            else:
                s.append(u'&#%s;' % ord(c))
        return ''.join(s), text.end
    else:
        raise TypeError("Can't handle %s" % text.__name__)
        
codecs.register_error('named_entities', named_entities)

def named_entities(text):
    unescaped_text = unescape(text)
    return unescaped_text.encode('ascii', 'named_entities')


# EXTENSION CODE

# The following two classes and one module-level function link smartyPants and
# named_entities into usable form via markdown's extension API.

class SmartypantsPost(Postprocessor):
    
    def run(self, text):
        return named_entities(smartyPants(text))

class SmartypantsExt(Extension):
    
    def extendMarkdown(self, md, md_globals):
        md.postprocessors.add('smartypants', SmartypantsPost(md), '_end')


def makeExtension(configs=None):
    return SmartypantsExt(configs=configs)