"""An extension to Python Markdown that uses smartypants to provide
typographically nicer ("curly") quotes, proper ("em" and "en") dashes, etc.
"""

import markdown	
from smartypants import smartyPants
from namedentities import named_entities

class SmartypantsPost(markdown.postprocessors.Postprocessor):
    
    def run(self, text):
        return named_entities(smartyPants(text))

class SmartypantsExt(markdown.extensions.Extension):
    
    def extendMarkdown(self, md, md_globals):
        md.postprocessors.add('smartypants', SmartypantsPost(md), '_end')

def makeExtension(configs=None):
    return SmartypantsExt(configs=configs)
