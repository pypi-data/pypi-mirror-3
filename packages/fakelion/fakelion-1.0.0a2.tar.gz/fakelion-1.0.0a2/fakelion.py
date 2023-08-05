#! /usr/bin/env python
"""Simplistic script to pseudo-localize a .po file into a .pot file

Steps:
    * mark up your django app with the built-in i18n support
    * create your app's locale subdirectory
    * create a .po file (in this case for French)
    
        django-admin.py makemessages -l fr
    
    * run the pseudo-localizer over the fr translation file 
    
        python -m fakelion locale/fr/LC_MESSAGES/django.po
        django-admin.py compilemessages
    
    * add the language to the set of languages supported in your project's settings.py
    
        LANGUAGES = (
            ('en', _('English')),
            ('fr', _('French Canadian')),
        )
    
    * add the localization middleware to your project (again, settings.py) 
    
        django.middleware.locale.LocaleMiddleware

    * restart your django server
    * set your browser to use the language (French) as default
    * view your site/app, look for any text strings which are not converted, mark for translation, iterate
"""
__version__ = '1.0.0a2'
import polib 
import re, sys, logging, optparse
from gettext import gettext as _
log = logging.getLogger( 'fakel10n' )

RE_FLAGS = re.I|re.U|re.VERBOSE

HTML_ENTITIES = re.compile(
    r"""(?:
            # HTML character entities
            [&][-a-zA-Z0-9]+[;]
        )""",
    RE_FLAGS,
)
HTML_TAGS = re.compile(
    r"""(?:
        # HTML tags (or, rather, a simplified model of them, just for basic non-minimized markup)
        [<][/]?
            [^>]*
        [>]
    )""",
    RE_FLAGS,
)
PYTHON_STRING_FORMAT = re.compile(
    r"""(?:
        # Python % string formatting...
        [%] 
            (?: [(] [^)]+ [)] )? # optionally with a named variable
            [-#0 +]* # optionally with conversion flags 
            [0-9]* # optionally with length modifier 
        [diouxXeEfFgGcrs] # one of the format characters...
    )""",
    RE_FLAGS,
)
LINES = re.compile(
    r"""(?:
        # lines can't be shuffled or po compiler gets angry...
        [\r\n\t]+
    )""",
    RE_FLAGS,
)
# TODO: common english sentence/meaning boundaries (". ", "(", ")", etc)

DEFAULT_MARKUP = [
    LINES,
    PYTHON_STRING_FORMAT,
    HTML_ENTITIES,
    HTML_TAGS,
]
def reverse( x ):
    return x[::-1]

a_to_z = u"".join([unicode(chr(x)) for x in range( 97, 123 )])
a_to_z_upper = u"".join([unicode(chr(x)) for x in range( 65, 91 )])
fw_a_to_z = u"".join([unichr(x) for x in range( 0xff41, 0xff41+26 )])
fw_a_to_z_upper = u"".join([unichr(x) for x in range( 0xff21, 0xff21+26 )])

_fullwidth_map = dict(zip(a_to_z+a_to_z_upper, fw_a_to_z+fw_a_to_z_upper))
def fullwidth( x ):
    return u"".join([ _fullwidth_map.get(c,c) for c in x])

DEFAULT_TRANSFORMS = [
    reverse,
    fullwidth,
]

class Transform( object ):
    """Class which performs substitution on strings-to-translate"""
    def __init__( self, transforms=None, markup=None ):
        """Initialize the transformation mechanism"""
        self.markup = markup or DEFAULT_MARKUP
        self.transforms = transforms or DEFAULT_TRANSFORMS
    def __call__( self, message ):
        """Transform message
        
        returns transformed message"""
        marked_up = self.split( message )
        result = []
        for (text,markup) in marked_up:
            text = self.transform( text )
            result.append( text )
            result.append( markup )
        return "".join( result )
        
    def split( self, message ):
        result = [(message,'')]
        for finder in self.markup:
            new = []
            for (text,markup) in result:
                new.extend( find_markup( text, finder ) )
                if markup:
                    if new:
                        new[-1][1] += markup 
                    else:
                        new.append( ['',markup] )
            result = new 
        return result 
    def transform( self, text ):
        for transform in self.transforms:
            text = transform( text )
        return text

def find_markup( message, markup_re ):
    """Convert message to list of [text, subs, text, subs,...,text]"""
    current = 0
    result = []
    for match in markup_re.finditer( message ):
        result.append( [message[current:match.start()], match.group(0)] )
        current = match.end()
    if message[current:]:
        result.append( [message[current:], ''] )
    return result 

def fake_l10n(source, transform, fuzzy=False):
    log.info( 'Translating: %s', source )
    po = polib.pofile(source)
    for entry in po:
        if not fuzzy and 'fuzzy' in entry.flags:
            entry.flags.remove( 'fuzzy' )
        entry.msgstr = transform( entry.msgid )
    po.save( source )

def parse( ):
    parser = optparse.OptionParser()
    parser.add_option( 
        '-H','--no-html', dest="html", default=True, action="store_false",
        help = _("Do not consider HTML entities or tags to be markup"),
    )
    parser.add_option( 
        '-P','--no-python', dest="python", default=True, action="store_false",
        help = _("Do not consider Python string-formatting sequences to be markup"),
    )

    parser.add_option( 
        '-R','--no-reverse', dest="reverse", action="store_false",default=True,
        help = _("Do not reverse message string text"),
    )
    parser.add_option( 
        '-f','--fullwidth', dest="fullwidth", action="store_true", default=False,
        help = _("Transform a-z and A-Z into full-width unicode character equivalents"),
    )
    parser.add_option(
        '-F','--fuzzy', dest='fuzzy',action="store_true", default=False,
        help = _("Allow 'fuzzy' declarations, which generally do not work well with Django"),
    )

    options,args = parser.parse_args()
    if not args:
        parser.error( _("Require a .po file to process"))
    return options, args

def main():
    """Run pseudo-localization on the command-line parameters"""
    options,args = parse()
    markup = [ LINES ]
    if options.python:
        markup.extend( [HTML_ENTITIES,HTML_TAGS])
    if options.html:
        markup.extend( [PYTHON_STRING_FORMAT] )
    transforms = []
    if options.reverse:
        transforms.append( reverse )
    if options.fullwidth:
        transforms.append( fullwidth )

    transformation = Transform( 
        transforms = transforms,
        markup = markup,
    )
    for arg in args:
        fake_l10n( arg, transformation, options.fuzzy )

if __name__ == "__main__":
    logging.basicConfig( level = logging.INFO )
    main()
