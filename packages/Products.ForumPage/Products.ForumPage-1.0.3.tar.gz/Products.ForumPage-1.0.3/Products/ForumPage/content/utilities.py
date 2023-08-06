import formatter, htmllib, cStringIO

# Maybe submit this to Plone/CMF

class MyAbstractFormatter(formatter.AbstractFormatter):

    def add_line_break(self):
        if not (self.hard_break or self.para_end):
            self.writer.send_line_break()
            self.have_label = self.parskip = 0
        self.nospace = 1
        self.softspace = 0

def render_html_as_text(text, size=None, format_newlines_as_html=False, strip_whitespace=True):
    file = cStringIO.StringIO()
    text = unescape(text)
    text = text.encode('utf-8')
    parser = htmllib.HTMLParser(MyAbstractFormatter(
        formatter.DumbWriter(file=file)))
    parser.feed(text)
    parser.close()
    data = file.getvalue()
    data = data.decode('utf-8')
    data = (len(data) < (size + 3) and data) or (data[:size] + '...')
    if format_newlines_as_html:
        if strip_whitespace:
            data = data.strip()
        data = data.replace('\r\n', '<br />').replace('\n', '<br />').replace('\r', '<br />')
    return data
# Following code is Copyright

copyright_unscape = """
    Copyright 1995-2009 by Fredrik Lundh

    By obtaining, using, and/or copying this software and/or its
    associated documentation, you agree that you have read,
    understood, and will comply with the following terms and
    conditions:

    Permission to use, copy, modify, and distribute this software and
    its associated documentation for any purpose and without fee is
    hereby granted, provided that the above copyright notice appears
    in all copies, and that both that copyright notice and this
    permission notice appear in supporting documentation, and that the
    name of Secret Labs AB or the author not be used in advertising or
    publicity pertaining to distribution of the software without
    specific, written prior permission.

    SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD
    TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL SECRET LABS AB OR
    THE AUTHOR BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL
    DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA
    OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
    TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
    PERFORMANCE OF THIS SOFTWARE.

"""

import re, htmlentitydefs

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

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
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

