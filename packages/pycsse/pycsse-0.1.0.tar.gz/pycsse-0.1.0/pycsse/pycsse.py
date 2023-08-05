#!/usr/bin/env python
import re
import argparse
from collections import OrderedDict

# TODO Unit tests wanted %)

RE_CSSE_N = re.compile(r'\s+', re.M | re.S)
# TODO Simplified rule expects no * in comments. Needs to be improved someday.
RE_CSSE_COMMENTS = re.compile(r'(/\*([^\*])*\*/)')
RE_CSSE_BLOCK = re.compile(r'\s*(?P<selector>[^?\{]+)\s*\{\s*(?P<rules>[^\}]+)\s*}\s*')
RE_CSSE_RULES = re.compile(r'\s*(?P<property>[^:]+)\s*:\s*(?P<value>[^;]+)\s*;\s*')


class CsseParser(object):
    """Parser for CSSe instructions.
    Translates a string representing CSSe instructions into an OrderedDict.

    """

    _source_string = ''
    _parsed_structure = None

    def __init__(self, source_string):
        self._source_string = source_string

    def parse(self):
        """Translates a string representing CSSe instructions into an OrderedDict."""

        # Prepare for parsing.
        self._source_string = re.subn(RE_CSSE_N, ' ', self._source_string)[0]
        self._source_string = re.subn(RE_CSSE_COMMENTS, ' ', self._source_string)[0]

        blocks = OrderedDict()
        for block in re.finditer(RE_CSSE_BLOCK, self._source_string):
            block_match = block.groups()
            rules = OrderedDict()
            mixin_counter = 0
            for rule in re.finditer(RE_CSSE_RULES, block_match[1]):
                rule_match = rule.groups()
                property = rule_match[0]
                if property == 'mix':
                    mixin_counter += 1
                    property = '%s_%s' % (property, mixin_counter)
                rules[property] = rule_match[1]
            block_name = block_match[0].strip()
            if block_name in blocks:
                # Just update block rules if block was previously defined.
                blocks[block_name].update(rules)
            else:
                blocks[block_name] = rules

        self._parsed_structure = blocks
        self.resolve_vars_block()
        self.resolve_blocks()

    def _resolve_vars_in_values(self, properties):
        """Resolves variables in properties values
        and removes unresolvev ones.

        """

        # Try to resolve variables.
        for var_name, var_value in properties.items():
            if var_value.startswith('@'):
                ref_var_name = var_value.lstrip('@')
                if ref_var_name in self._parsed_structure['_vars']:
                    properties[var_name] = self._parsed_structure['_vars'][ref_var_name]

        # Remove unresolved vars.
        for var_name, var_value in properties.items():
            if var_value.startswith('@'):
                del(properties[var_name])

    def resolve_blocks(self):
        """Resolves variables and mixins in blocks."""
        struc = self._parsed_structure

        # First, resolve variables.
        for block_name, block_rules in struc.items():
            if block_name == '_vars':
                continue
            self._resolve_vars_in_values(block_rules)

        # Second, apply mixins.
        for block_name, block_rules in struc.items():
            for property, value in block_rules.items():
                if property.startswith('mix_'):
                    mixin_class = '.%s' % value
                    if mixin_class in struc:
                        struc[block_name].update(struc[mixin_class])
                    del (struc[block_name][property])

    def resolve_vars_block(self):
        """Resolves variables in variables declaration block and removes
        unresolved variable declarations.

        Note that nested references, i.e. reference to reference
        to variable (and deeper) are only supported for forward declaraions.

        Example::

            vars {
                var_1: resolved;
                var_2: @var_1;
                var_3: @var_2;
            }

            /* Declaration above is the same as: */

            vars {
                var_1: resolved;
                var_2: resolved;
                var_3: resolved;
            }

            /* In below declaration `var_1` and `var_2` won't be resolved. */

            vars {
                var_1: @var_2;
                var_2: @var_3;
                var_3: resolved;
            }


        """
        struc = self._parsed_structure
        if '_vars' in struc:
            self._resolve_vars_in_values(struc['_vars'])

    def get_structure(self):
        """Returns OrderedDict with parsed CSSe structure."""
        if self._parsed_structure is None:
            self.parse()
        return self._parsed_structure


class CssExporter(object):

    def __init__(self, csse_parser):
        self.csse_parser = csse_parser

    def get_output(self, pretty=False):
        struct = self.csse_parser.get_structure()

        gap = br = ''
        if pretty:
            gap = ' '
            br = '\n'

        output = []
        for selector, rules in struct.items():

            if selector == '_vars':
                continue

            output.append('%s%s{' % (selector, gap))

            for property, value in rules.items():
                output.append('%s%s:%s%s;' % (gap * 4, property, gap, value))

            output.append('}%s' % br)

        return br.join(output)


if __name__ == '__main__':

    argparser = argparse.ArgumentParser('pycsse.py')

    # TODO Add debug information output switch.
    # TODO Add demonic mode to watch for CSSe files changes and autoexport.
    argparser.add_argument('source', help='Path to source CSSe file.')
    argparser.add_argument('-o', help='File path to store CSS into.', default=None)
    argparser.add_argument('--pretty', help='Use to get pretty print CSS at output instead of minified.', action='store_true')

    parsed = argparser.parse_args()
    pretty_print = parsed.pretty
    target = parsed.o

    with open(parsed.source, 'r') as source_file:
        source_code = source_file.read()

    exporter = CssExporter(CsseParser(source_code))
    output_css = exporter.get_output(pretty_print)

    if target is None:
        print output_css
    else:
        with open(target, 'w') as target_file:
            target_file.write(output_css)
