import re
import itertools


TOKEN_RAW        = intern('raw')
TOKEN_TAGOPEN    = intern('tagopen')
TOKEN_TAGINVERT  = intern('taginvert')
TOKEN_TAGCLOSE   = intern('tagclose')
TOKEN_TAGCOMMENT = intern('tagcomment')
TOKEN_TAGDELIM   = intern('tagdelim')
TOKEN_TAG        = intern('tag')


def _checkprefix(tag, prefix):
    return tag[1:].strip() if tag and tag[0] == prefix else None


def _lookup(data, datum):
    for scope in data:
        #print '    lookup: ', datum, scope, ' - ', data
        if datum == '.':
            return str(scope)
        elif datum in scope:
            return scope[datum]
        elif hasattr(scope, datum):
            return getattr(scope, datum)
    return None

def render(template, data):
    return Stache().render(template, data)

class Stache(object):
    def __init__(self, otag='{{', ctag='}}'):
        self.otag = otag
        self.ctag = ctag

    def render(self, template, data={}):
        return ''.join(self.render_iter(template, data))

    def render_iter(self, template, data={}):
        return self._parse(self._tokenize(template), data)

    def _tokenize(self, template):
        rest = template

        while rest and len(rest) > 0:
            pre_section    = rest.split(self.otag, 1)
            pre, rest      = pre_section if len(pre_section) == 2 else (pre_section[0], None)
            taglabel, rest = rest.split(self.ctag, 1) if rest else (None, None)
            taglabel       = taglabel.strip() if taglabel else ''
            open_tag       = _checkprefix(taglabel, '#')
            invert_tag     = _checkprefix(taglabel, '^') if not open_tag else None
            close_tag      = _checkprefix(taglabel, '/') if not invert_tag else None
            comment_tag    = _checkprefix(taglabel, '!') if not close_tag else None
            delim_tag      = re.match('=(.*) (.*)=', taglabel) if not comment_tag else None
            delim_tag      = delim_tag.groups() if delim_tag else None

            if pre:
                yield TOKEN_RAW, pre

            if open_tag:
                yield TOKEN_TAGOPEN, open_tag
            elif invert_tag:
                yield TOKEN_TAGINVERT, invert_tag
            elif close_tag:
                yield TOKEN_TAGCLOSE, close_tag
            elif comment_tag:
                yield TOKEN_TAGCOMMENT, comment_tag
            elif delim_tag:
                yield TOKEN_TAGDELIM, delim_tag
            else:
                yield TOKEN_TAG, taglabel

    def _parse(self, tokens, *data):
        for token in tokens:
            #print '    token:' + str(token)
            tag, content = token
            if tag == TOKEN_RAW:
                yield str(content)
            elif tag == TOKEN_TAG:
                tagvalue = _lookup(data,content)
                if tagvalue is not None and tagvalue is not False:
                    yield str(tagvalue)
            elif tag == TOKEN_TAGOPEN or tag == TOKEN_TAGINVERT:
                tagvalue = _lookup(data,content)
                #print '    found data:' + str(tagvalue)
                untilclose = itertools.takewhile(lambda x: x != (TOKEN_TAGCLOSE,content), tokens)
                if (tag==TOKEN_TAGOPEN and tagvalue) or (tag==TOKEN_TAGINVERT and not tagvalue):
                    if hasattr(tagvalue, 'items'):
                        #print '    its a dict!', tagvalue, untilclose
                        for part in self._parse(untilclose, tagvalue, *data):
                            yield part
                    else:
                        try:
                            iterlist = list(iter(tagvalue))
                            if len(iterlist) == 0:
                                raise TypeError
                            #print '    its a list!', list(rest)
                            #from http://docs.python.org/library/itertools.html#itertools.tee
                            #In general, if one iterator uses most or all of the data before
                            #another iterator starts, it is faster to use list() instead of tee().
                            rest = list(untilclose)
                            for listitem in iterlist:
                                for part in self._parse(iter(rest), listitem, *data):
                                    yield part
                        except TypeError:
                            #print '    its a bool!'
                            for part in self._parse(untilclose, *data):
                                yield part
                else:
                    for ignore in untilclose:
                        pass
            elif tag == TOKEN_TAGDELIM:
                self.otag, self.ctag = content
