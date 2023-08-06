

A Python-Markdown extension that uses smartypants to provide typographically nicer ("curly") quotes, proper ("em" and "en") dashes, etc.

Installation
============

Use::

    pip install mdx_smartypants
    
Or::

    easy_install mdx_smartypants
    
(You may need to begin these with "sudo ".)

Usage
=====

To use::

    import markdown
    import mdx_smartypants
    
    md = markdown.Markdown(extensions=['smartypants'])
    
    md_text = """
        This is some Markdown. It's pretty nice, and simple. But--it could
        really use some typographic "prettification." That... That would
        be sweet. Definitely 7---8 on a '10-point scale'.
        
        Huzzah!
    """

    print md.convert(md_text)

This produces nice HTML output, including typographically "pretty" quotes and other
punctuation. It also renders HTML entites in their named rather than numeric form
for easier-on-the-eyes, more-rapidly-comprehended HTML::

    <p>This is some Markdown. It&rsquo;s pretty nice, and simple. But&mdash;it could
    really use some typographic &ldquo;prettification.&rdquo; That&hellip; That would
    be sweet. Definitely 7&ndash;8 on a &lsquo;10-point scale&rsquo;.</p>
    <p>Huzzah!</p>
    
Which renders as:

.. raw:: html

<p>This is some Markdown. It&rsquo;s pretty nice, and simple. But&mdash;it could
really use some typographic &ldquo;prettification.&rdquo; That&hellip; That would
be sweet. Definitely 7&ndash;8 on a &lsquo;10-point scale&rsquo;.</p>
<p>Huzzah!</p>