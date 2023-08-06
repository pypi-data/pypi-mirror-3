unified2: pure-python parser for IDS (think `Snort <http://snort.org>`_) unified2 binary log format
---------------------------------------------------------------------------------------------------

Module allows to process IDS logs in binary "unified2" format into
python objects.

It does not resolve rule ids and is not meant to be a replacement for
`barnyard2 <https://github.com/firnsy/barnyard2>`_ or Snort itself in
that role.

In fact, I've found that snort-produced text logs are enough for my
purposes, so **this module isn't really maintained or updated** (at
least by me), so if you really find it useful, I encourage you to fork
the module, and contact me to transfer pypi package ownership to you.

Main purpose is to extract a packet data from the log, associated with
some particular triggered (and resolved/logged separately via other
means, e.g. alert\_syslog or alert\_csv snort modules) rule, so I
haven't paid much attention to processing event metadata.

Module doesn't have C components and doesn't use ctypes, so should be
fairly portable to non-cPython language implementations.

Format
------

Format definition is derived from Snort headers
(src/sfutil/Unified2\_common.h) via
`pyclibrary <https://code.launchpad.net/~luke-campagnola/pyclibrary>`_
module and are cached in unified2/\_format.py file.

Newer definitions (say, if new data types were added) can be generated
by running the same script on the Snort's Unified2\_common.h:

::

    bzr branch lp:pyclibrary
    cd pyclibrary
    python .../unified2/_format.py .../snort-2.X.Y.Z/src/sfutil/Unified2_common.h

Installation
------------

It's a regular package for Python 2.7 (not 3.X).

Using `pip <http://pip-installer.org/>`_ is the best way:

::

    % pip install unified2

If you don't have it, use:

::

    % easy_install pip
    % pip install unified2

Alternatively (`see
also <http://www.pip-installer.org/en/latest/installing.html>`_):

::

    % curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python
    % pip install unified2

Or, if you absolutely must:

::

    % easy_install unified2

But, you really shouldn't do that.

Current-git version can be installed like this:

::

    % pip install 'git+https://github.com/mk-fg/unified2.git#egg=unified2'

Usage
-----

Simple example:

::

    import unified2.parser
    for ev, ev_tail in unified2.parser.parse('/var/log/snort/snort.u2.1337060186'):
        print 'Event:', ev
        if ev_tail: print 'Event tail:', ev_tail

Event object here is a dict of metadata and a "tail", which can either
be a blob or a similar recursively-parsed tuple of metadata-dict and
"tail" (e.g. for UNIFIED2\_EXTRA\_DATA).

unified2.parser.Parser interface is best illustrated by the
unified2.parser.read function:

::

    parser, buff_agg = Parser(), ''
    while True:
        buff = parser.read(src)
        if not buff: break # EOF
        buff_agg += buff
        while True:
            buff_agg, ev = parser.process(buff_agg)
            if ev is None: break
            yield ev

Idea here is that Parser.read method should be called with a stream
(e.g. a file object), returning however many bytes parser needs to get
the next parseable chunk of data (one packet, in case of u2 log) or
whatever can be read at the moment, empty string is usually an
indication of EOF or maybe non-blocking read return.

Parser.process then should be called with accumulated (by Parser.read
calls) buffer, returning the first packet that can be parsed from there
(or None, if buffer isn't large enough) and remaining (non-parsed)
buffer data.

Related stuff
-------------

-  http://manual.snort.org/node21.html#SECTION00369000000000000000
-  http://www.securixlive.com/barnyard2/docs/unified.php
-  https://github.com/firnsy/barnyard2
-  http://blog.snort.org/2010/12/working-with-unified-and-unified2-files.html
-  https://github.com/mephux/unified2
-  https://code.launchpad.net/~luke-campagnola/pyclibrary
-  https://github.com/mk-fg/bordercamp-irc-bot

