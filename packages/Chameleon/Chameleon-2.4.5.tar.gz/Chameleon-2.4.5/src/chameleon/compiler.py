import re
import sys
import itertools
import logging
import threading
import functools

try:
    import ast
except ImportError:
    from chameleon import ast24 as ast

try:
    fast_string = str
    str = unicode
    bytes = fast_string
except NameError:
    long = int
    basestring = str
    fast_string = str

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

from .astutil import load
from .astutil import store
from .astutil import param
from .astutil import swap
from .astutil import subscript
from .astutil import node_annotations
from .astutil import annotated
from .astutil import NameLookupRewriteVisitor
from .astutil import Comment
from .astutil import Symbol
from .astutil import Builtin

from .codegen import TemplateCodeGenerator
from .codegen import template

from .tales import StringExpr
from .tal import ErrorInfo
from .i18n import fast_translate

from .nodes import Text
from .nodes import Value
from .nodes import Substitution
from .nodes import Assignment
from .nodes import Module
from .nodes import Context

from .config import DEBUG_MODE
from .exc import TranslationError
from .utils import DebuggingOutputStream
from .utils import char2entity
from .utils import ListDictProxy

log = logging.getLogger('chameleon.compiler')

COMPILER_INTERNALS_OR_DISALLOWED = set([
    "econtext",
    "rcontext",
    "translate",
    "decode",
    "convert",
    "str",
    "int",
    "float",
    "long",
    "len",
    "None",
    "True",
    "False",
    "RuntimeError",
    ])


RE_MANGLE = re.compile('[\-: ]')

if DEBUG_MODE:
    LIST = template("cls()", cls=DebuggingOutputStream, mode="eval")
else:
    LIST = template("[]", mode="eval")


def identifier(prefix, suffix=None):
    return "__%s_%s" % (prefix, mangle(suffix or id(prefix)))


def mangle(string):
    return RE_MANGLE.sub('_', str(string)).replace('\n', '')


def load_econtext(name):
    return template("getitem(KEY)", KEY=ast.Str(s=name), mode="eval")


def store_econtext(name):
    name = fast_string(name)
    return subscript(name, load("econtext"), ast.Store())


def store_rcontext(name):
    name = fast_string(name)
    return subscript(name, load("rcontext"), ast.Store())


@template
def emit_node(node):  # pragma: no cover
    __append(node)


@template
def emit_node_if_non_trivial(node):  # pragma: no cover
    if node is not None:
        __append(node)


@template
def emit_bool(target, s, default_marker=None,
                 default=None):  # pragma: no cover
    if target is default_marker:
        target = default
    elif target:
        target = s
    else:
        target = None

@template
def emit_convert(target, encoded=bytes, str=str, long=long, type=type,
                 default_marker=None, default=None):  # pragma: no cover
    if target is None:
        pass
    elif target is default_marker:
        target = default
    else:
        __tt = type(target)

        if __tt is int or __tt is float or __tt is long:
            target = str(target)
        elif __tt is encoded:
            target = decode(target)
        elif __tt is not str:
            try:
                target = target.__html__
            except AttributeError:
                __converted = convert(target)
                target = str(target) if target is __converted else __converted
            else:
                target = target()


@template
def emit_translate(target, msgid, default=None):  # pragma: no cover
    target = translate(msgid, default=default, domain=__i18n_domain)


@template
def emit_convert_and_escape(
    target, quote=None, quote_entity=None, str=str, long=long,
    type=type, encoded=bytes, default_marker=None, default=None):  # pragma: no cover
    if target is None:
        pass
    elif target is default_marker:
        target = default
    else:
        __tt = type(target)

        if __tt is int or __tt is float or __tt is long:
            target = str(target)
        else:
            try:
                if __tt is encoded:
                    target = decode(target)
                elif __tt is not str:
                    try:
                        target = target.__html__
                    except:
                        __converted = convert(target)
                        target = str(target) if target is __converted else __converted
                    else:
                        raise RuntimeError
            except RuntimeError:
                target = target()
            else:
                if target is not None:
                    try:
                        escape = __re_needs_escape(target) is not None
                    except TypeError:
                        pass
                    else:
                        if escape:
                            # Character escape
                            if '&' in target:
                                target = target.replace('&', '&amp;')
                            if '<' in target:
                                target = target.replace('<', '&lt;')
                            if '>' in target:
                                target = target.replace('>', '&gt;')
                            if quote is not None and quote in target:
                                target = target.replace(quote, quote_entity)


class ExpressionEngine(object):
    """Expression engine.

    This test demonstrates how to configure and invoke the engine.

    >>> from chameleon import tales
    >>> parser = tales.ExpressionParser({
    ...     'python': tales.PythonExpr,
    ...     'not': tales.NotExpr,
    ...     'exists': tales.ExistsExpr,
    ...     'string': tales.StringExpr,
    ...     }, 'python')

    >>> engine = ExpressionEngine(parser)

    An expression evaluation function:

    >>> eval = lambda expression: tales.test(
    ...     tales.IdentityExpr(expression), engine)

    We have provided 'python' as the default expression type. This
    means that when no prefix is given, the expression is evaluated as
    a Python expression:

    >>> eval('not False')
    True

    Note that the ``type`` prefixes bind left. If ``not`` and
    ``exits`` are two expression type prefixes, consider the
    following::

    >>> eval('not: exists: int(None)')
    True

    The pipe operator binds right. In the following example, but
    arguments are evaluated against ``not: exists: ``.

    >>> eval('not: exists: help')
    False

    >>> eval('string:test ${1}${2}')
    'test 12'

    """

    supported_char_escape_set = set(('&', '<', '>'))

    def __init__(self, parser, char_escape=(),
                 default=None, default_marker=None):
        self._parser = parser
        self._char_escape = char_escape
        self._default = default
        self._default_marker = default_marker

    def __call__(self, string, target):
        # BBB: This method is deprecated. Instead, a call should first
        # be made to ``parse`` and then one of the assignment methods
        # ("value" or "text").

        compiler = self.parse(string)
        return compiler(string, target)

    def parse(self, string):
        expression = self._parser(string)

        def exception_wrapper(target, engine, result_type=None, *args):
            stmts = expression(target, engine)

            if result_type is not None:
                method = getattr(self, '_convert_%s' % result_type)
                steps = method(target, *args)
                stmts.extend(steps)

            try:
                line, column = string.location
                filename = string.filename
            except AttributeError:
                line, column = 0, 0
                filename = "<string>"

            return [ast.TryExcept(
                body=stmts,
                handlers=[ast.ExceptHandler(
                    body=template(
                        "rcontext.setdefault('__error__', [])."
                        "append((string, line, col, src, sys.exc_info()[1]))\n"
                        "raise",
                        string=ast.Str(s=string),
                        line=ast.Num(n=line),
                        col=ast.Num(n=column),
                        src=ast.Str(s=filename),
                        sys=Symbol(sys),
                        ),
                    )],
                )]

        return ExpressionCompiler(exception_wrapper, self)

    def _convert_bool(self, target, s):
        """Converts value given by ``target`` to a string ``s`` if the
        target is a true value, otherwise ``None``.
        """

        return emit_bool(
            target, ast.Str(s=s),
            default=self._default,
            default_marker=self._default_marker
            )

    def _convert_text(self, target):
        """Converts value given by ``target`` to text."""

        if self._char_escape:
            # This is a cop-out - we really only support a very select
            # set of escape characters
            for supported in '"', '\'', '':
                if supported in self._char_escape:
                    quote = supported
                    break

            if set(self._char_escape) - \
                   self.supported_char_escape_set != set((quote, )):
                raise RuntimeError(
                    "Unsupported escape set: %s." % repr(self._char_escape)
                    )

            entity = char2entity(quote or '\0')

            return emit_convert_and_escape(
                target,
                quote=ast.Str(s=quote),
                quote_entity=ast.Str(s=entity),
                default=self._default,
                default_marker=self._default_marker,
                )

        return emit_convert(
            target,
            default=self._default,
            default_marker=self._default_marker,
            )


class ExpressionCompiler(object):
    def __init__(self, compiler, engine):
        self.compiler = compiler
        self.engine = engine

    def assign_bool(self, target, s):
        return self.compiler(target, self.engine, "bool", s)

    def assign_text(self, target):
        return self.compiler(target, self.engine, "text")

    def assign_value(self, target):
        return self.compiler(target, self.engine)


class ExpressionEvaluator(object):
    """Evaluates dynamic expression.

    This is not particularly efficient, but supported for legacy
    applications.

    >>> from chameleon import tales
    >>> parser = tales.ExpressionParser({'python': tales.PythonExpr}, 'python')
    >>> engine = functools.partial(ExpressionEngine, parser)

    >>> evaluate = ExpressionEvaluator(engine, {
    ...     'foo': 'bar',
    ...     })

    The evaluation function is passed the local and remote context,
    the expression type and finally the expression.

    >>> evaluate({'boo': 'baz'}, {}, 'python', 'foo + boo')
    'barbaz'

    The cache is now primed:

    >>> evaluate({'boo': 'baz'}, {}, 'python', 'foo + boo')
    'barbaz'

    Note that the call method supports currying of the expression
    argument:

    >>> python = evaluate({'boo': 'baz'}, {}, 'python')
    >>> python('foo + boo')
    'barbaz'

    """

    __slots__ = "_engine", "_cache", "_names", "_builtins"

    def __init__(self, engine, builtins):
        self._engine = engine
        self._names, self._builtins = zip(*builtins.items())
        self._cache = {}

    def __call__(self, econtext, rcontext, expression_type, string=None):
        if string is None:
            return functools.partial(
                self.__call__, econtext, rcontext, expression_type
                )

        expression = "%s:%s" % (expression_type, string)

        try:
            evaluate = self._cache[expression]
        except KeyError:
            assignment = Assignment(["_result"], expression, True)
            module = Module("evaluate", Context(assignment))

            compiler = Compiler(
                self._engine, module, ('econtext', 'rcontext') + self._names
                )

            env = {}
            exec(compiler.code, env)
            evaluate = self._cache[expression] = env["evaluate"]

        evaluate(econtext, rcontext, *self._builtins)
        return econtext['_result']


class NameTransform(object):
    """
    >>> nt = NameTransform(set(('foo', 'bar', )), {'boo': 'boz'})
    >>> def test(node):
    ...     rewritten = nt(node)
    ...     module = ast.Module([ast.fix_missing_locations(rewritten)])
    ...     codegen = TemplateCodeGenerator(module)
    ...     return codegen.code

    Any odd name:

    >>> test(load('frobnitz'))
    "getitem('frobnitz')"

    A 'builtin' name will first be looked up via ``get`` allowing fall
    back to the global builtin value:

    >>> test(load('foo'))
    "get('foo', foo)"

    Internal names (with two leading underscores) are left alone:

    >>> test(load('__internal'))
    '__internal'

    Compiler internals or disallowed names:

    >>> test(load('econtext'))
    'econtext'

    Aliased names:

    >>> test(load('boo'))
    'boz'

    """

    def __init__(self, builtins, aliases):
        self.builtins = builtins
        self.aliases = aliases

    def __call__(self, node):
        name = node.id

        # Don't rewrite names that begin with an underscore; they are
        # internal and can be assumed to be locally defined. This
        # policy really should be part of the template program, not
        # defined here in the compiler.
        if name.startswith('__') or name in COMPILER_INTERNALS_OR_DISALLOWED:
            return node

        if isinstance(node.ctx, ast.Store):
            return store_econtext(name)

        aliased = self.aliases.get(name)
        if aliased is not None:
            return load(aliased)

        # If the name is a Python global, first try acquiring it from
        # the dynamic context, then fall back to the global.
        if name in self.builtins:
            return template(
                "get(key, name)",
                mode="eval",
                key=ast.Str(s=name),
                name=load(name),
                )

        # Otherwise, simply acquire it from the dynamic context.
        return load_econtext(name)


class ExpressionTransform(object):
    """Internal wrapper to transform expression nodes into assignment
    statements.

    The node input may use the provided expression engine, but other
    expression node types are supported such as ``Builtin`` which
    simply resolves a built-in name.

    Used internally be the compiler.
    """

    def __init__(self, engine_factory, cache, transform):
        self.engine_factory = engine_factory
        self.cache = cache
        self.transform = transform

    def __call__(self, expression, target):
        if isinstance(target, basestring):
            target = store(target)

        stmts = self.translate(expression, target)

        # Apply dynamic name rewrite transform to each statement
        visitor = NameLookupRewriteVisitor(self.transform)

        for stmt in stmts:
            visitor(stmt)

        return stmts

    def translate(self, expression, target):
        if isinstance(target, basestring):
            target = store(target)

        cached = self.cache.get(expression)

        if cached is not None:
            stmts = [ast.Assign(targets=[target], value=cached)]
        elif isinstance(expression, ast.expr):
            stmts = [ast.Assign(targets=[target], value=expression)]
        else:
            # The engine interface supports simple strings, which
            # default to expression nodes
            if isinstance(expression, basestring):
                expression = Value(expression, True)

            kind = type(expression).__name__
            visitor = getattr(self, "visit_%s" % kind)
            stmts = visitor(expression, target)

            # Add comment
            target_id = getattr(target, "id", target)
            comment = Comment(" %r -> %s" % (expression, target_id))
            stmts.insert(0, comment)

        return stmts

    def visit_Value(self, node, target):
        engine = self.engine_factory()
        compiler = engine.parse(node.value)
        return compiler.assign_value(target)

    def visit_Default(self, node, target):
        value = annotated(node.marker)
        return [ast.Assign(targets=[target], value=value)]

    def visit_Substitution(self, node, target):
        engine = self.engine_factory(
            char_escape=node.char_escape,
            default=node.default,
            )
        compiler = engine.parse(node.value)
        return compiler.assign_text(target)

    def visit_Negate(self, node, target):
        return self.translate(node.value, target) + \
               template("TARGET = not TARGET", TARGET=target)

    def visit_Identity(self, node, target):
        expression = self.translate(node.expression, "__expression")
        value = self.translate(node.value, "__value")

        return expression + value + \
               template("TARGET = __expression is __value", TARGET=target)

    def visit_Equality(self, node, target):
        expression = self.translate(node.expression, "__expression")
        value = self.translate(node.value, "__value")

        return expression + value + \
               template("TARGET = __expression == __value", TARGET=target)

    def visit_Boolean(self, node, target):
        engine = self.engine_factory()
        compiler = engine.parse(node.value)
        return compiler.assign_bool(target, node.s)

    def visit_Interpolation(self, node, target):
        expr = node.value
        if isinstance(expr, Value):
            engine = self.engine_factory()
            attr = "value"
        elif isinstance(expr, Substitution):
            engine = self.engine_factory(
                char_escape=expr.char_escape,
                default=expr.default,
                )
            attr = "text"
        else:
            raise RuntimeError("Bad value: %r." % node.value)

        expression = StringExpr(expr.value, node.braces_required)
        compiler = ExpressionCompiler(expression, engine)
        assign = getattr(compiler, "assign_%s" % attr)

        return assign(target)

    def visit_Translate(self, node, target):
        if node.msgid is not None:
            msgid = ast.Str(s=node.msgid)
        else:
            msgid = target
        return self.translate(node.node, target) + \
               emit_translate(target, msgid, default=target)

    def visit_Static(self, node, target):
        value = annotated(node)
        return [ast.Assign(targets=[target], value=value)]

    def visit_Builtin(self, node, target):
        value = annotated(node)
        return [ast.Assign(targets=[target], value=value)]


class Compiler(object):
    """Generic compiler class.

    Iterates through nodes and yields Python statements which form a
    template program.
    """

    exceptions = NameError, \
                 ValueError, \
                 AttributeError, \
                 LookupError, \
                 TypeError

    defaults = {
        'translate': Symbol(fast_translate),
        'decode': Builtin("str"),
        'convert': Builtin("str"),
        }

    lock = threading.Lock()

    global_builtins = set(builtins.__dict__)

    def __init__(self, engine_factory, node, builtins={}):
        self._scopes = [set()]
        self._expression_cache = {}
        self._translations = []
        self._builtins = builtins
        self._aliases = [{}]

        transform = NameTransform(
            self.global_builtins | set(builtins),
            ListDictProxy(self._aliases),
            )

        self._engine = ExpressionTransform(
            engine_factory,
            self._expression_cache,
            transform,
            )

        if isinstance(node_annotations, dict):
            self.lock.acquire()
            backup = node_annotations.copy()
        else:
            backup = None

        try:
            module = ast.Module([])
            module.body += self.visit(node)
            ast.fix_missing_locations(module)
            generator = TemplateCodeGenerator(module)
        finally:
            if backup is not None:
                node_annotations.clear()
                node_annotations.update(backup)
                self.lock.release()

        self.code = generator.code

    def visit(self, node):
        if node is None:
            return ()
        kind = type(node).__name__
        visitor = getattr(self, "visit_%s" % kind)
        iterator = visitor(node)
        return list(iterator)

    def visit_Sequence(self, node):
        for item in node.items:
            for stmt in self.visit(item):
                yield stmt

    def visit_Element(self, node):
        self._aliases.append(self._aliases[-1].copy())

        for stmt in self.visit(node.start):
            yield stmt

        for stmt in self.visit(node.content):
            yield stmt

        if node.end is not None:
            for stmt in self.visit(node.end):
                yield stmt

        self._aliases.pop()

    def visit_Module(self, node):
        body = []

        body += template("import re")
        body += template("import functools")
        body += template("__marker = object()")
        body += template(
            r"g_re_amp = re.compile(r'&(?!([A-Za-z]+|#[0-9]+);)')"
        )
        body += template(
            r"g_re_needs_escape = re.compile(r'[&<>\"\']').search")

        body += template(
            r"__re_whitespace = "
            r"functools.partial(re.compile('\s+').sub, ' ')",
        )

        # Visit module content
        program = self.visit(node.program)

        body += [ast.FunctionDef(
            name=node.name, args=ast.arguments(
                args=[param(b) for b in self._builtins],
                defaults=(),
                ),
            body=program
            )]

        return body

    def visit_MacroProgram(self, node):
        functions = []

        # Visit defined macros
        macros = getattr(node, "macros", ())
        names = []
        for macro in macros:
            stmts = self.visit(macro)
            function = stmts[-1]
            names.append(function.name)
            functions += stmts

        # Return function dictionary
        functions += [ast.Return(value=ast.Dict(
            keys=[ast.Str(s=name) for name in names],
            values=[load(name) for name in names],
            ))]

        return functions

    def visit_Context(self, node):
        return template("getitem = econtext.__getitem__") + \
               template("get = econtext.get") + \
               self.visit(node.node)

    def visit_Macro(self, node):
        body = []

        # Initialization
        body += template("__append = __stream.append")
        body += template("__re_amp = g_re_amp")
        body += template("__re_needs_escape = g_re_needs_escape")

        # Resolve defaults
        for name in self.defaults:
            body += template(
                "NAME = econtext[KEY]",
                NAME=name, KEY=ast.Str(s=name)
            )

        # Internal set of defined slots
        self._slots = set()

        # Visit macro body
        nodes = itertools.chain(*tuple(map(self.visit, node.body)))

        # Slot resolution
        for name in self._slots:
            body += template(
                "try: NAME = econtext[KEY].pop()\n"
                "except: NAME = None",
                KEY=ast.Str(s=name), NAME=store(name))

        # Append visited nodes
        body += nodes

        function_name = "render" if node.name is None else \
                        "render_%s" % mangle(node.name)

        function = ast.FunctionDef(
            name=function_name, args=ast.arguments(
                args=[
                    param("__stream"),
                    param("econtext"),
                    param("rcontext"),
                    param("__i18n_domain"),
                    ],
                defaults=[load("None")],
            ),
            body=body
            )

        yield function

    def visit_Text(self, node):
        return emit_node(ast.Str(s=node.value))

    def visit_Domain(self, node):
        backup = "__previous_i18n_domain_%d" % id(node)
        return template("BACKUP = __i18n_domain", BACKUP=backup) + \
               template("__i18n_domain = NAME", NAME=ast.Str(s=node.name)) + \
               self.visit(node.node) + \
               template("__i18n_domain = BACKUP", BACKUP=backup)

    def visit_OnError(self, node):
        body = []

        fallback = identifier("__fallback")
        body += template("fallback = len(__stream)", fallback=fallback)

        self._enter_assignment((node.name, ))
        fallback_body = self.visit(node.fallback)
        self._leave_assignment((node.name, ))

        error_assignment = template(
            "econtext[key] = cls(__exc, rcontext['__error__'][-1][1:3])",
            cls=ErrorInfo,
            key=ast.Str(s=node.name),
            )

        body += [ast.TryExcept(
            body=self.visit(node.node),
            handlers=[ast.ExceptHandler(
                type=ast.Tuple(
                    elts=[Builtin(cls.__name__) for cls in self.exceptions],
                    ctx=ast.Load()),
                name=store("__exc"),
                body=(error_assignment + \
                      template("del __stream[fallback:]", fallback=fallback) + \
                      fallback_body
                      ),
                )]
            )]

        return body

    def visit_Content(self, node):
        name = "__content"
        body = self._engine(node.expression, store(name))

        if node.translate:
            body += emit_translate(name, name)

        if node.char_escape:
            body += emit_convert_and_escape(name)
        else:
            body += emit_convert(name)

        body += template("if NAME is not None: __append(NAME)", NAME=name)

        return body

    def visit_Interpolation(self, node):
        name = identifier("content")
        return self._engine(node, name) + \
               emit_node_if_non_trivial(name)

    def visit_Alias(self, node):
        assert len(node.names) == 1
        name = node.names[0]
        target = self._aliases[-1][name] = identifier(name, id(node))
        return self._engine(node.expression, target)

    def visit_Assignment(self, node):
        for name in node.names:
            if name in COMPILER_INTERNALS_OR_DISALLOWED:
                raise TranslationError(
                    "Name disallowed by compiler.", name
                    )

            if name.startswith('__'):
                raise TranslationError(
                    "Name disallowed by compiler (double underscore).",
                    name
                    )

        assignment = self._engine(node.expression, store("__value"))

        if len(node.names) != 1:
            target = ast.Tuple(
                elts=[store_econtext(name) for name in node.names],
                ctx=ast.Store(),
            )
        else:
            target = store_econtext(node.names[0])

        assignment.append(ast.Assign(targets=[target], value=load("__value")))

        for name in node.names:
            if not node.local:
                assignment += template(
                    "rcontext[KEY] = __value", KEY=ast.Str(s=fast_string(name))
                    )

        return assignment

    def visit_Define(self, node):
        scope = set(self._scopes[-1])
        self._scopes.append(scope)

        for assignment in node.assignments:
            if assignment.local:
                for stmt in self._enter_assignment(assignment.names):
                    yield stmt

            for stmt in self.visit(assignment):
                yield stmt

        for stmt in self.visit(node.node):
            yield stmt

        for assignment in node.assignments:
            if assignment.local:
                for stmt in self._leave_assignment(assignment.names):
                    yield stmt

        self._scopes.pop()

    def visit_Omit(self, node):
        return self.visit_Condition(node)

    def visit_Condition(self, node):
        target = "__condition"
        assignment = self._engine(node.expression, target)

        assert assignment

        for stmt in assignment:
            yield stmt

        body = self.visit(node.node) or [ast.Pass()]

        orelse = getattr(node, "orelse", None)
        if orelse is not None:
            orelse = self.visit(orelse)

        test = load(target)

        yield ast.If(test=test, body=body, orelse=orelse)

    def visit_Translate(self, node):
        """Translation.

        Visit items and assign output to a default value.

        Finally, compile a translation expression and use either
        result or default.
        """

        body = []

        # Track the blocks of this translation
        self._translations.append(set())

        # Prepare new stream
        append = identifier("append", id(node))
        stream = identifier("stream", id(node))
        body += template("s = new_list", s=stream, new_list=LIST) + \
                template("a = s.append", a=append, s=stream)

        # Visit body to generate the message body
        code = self.visit(node.node)
        swap(ast.Suite(body=code), load(append), "__append")
        body += code

        # Reduce white space and assign as message id
        msgid = identifier("msgid", id(node))
        body += template(
            "msgid = __re_whitespace(''.join(stream)).strip()",
            msgid=msgid, stream=stream
        )

        default = msgid

        # Compute translation block mapping if applicable
        names = self._translations[-1]
        if names:
            keys = []
            values = []

            for name in names:
                stream, append = self._get_translation_identifiers(name)
                keys.append(ast.Str(s=name))
                values.append(load(stream))

                # Initialize value
                body.insert(
                    0, ast.Assign(
                        targets=[store(stream)],
                        value=ast.Str(s=fast_string(""))))

            mapping = ast.Dict(keys=keys, values=values)
        else:
            mapping = None

        # if this translation node has a name, use it as the message id
        if node.msgid:
            msgid = ast.Str(s=node.msgid)

        # emit the translation expression
        body += template(
            "__append(translate("
            "msgid, mapping=mapping, default=default, domain=__i18n_domain))",
            msgid=msgid, default=default, mapping=mapping
            )

        # pop away translation block reference
        self._translations.pop()

        return body

    def visit_Start(self, node):
        try:
            line, column = node.prefix.location
        except AttributeError:
            line, column = 0, 0

        yield Comment(
            " %s%s ... (%d:%d)\n"
            " --------------------------------------------------------" % (
                node.prefix, node.name, line, column))

        if node.attributes:
            for stmt in emit_node(ast.Str(s=node.prefix + node.name)):
                yield stmt

            for attribute in node.attributes:
                for stmt in self.visit(attribute):
                    yield stmt

            for stmt in emit_node(ast.Str(s=node.suffix)):
                yield stmt
        else:
            for stmt in emit_node(
                ast.Str(s=node.prefix + node.name + node.suffix)):
                yield stmt

    def visit_End(self, node):
        for stmt in emit_node(ast.Str(
            s=node.prefix + node.name + node.space + node.suffix)):
            yield stmt

    def visit_Attribute(self, node):
        f = node.space + node.name + node.eq + node.quote + "%s" + node.quote

        # Static attributes are just outputted directly
        if isinstance(node.expression, ast.Str):
            s = f % node.expression.s
            return template("__append(S)", S=ast.Str(s=s))

        target = identifier("attr", node.name)
        body = self._engine(node.expression, store(target))
        return body + template(
            "if TARGET is not None: __append(FORMAT % TARGET)",
            FORMAT=ast.Str(s=f),
            TARGET=target,
            )

    def visit_Cache(self, node):
        body = []

        for expression in node.expressions:
            name = identifier("cache", id(expression))
            target = store(name)

            # Skip re-evaluation
            if self._expression_cache.get(expression):
                continue

            body += self._engine(expression, target)
            self._expression_cache[expression] = target

        body += self.visit(node.node)

        return body

    def visit_UseInternalMacro(self, node):
        if node.name is None:
            render = "render"
        else:
            render = "render_%s" % mangle(node.name)

        return template("f(__stream, econtext.copy(), rcontext, __i18n_domain)", f=render) + \
               template("econtext.update(rcontext)")

    def visit_DefineSlot(self, node):
        name = "__slot_%s" % mangle(node.name)
        self._slots.add(name)
        body = self.visit(node.node)

        orelse = template("SLOT(__stream, econtext.copy(), rcontext, __i18n_domain)", SLOT=name)
        test = ast.Compare(
            left=load(name),
            ops=[ast.Is()],
            comparators=[load("None")]
            )

        return [
            ast.If(test=test, body=body or [ast.Pass()], orelse=orelse)
            ]

    def visit_Name(self, node):
        """Translation name."""

        if not self._translations:
            raise TranslationError(
                "Not allowed outside of translation.", node.name)

        if node.name in self._translations[-1]:
            raise TranslationError(
                "Duplicate translation name: %s." % node.name)

        self._translations[-1].add(node.name)
        body = []

        # prepare new stream
        stream, append = self._get_translation_identifiers(node.name)
        body += template("s = new_list", s=stream, new_list=LIST) + \
                template("a = s.append", a=append, s=stream)

        # generate code
        code = self.visit(node.node)
        swap(ast.Suite(body=code), load(append), "__append")
        body += code

        # output msgid
        text = Text('${%s}' % node.name)
        body += self.visit(text)

        # Concatenate stream
        body += template("stream = ''.join(stream)", stream=stream)

        return body

    def visit_UseExternalMacro(self, node):
        callbacks = []
        for slot in node.slots:
            key = "__slot_%s" % mangle(slot.name)
            fun = "__fill_%s" % mangle(slot.name)

            body = template("getitem = econtext.__getitem__") + \
                   template("get = econtext.get") + \
                   self.visit(slot.node)

            callbacks.append(
                ast.FunctionDef(
                    name=fun,
                    args=ast.arguments(
                        args=[
                            param("__stream"),
                            param("econtext"),
                            param("rcontext"),
                            param("__i18n_domain"),
                            ],
                        defaults=[load("__i18n_domain")],
                        ),
                    body=body or [ast.Pass()],
                ))

            key = ast.Str(s=key)

            if node.extend:
                update_body = None
            else:
                update_body = template("_slots.append(NAME)", NAME=fun)

            callbacks.append(
                ast.TryExcept(
                    body=template("_slots = getitem(KEY)", KEY=key),
                    handlers=[ast.ExceptHandler(
                        body=template(
                            "_slots = econtext[KEY] = [NAME]",
                            KEY=key, NAME=fun,
                        ))],
                    orelse=update_body
                    ))

        assignment = self._engine(node.expression, store("__macro"))

        return (
            callbacks + \
            assignment + \
            template("__macro.include(__stream, econtext.copy(), rcontext, __i18n_domain)") + \
            template("econtext.update(rcontext)")
            )

    def visit_Repeat(self, node):
        # Used for loop variable definition and restore
        self._scopes.append(set())

        # Variable assignment and repeat key for single- and
        # multi-variable repeat clause
        if node.local:
            contexts = "econtext",
        else:
            contexts = "econtext", "rcontext"

        for name in node.names:
            if name in COMPILER_INTERNALS_OR_DISALLOWED:
                raise TranslationError(
                    "Name disallowed by compiler.", name
                    )

        if len(node.names) > 1:
            targets = [
                ast.Tuple(elts=[
                    subscript(fast_string(name), load(context), ast.Store())
                    for name in node.names], ctx=ast.Store())
                for context in contexts
                ]

            key = ast.Tuple(
                elts=[ast.Str(s=name) for name in node.names],
                ctx=ast.Load())
        else:
            name = node.names[0]
            targets = [
                subscript(fast_string(name), load(context), ast.Store())
                for context in contexts
                ]

            key = ast.Str(s=node.names[0])

        index = identifier("__index", id(node))
        assignment = [ast.Assign(targets=targets, value=load("__item"))]

        # Make repeat assignment in outer loop
        names = node.names
        local = node.local

        outer = self._engine(node.expression, store("__iterator"))

        if local:
            outer[:] = list(self._enter_assignment(names)) + outer

        outer += template(
            "__iterator, INDEX = getitem('repeat')(key, __iterator)",
            key=key, INDEX=index
            )

        # Set a trivial default value for each name assigned to make
        # sure we assign a value even if the iteration is empty
        outer += [ast.Assign(
            targets=[store_econtext(name)
                     for name in node.names],
            value=load("None"))
              ]

        # Compute inner body
        inner = self.visit(node.node)

        # After each iteration, decrease the index
        inner += template("index -= 1", index=index)

        # For items up to N - 1, emit repeat whitespace
        inner += template(
            "if INDEX > 0: __append(WHITESPACE)",
            INDEX=index, WHITESPACE=ast.Str(s=node.whitespace)
            )

        # Main repeat loop
        outer += [ast.For(
            target=store("__item"),
            iter=load("__iterator"),
            body=assignment + inner,
            )]

        # Finally, clean up assignment if it's local
        if outer:
            outer += self._leave_assignment(names)

        self._scopes.pop()

        return outer

    def _get_translation_identifiers(self, name):
        assert self._translations
        prefix = id(self._translations[-1])
        stream = identifier("stream_%d" % prefix, name)
        append = identifier("append_%d" % prefix, name)
        return stream, append

    def _enter_assignment(self, names):
        for name in names:
            for stmt in template(
                "BACKUP = get(KEY, __marker)",
                BACKUP=identifier("backup_%s" % name, id(names)),
                KEY=ast.Str(s=fast_string(name)),
                ):
                yield stmt

    def _leave_assignment(self, names):
        for name in names:
            for stmt in template(
                "if BACKUP is __marker: del econtext[KEY]\n"
                "else:                 econtext[KEY] = BACKUP",
                BACKUP=identifier("backup_%s" % name, id(names)),
                KEY=ast.Str(s=fast_string(name)),
                ):
                yield stmt
