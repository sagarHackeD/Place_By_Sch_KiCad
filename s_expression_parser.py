import re


class S_ExpressionParser():
    "A simple S-expression parser."

    def __tokenize(self, s):
        "Convert a string into a list of tokens."
        return re.findall(r"\(|\)|[^\s()]+", s)

    def __atom(self, token):
        "Numbers become numbers; every other token is a symbol."
        try:
            return int(token)
        except ValueError:
            try:
                return float(token)
            except ValueError:
                return str(token)

    def __parse(self, tokens):
        "Parse a sequence of tokens into an S-expression."
        if len(tokens) == 0:
            raise SyntaxError("unexpected EOF")

        token = tokens.pop(0)

        if token == "(":
            _list = []
            while tokens[0] != ")":
                _list.append(self.__parse(tokens))
            tokens.pop(0)  # pop off ')'
            return _list
        elif token == ")":
            raise SyntaxError("unexpected )")
        else:
            return self.__atom(token)

    def parse_s_expression(self, s):
        "Parse a string into an S-expression."
        return self.__parse(self.__tokenize(s))
