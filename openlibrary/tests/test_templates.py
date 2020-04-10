from web.template import Template
from tokenize import TokenError


def try_parse_template(template_text, filename=''):
    """
    :param str template_text:
    :param str filename:
    :rtype: (bool, str or Exception)
    """
    try:
        text = Template.normalize_text(template_text)
        Template(text, filename)
        return True, None
    except SyntaxError as e:
        return False, "{} - {}:{}".format(e.args[0], e.lineno, e.offset)
    except TokenError as e:
        return False, e


def test_valid_template(filename):
    with open(filename, 'r') as f:
        template_text = f.read()
    parsed, err = try_parse_template(template_text, filename)
    assert parsed, err
