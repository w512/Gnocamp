# BSD LICENSE
# adapted from:
# http://code.djangoproject.com/browser/django/tags/releases/1.2.1/django/test/client.py
# http://code.djangoproject.com/browser/django/tags/releases/1.2.1/django/utils/encoding.py
# http://code.djangoproject.com/browser/django/tags/releases/1.2.1/django/utils/itercompat.py
import mimetypes
import os
import types

BOUNDARY = 'BoUnDaRyStRiNg'

def is_iterable(x):
    "A implementation independent way of checking for iterables"
    try:
        iter(x)
    except TypeError:
        return False
    else:
        return True

def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Returns a bytestring version of 's', encoded as specified in 'encoding'.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s

    if not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return ' '.join([smart_str(arg, encoding, strings_only,
                        errors) for arg in s])
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s
        
def encode_multipart(boundary, data):
    """
    Encodes multipart POST data from a dictionary of form values.

    The key will be used as the form data name; the value will be transmitted
    as content. If the value is a file, the contents of the file will be guessed or sent
    as an application/octet-stream; otherwise, str(value) will be sent.
    """
    lines = []

    # Not by any means perfect, but good enough for our purposes.
    is_file = lambda thing: hasattr(thing, "read") and callable(thing.read)

    # Each bit of the multipart form data could be either a form value or a
    # file, or a *list* of form values and/or files. Remember that HTTP field
    # names can be duplicated!
    for (key, value) in data.items():
        if is_file(value):
            lines.extend(encode_file(boundary, key, value))
        elif not isinstance(value, basestring) and is_iterable(value):
            for item in value:
                if is_file(item):
                    lines.extend(encode_file(boundary, key, item))
                else:
                    lines.extend([
                        '--' + boundary,
                        'Content-Disposition: form-data; name="%s"' % smart_str(key),
                        '',
                        smart_str(item)
                    ])
        else:
            lines.extend([
                '--' + boundary,
                'Content-Disposition: form-data; name="%s"' % smart_str(key),
                '',
                smart_str(value)
            ])

    lines.extend([
        '--' + boundary + '--',
        '',
    ])
    return '\r\n'.join(lines)

def guess_mime(filepath):
    mime, _ = mimetypes.guess_type(filepath)
    return mime or 'application/octet-stream'

def encode_file(boundary, key, file_):
    return [
        '--' + boundary,
        'Content-Disposition: form-data; name="%s"; filename="%s"' \
            % (smart_str(key), smart_str(os.path.basename(file_.name))),
        'Content-Type: %s' % guess_mime(file_.name),
        '',
        file_.read()
    ]