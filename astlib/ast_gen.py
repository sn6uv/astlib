#-----------------------------------------------------------------
# _ast_gen.py
#
# Generates the AST Node classes from a specification given in
# a .yaml file
#
# The design of this module was inspired by astgen.py from the
# Python 2.5 code-base.
#
# Copyright (C) 2008-2012, Eli Bendersky
# License: BSD
#-----------------------------------------------------------------
import pprint
from string import Template


class ASTCodeGenerator(object):
    def __init__(self, cfg_filename='_c_ast.cfg'):
        """
        Initialize the code generator from a configuration file.
        """
        self.cfg_filename = cfg_filename
        self.node_cfg = [NodeCfg(name, contents) for (name, contents)
                         in self.parse_cfgfile(cfg_filename)]

    def generate(self, file=None):
        """
        Generates the code into file, an open file buffer.
        """
        src = [Template(_PROLOGUE_COMMENT).substitute(
            cfg_filename=self.cfg_filename)]

        src += [node_cfg.generate_source() for node_cfg in self.node_cfg]

        src = '\n\n'.join(src)

        file.write(src)

    def parse_cfgfile(self, filename):
        """
        Parse the configuration file and yield pairs of (name, contents)
        for each node.
        """
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                colon_i = line.find(':')
                lbracket_i = line.find('[')
                rbracket_i = line.find(']')
                if not 1 < colon_i < lbracket_i < rbracket_i:
                    raise RuntimeError(
                        "Invalid line in %s:\n%s\n" % (filename, line))

                name = line[:colon_i]
                val = line[lbracket_i + 1:rbracket_i]
                vallist = [v.strip() for v in val.split(',')] if val else []
                yield name, vallist


class NodeCfg(object):
    """ 
    Node configuration.

    name: node name
    contents: a list of contents - attributes and child nodes
    See comment at the top of the configuration file for details.
    """
    def __init__(self, name, contents):
        self.name = name
        self.all_entries = []
        self.attr = []
        self.child = []
        self.seq_child = []

        for entry in contents:
            clean_entry = entry.rstrip('*')
            self.all_entries.append(clean_entry)

            if entry.endswith('**'):
                self.seq_child.append(clean_entry)
            elif entry.endswith('*'):
                self.child.append(clean_entry)
            else:
                self.attr.append(entry)

    def generate_source(self):
        src = self._gen_init()
        src += '\n' + self._gen_children()
        src += '\n' + self._gen_attr_names() + '\n'
        return src

    def _gen_init(self):
        src = "class %s(Node):\n" % self.name

        if self.all_entries:
            args = ', '.join(self.all_entries)
            arglist = '(self, %s, coord=None)' % args
        else:
            arglist = '(self, coord=None)'

        src += "    def __init__%s:\n" % arglist

        for name in self.all_entries + ['coord']:
            src += "        self.%s = %s\n" % (name, name)

        return src

    def _gen_children(self):
        src = '    def children(self):\n'

        if self.all_entries:
            src += '        nodelist = []\n'

            for child in self.child:
                src += (
                    '        if self.%(child)s is not None:\n'
                    '            nodelist.append('
                    '("%(child)s", self.%(child)s))\n') % (dict(child=child))

            for seq_child in self.seq_child:
                src += (
                    '        if self.%(child)s is not None:\n'
                    '            for i, child in enumerate(self.%(child)s):\n'
                    '                nodelist.append('
                    '("%(child)s[%%d]" %% i, child))\n') % (
                        dict(child=seq_child))

            src += '        return tuple(nodelist)\n'
        else:
            src += '        return ()\n'

        return src

    def _gen_attr_names(self):
        src = ("    attr_names = (%s)" % (
            ' '.join("%r," % nm for nm in self.attr)))
        return src


_PROLOGUE_COMMENT = (
    "#-----------------------------------------------------------------\n"
    "# ** ATTENTION **\n"
    "# This code was automatically generated from the file:\n"
    "# $cfg_filename\n"
    "#\n"
    "# Do not modify it directly. Modify the configuration file and\n"
    "# run the generator again.\n"
    "# ** ** *** ** **\n"
    "#\n"
    "# pycparser: c_ast.py\n"
    "#\n"
    "# AST Node classes.\n"
    "#\n"
    "# Copyright (C) 2008-2012, Eli Bendersky\n"
    "# License: BSD\n"
    "#-----------------------------------------------------------------\n")

if __name__ == "__main__":
    import sys
    ast_gen = ASTCodeGenerator('_c_ast.cfg')
    ast_gen.generate(open('c_ast.py', 'w'))
