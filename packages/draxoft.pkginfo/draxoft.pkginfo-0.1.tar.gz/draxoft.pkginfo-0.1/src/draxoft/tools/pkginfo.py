#!/usr/bin/env python
#-*- coding: utf-8 -*-

import ast
class _SetupTransformer(ast.NodeTransformer):
    def visit_Call(self, node):
        import ast
        if isinstance(node.func, ast.Name) and node.func.id == 'setup':
            node.func.id = '__mock_setup__'
        self.generic_visit(node)
        return node

del ast
class PackageMetadata(dict):
    @classmethod
    def parse_setup(cls, source):
        import ast
        self = cls()
        t = ast.parse(source, filename='setup.py')
        t = _SetupTransformer().visit(t)
        c = compile(t, 'setup.py', 'exec')
        g = globals()
        l = {}
        l['__mock_setup__'] = self.setup
        eval(c, g, l)
        return self
    
    setup = dict.update
    
    @classmethod
    def parse_setup_file(cls, path):
        with open(path, 'r') as f:
            setup = f.read()
        return cls.parse_setup(setup)
    

parse_setup = PackageMetadata.parse_setup
parse_setup_file = PackageMetadata.parse_setup_file