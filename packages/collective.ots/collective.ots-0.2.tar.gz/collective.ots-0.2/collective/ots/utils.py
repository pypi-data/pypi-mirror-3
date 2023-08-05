# ots integrattion
import logging
try:
    import ots
    LIB_OTS = True
except ImportError:
    LIB_OTS = False

from subprocess import call
from tempfile import NamedTemporaryFile
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('collective.ots')

LANGUAGES = ['bg', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en', 'eo', 'es',
        'et', 'eu', 'fi', 'fr', 'ga', 'gl', 'he', 'hu', 'ia', 'id', 'is',
        'it', 'lv', 'mi', 'ms', 'mt', 'nl', 'nn', 'pl', 'pt', 'ro', 'ru',
        'sv', 'tl', 'tr', 'uk', 'yi']

def summarize(text, language='en', words=70):
    """ Summarize the given text in language to a maximum of words"""
    tmp = NamedTemporaryFile()
    tmp.write(text)
    tmp.flush()
    txt_len = len(text.split())
    if txt_len == 0:
        return ''
    ratio = max([int(float(words)/float(txt_len) * 100), 2])
    ratio = min(ratio, 20)
    if LIB_OTS:

        if language in LANGUAGES:
            o = ots.OTS(language)
        else:
            o = ots.OTS()
        o.parse(tmp.name, ratio)
        tmp.close()
        return o.asText()
    else:
        outfile = NamedTemporaryFile()
        args =['ots']
        args.append('--ratio=%i' % ratio)
        if language in LANGUAGES:
            args.append('--dic=%s' % language)
        args.append('--out=%s' % outfile.name)
        args.append(tmp.name)
        try:
            if call(args) == 0:
                outfile.seek(0)
                result = outfile.read()
            else:
                result =''
        except OSError:
            logger.info("OTS not found")
            result = ''
        tmp.close()
        outfile.close()
        return result

def generate_description_searchable_text(context, event):
    if hasattr(context, 'Description') and hasattr(context, 'SearchableText'):
        if context.Description() == '':
            text = context.SearchableText()
            summary = summarize(text, context.Language())
            context.setDescription(summary)


