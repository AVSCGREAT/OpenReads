from openlibrary.catalog.marc.fast_parse import get_all_tag_lines, translate, split_line
import re

trans = {'&':'&amp;','<':'&lt;','>':'&gt;','\n':'<br>', '\x1b': '<b>[esc]</b>'}
re_html_replace = re.compile('([&<>\n\x1b])')

def esc(s):
    return re_html_replace.sub(lambda m: trans[m.group(1)], s)

def esc_sp(s):
    return esc(s).replace(' ', '&nbsp;')

class html_record():
    def __init__(self, data):
        """
        >>> hr = html_record("00053This is the leader.Now we are beyond the leader.")
        >>> hr.leader
        '00053This is the leader.'
        >>> hr.is_marc8
        True
        >>> # Change "00053" to "00054"...
        >>> hr = html_record("00054This is the leader.Now we are beyond the leader.")
        Traceback (most recent call last):
        ...
        AssertionError
        >>> # Change " " to "a"...
        >>> hr = html_record("00053Thisais the leader.Now we are beyond the leader.")
        >>> hr.is_marc8
        False
        """
        assert len(data) == int(data[:5])
        self.data = data
        self.leader = data[:24]
        self.is_marc8 = data[9] != 'a'

    def html(self):
        return '<br>\n'.join(self.html_line(t, l) for t, l in get_all_tag_lines(self.data))

    def html_subfields(self, line):
        assert line[-1] == '\x1e'
        encode = {
            'k': lambda s: '<b>$%s</b>' % esc(translate(s, self.is_marc8)),
            'v': lambda s: esc(translate(s, self.is_marc8)),
        }
        return ''.join(encode[k](v) for k, v in split_line(line[2:-1]))

    def html_line(self, tag, line):
        if tag.startswith('00'):
            s = esc_sp(line[:-1])
        else:
            s = esc_sp(line[0:2]) + ' ' + self.html_subfields(line)
        return u'<large>' + tag + u'</large> <code>' + s + u'</code>'

def test_html_subfields():
    """
    >>> test_html_subfields()
    """
    samples = [
        ('  \x1fa0123456789\x1e', '<b>$a</b>0123456789'),
        ('  end of wrapped\x1e', 'end of wrapped'),
        ('  \x1fa<whatever>\x1e', '<b>$a</b>&lt;whatever&gt;'),
    ]
    hr = html_record("00053This is the leader.Now we are beyond the leader.")
    for input, output in samples:
        assert hr.html_subfields(input) == output

def test_html_line():
    """
    >>> test_html_line()
    """
    samples = [
        ('020', '  \x1fa0123456789\x1e', '&nbsp;&nbsp; <b>$a</b>0123456789'),
        ('520', '  end of wrapped\x1e', '&nbsp;&nbsp; end of wrapped'),
        ('245', '10\x1faDbu ma la \xca\xbejug pa\xca\xbei kar t\xcc\xa3i\xcc\x84k :\x1fbDwags-brgyud grub pa\xca\xbei s\xcc\x81in\xcc\x87 rta /\x1fcKarma-pa Mi-bskyod-rdo-rje.\x1e', u'10 <b>$a</b>Dbu ma la \u02bejug pa\u02bei kar \u1e6d\u012bk :<b>$b</b>Dwags-brgyud grub pa\u02bei \u015bi\u1e45 rta /<b>$c</b>Karma-pa Mi-bskyod-rdo-rje.'),
    ]
    hr = html_record("00053This is the leader.Now we are beyond the leader.")
    for tag, input, output in samples:
        expect = '<large>%s</large> <code>%s</code>' % (tag, output)
        assert hr.html_line(tag, input) == expect


if __name__ == '__main__':
    import doctest

    doctest.testmod()
