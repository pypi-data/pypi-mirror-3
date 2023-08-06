from collections import namedtuple

_text = namedtuple('TEXT',
'CMD CSS CSV HTML PLAIN XML')

_application = namedtuple('APPLICATION',
'ATOM ECMASCRIPT JSON JAVASCRIPT OCTET_STREAM\
 OGG PDF POSTSCRIPT RSS SOAP FONT_WOFF XHTML\
 XML_DTD XOP ZIP X_ZIP')

TEXT = _text(
        ('Content-Type', 'text/cmdl'),
        ('Content-Type', 'text/css'),
        ('Content-Type', 'text/csv'),
        ('Content-Type', 'text/html'),
        ('Content-Type', 'text/plain'),
        ('Content-Type', 'text/xml'),
    )

APPLICATION = _application(
        ('Content-Type', 'application/atom+xml'),
        ('Content-Type', 'application/ecmascript'),
        ('Content-Type', 'application/json'),
        ('Content-Type', 'application/javascript'),
        ('Content-Type', 'application/octet-stream'),
        ('Content-Type', 'application/ogg'),
        ('Content-Type', 'application/pdf'),
        ('Content-Type', 'application/postscript'),
        ('Content-Type', 'application/rss+xml'),
        ('Content-Type', 'application/soap+xml'),
        ('Content-Type', 'application/font-woff'),
        ('Content-Type', 'application/xhtml+xml'),
        ('Content-Type', 'application/xml-dtd'),
        ('Content-Type', 'application/xop+xml'),
        ('Content-Type', 'application/zip'),
        ('Content-Type', 'application/x-gzip'),
    )
