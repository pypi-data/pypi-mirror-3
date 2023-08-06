
Installation
============

::

    pip install mdx_smartypants
    
(You may need to prefix this with "sudo " to authorize installation.)

Usage
=====

::
  
    import markdown
    import mdx_smartypants
    
    text = """
    Markdown makes HTML from simple text files. But--it lacks typographic
    "prettification." That... That'd be sweet. Definitely 7---8 on a '10-point
    scale'. Now it has it.
    
    Huzzah!
    """
    
    print markdown.markdown(text, extensions=['smartypants'])

This produces nice HTML output, including typographically "pretty" quotes and
other punctuation. It also renders HTML entites in their named rather than
numeric form, which is easier on the eyes and more readily comprehended::

    <p>Markdown makes HTML from simple text files. But&mdash;it lacks
    typographic &ldquo;prettification.&rdquo; That&hellip; That&rsquo;d be
    sweet. Definitely 7&ndash;8 on a &lsquo;10-point scale&rsquo;. Now it has
    it.</p>
    <p>Huzzah!</p>

Bugs
====

The smartypants module (as of version 1.6.0.3) wrongly
munges punctuation within style sections found in the document
body.
As of version 1.0.7, mdx_smartypants monkey-patches a fix for this.