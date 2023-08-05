"""
Provide an mselect filter type. This extends the filter syntax
to allow a union of two or more select type filters in one
filter step. This allows for union or multiple type selections.
The following example will select those tiddlers which have tag
blog OR tag published and then sort by modified time:

        mselect=tag:blog,tag:published;sort=-modified

Install by adding 'tiddlywebplugins.mselect' to 'system_plugins'
in tiddlywebconfig.py.
"""

from tiddlyweb.filters import FILTER_PARSERS, FilterError
from tiddlyweb.filters.select import select_parse


MSELECT_SEPARATOR = ','

# XXX: make the function available for testing.
# This enclosure mess works around some bugs in
# control.filter_tiddlers_from_bag which are fixed in
# TiddlyWeb 1.1
test_mselect = None


def init(config):

    global test_mselect

    def mselect(command, entities, environ=None):
        global separator
        if environ:
            try:
                separator = environ['tiddlyweb.config']['mselect.separator']
            except (TypeError, KeyError):
                separator = MSELECT_SEPARATOR
        else:
            separator = config.get('mselect.separator', MSELECT_SEPARATOR)

        commands = command.split(separator)
        try:
            parsed_commands = [select_parse(command) for command in commands]
        except ValueError, exc:
            raise FilterError('malformed filter: %s' % exc)

        # unwind the (probably) generator so we can use it multiple times
        entities = list(entities)
        seen_results = []

        for func in parsed_commands:
            for result in func(entities, environ=environ):
                if result not in seen_results:
                    yield result

        return

    def mselect_parse(command):
        def selector(entities, indexable=False, environ=None):
            return mselect(command, entities, environ)
        return selector

    FILTER_PARSERS['mselect'] = mselect_parse

    test_mselect = mselect
