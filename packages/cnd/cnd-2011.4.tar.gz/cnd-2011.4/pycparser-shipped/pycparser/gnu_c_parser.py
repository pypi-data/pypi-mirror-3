#-----------------------------------------------------------------
# pycparser: gnu_c_parser.py
#
# CParser class: Parser and AST builder for the C language
#
# Copyright (C) 2011, Eli Bendersky, Andreas Kloeckner
# License: BSD
#-----------------------------------------------------------------

from __future__ import division

from pycparser.c_parser import CParser
import pycparser.c_ast as c_ast



class _AttributesMixin(object):
    def p_attributes_opt_1(self, p):
        """ attributes_opt : attribute_decl attributes_opt
        """
        p[1].exprs.extend(p[2].exprs)
        p[0] = p[1]

    def p_attributes_opt_2(self, p):
        """ attributes_opt : empty
        """
        p[0] = c_ast.ExprList([], self._coord(p.lineno(1)))

    def p_attribute_decl(self, p):
        """ attribute_decl : __ATTRIBUTE__ LPAREN LPAREN attribute_list RPAREN RPAREN
        """
        p[0] = p[4]

    def p_attribute_list_1(self, p):
        """ attribute_list : attribute
        """
        p[0] = c_ast.ExprList([p[1]], self._coord(p.lineno(1)))

    def p_attribute_list_2(self, p):
        """ attribute_list : attribute_list COMMA attribute
        """
        p[1].exprs.append(p[3])
        p[0] = p[1]

    def p_attribute_1(self, p):
        """ attribute : CONST
        """
        p[0] = c_ast.ID(name="const", coord=self._coord(p.lineno(1)))

    def p_attribute_2(self, p):
        """ attribute : assignment_expression
        """
        p[0] = p[1]




class GnuCParser(CParser, _AttributesMixin):
    # TODO: __extension__

    def p_function_specifier_gnu(self, p):
        """ function_specifier  : __INLINE
                                | __INLINE__
        """
        p[0] = p[1]

    def p_type_qualifier_gnu(self, p):
        """ type_qualifier  : __CONST
                            | __RESTRICT
                            | __EXTENSION__
        """
        p[0] = p[1]

    # /!\ name must match C parser
    def p_declarator_1(self, p):
        """ declarator  : direct_declarator attributes_opt
        """
        if p[2].exprs:
            if not isinstance(p[1], c_ast.TypeDecl):
                raise NotImplementedError(
                        "cannot attach attributes to nodes of type '%s'"
                        % type(p[1]))

            p[1].attributes = p[2]

        p[0] = p[1]

    def p_type_specifier_gnu_typeof_expr(self, p):
        """ type_specifier  : __TYPEOF__ LPAREN expression RPAREN
        """
        if isinstance(p[3], c_ast.TypeDecl):
            pass

        p[0] = c_ast.TypeOfExpression(p[3])

    def p_type_specifier_gnu_typeof_decl(self, p):
        """ type_specifier  : __TYPEOF__ LPAREN parameter_declaration RPAREN
        """
        p[0] = c_ast.TypeOfDeclaration(p[3])

    def p_statement_gnu(self, p):
        """ statement   : asm
        """
        p[0] = p[1]

    def p_unary_operator_gnu(self, p):
        """ unary_operator  : __REAL__
                            | __IMAG__
        """
        p[0] = p[1]

    # /!\ name must match C parser
    def p_direct_declarator_5(self, p):
        """ direct_declarator   : direct_declarator LPAREN parameter_type_list RPAREN asm_opt attributes_opt
                                | direct_declarator LPAREN identifier_list_opt RPAREN asm_opt attributes_opt
        """
        func = c_ast.FuncDecl(
            args=p[3],
            type=None,
            attributes=p[6],
            asm=p[5],
            coord=p[1].coord)

        p[0] = self._type_modify_decl(decl=p[1], modifier=func)

    # /!\ name must match C parser
    def p_direct_abstract_declarator_6(self, p):
        """ direct_abstract_declarator  : direct_abstract_declarator LPAREN parameter_type_list_opt RPAREN asm_opt attributes_opt
        """
        func = c_ast.FuncDecl(
            args=p[3],
            type=None,
            attributes=p[6],
            asm=p[5],
            coord=p[1].coord)

        p[0] = self._type_modify_decl(decl=p[1], modifier=func)

    def p_postfix_expression_gnu_tcp(self, p):
        """ postfix_expression  : __BUILTIN_TYPES_COMPATIBLE_P LPAREN parameter_declaration COMMA parameter_declaration RPAREN
        """
        p[0] = c_ast.FuncCall(c_ast.ID(p[1], self._coord(p.lineno(1))),
                c_ast.TypeList([p[3], p[5]], self._coord(p.lineno(2))))

    # {{{ asm

    def p_asm_opt_1(self, p):
        """ asm_opt : empty
        """
        p[0] = None

    def p_asm_opt_2(self, p):
        """ asm_opt : asm
        """
        p[0] = p[1]

    def p_asm_1(self, p):
        """ asm : asm_keyword LPAREN argument_expression_list RPAREN
        """
        p[0] = c_ast.Asm(p[1], p[3], None, None, None, coord=self._coord(p.lineno(1)))

    def p_asm_2(self, p):
        """ asm : asm_keyword LPAREN argument_expression_list COLON argument_expression_list RPAREN
        """
        p[0] = c_ast.Asm(p[1], p[3], p[5], None, None, coord=self._coord(p.lineno(1)))

    def p_asm_3(self, p):
        """ asm : asm_keyword LPAREN argument_expression_list COLON argument_expression_list COLON argument_expression_list RPAREN
        """
        p[0] = c_ast.Asm(p[1], p[3], p[5], p[7], None, coord=self._coord(p.lineno(1)))

    def p_asm_4(self, p):
        """ asm : asm_keyword LPAREN argument_expression_list COLON argument_expression_list COLON argument_expression_list COLON argument_expression_list RPAREN
        """
        p[0] = c_ast.Asm(p[1], p[3], p[5], p[7], p[9], coord=self._coord(p.lineno(1)))

    def p_asm_keyword(self, p):
        """ asm_keyword : __ASM__
                        | __ASM
        """
        p[0] = p[1]

    # }}}
