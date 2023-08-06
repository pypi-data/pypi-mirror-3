"""Namedentities workhorse for Python 2."""


from htmlentitydefs import codepoint2name, name2codepoint
import re
import codecs

def unescape(text):
    """Convert from HTML entities (named or numeric) to Unicode characters."""
    
    def fixup(m):
        """Given a matched entity, return its Unicode equivalent.  NB this maps
        existing named entities as well."""
        
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
    
    
def named_entities_codec(text):
    """Encode codec that converts Unicode characters into named entities (where
    the names are known), or failing that, numerical entities."""
    
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


codecs.register_error('named_entities', named_entities_codec)
    

def named_entities(text):
    """Given a string, convert its numerical HTML entities to named HTML
    entities. Works by converting the entire string to Unicode characters, then
    re-encoding Unicode characters into named entities (where the names are
    known), or failing that, numerical entities."""
    
    unescaped_text = unescape(text)
    return unescaped_text.encode('ascii', 'named_entities')
    
    
def encode_ampersands(text):
    """Encode ampersands into &amp;"""
    
    text = re.sub('&(?!([a-zA-Z0-9]+|#[0-9]+|#x[0-9a-fA-F]+);)', '&amp;', text)
    return text

