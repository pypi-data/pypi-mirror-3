"""mogrify module

Inspired by psycopg's mogrify:
  http://initd.org/psycopg/docs/cursor.html#cursor.mogrify

Relies on the DB-API 2.0 (see http://www.python.org/dev/peps/pep-0249/):
  - paramstyle

"""

import re
from keyword import kwlist
from collections import Mapping, Sequence, namedtuple


IDENT_STR = "[a-zA-Z_]\w*"
IDENT_RE = re.compile("^%s$" % IDENT_STR)


class Error(Exception): pass


try:
    isidentifier = str.isidentifier
except AttributeError:
    # 2.x doesn't have str.isidentifier()
    isidentifier = lambda s: (s in kwlist and IDENT_RE.match(s) is not None)


def render_literal_value(value, type_=None):
    """Render the value of a bind parameter as a quoted literal.

    Adapted from hg.sqlalchemy.org/.../sqlalchemy/sql/compiler.py
      render_literal_value()

    """

    if type_ is not None:
        value = type_(value)

    if isinstance(value, basestring):
        value = value.replace("'", "''")
        return "'%s'" % value
    elif value is None:
        return "NULL"
    elif isinstance(value, (float, int, long)):
        return repr(value)
    elif isinstance(value, decimal.Decimal):
        return str(value)
    else:
        raise TypeError("don't know how to literal-quote %r" % value)


#  else if (PyObject_CheckReadBuffer(obj))
#    {
#      APSW_FAULT_INJECT(DoBindingAsReadBufferFails,asrb=PyObject_AsReadBuffer(obj, &buffer, &buflen), (PyErr_NoMemory(), asrb=-1));
#      PYSQLITE_CUR_CALL(res=sqlite3_bind_blob(self->statement->vdbestatement, arg, buffer, buflen, SQLITE_TRANSIENT));
#    }
#  else if(PyObject_TypeCheck(obj, &ZeroBlobBindType)==1)
#    {
#      PYSQLITE_CUR_CALL(res=sqlite3_bind_zeroblob(self->statement->vdbestatement, arg, ((ZeroBlobBind*)obj)->blobsize));
#    }


Parameter = namedtuple("Parameter", "name index original position")

class ParamStyle(str):
    """A SQL substitution parameter style.

    "start" is the first character expected for the style.
    
    "matcher" is either a regex pattern string or a function.  If a
    string, it should include a named group for "name" or "index", if
    applicable.  If a function, it must take a single string and return
    a tuple of (name, index, original, remainder)

    "valstype" is Mapping or Sequence.

    """
    MATCH_STR = "(?P<original>%s)(?P<remainder>.*)"
    def __new__(cls, name, *args, **kwargs):
        return super(cls, cls).__new__(cls, name)
    def __init__(self, name, matcher, start, valstype):
        if isinstance(matcher, basestring):
            m = re.compile((self.MATCH_STR % matcher), re.S).match
            def matcher(s):
                result = m(s)
                if not result:
                    return None
                result = result.groupdict()
                index = result.get("index")
                index = int(index) if index is not None else index
                return Parameter(result.get("name"),
                                 index,
                                 result.get("original"),
                                 result.get("remainder"))
        self.name = name
        self.matcher = matcher
        self.start = start
        self.valstype = valstype
    def __repr__(self):
        REPR = "%s(%r, %r, %r, %r)"
        qname = type(self).__name__
        matcher = self.regex.pattern if self.regex else self.matcher
        return REPR % (qname, self.name, self.start, matcher, self.valstype)


# allowed paramstyle values from PEP 249
_QMARK = "\?"
_NUMERIC = ":(?P<index>\d+)"
_NAMED = ":(?P<name>%s)" % IDENT_STR
_FORMAT = "%s"
_PYFORMAT = "%%\((?P<name>%s)\)s" % IDENT_STR

QMARK = ParamStyle("qmark", _QMARK, "?", Sequence)
NUMERIC = ParamStyle("numeric", _NUMERIC, ":", Sequence)
NAMED = ParamStyle("named", _NAMED, ":", Mapping)
FORMAT = ParamStyle("format", _FORMAT, "%", Sequence)
PYFORMAT = ParamStyle("pyformat", _PYFORMAT, "%", Mapping)

class BoundStatement(str):
    """A representation of a SQL statement with bound parameters."""

    PARAM_BASE = 0 # pythonic

    PARAMSTYLES = {
            "?": (QMARK,),
            ":": (NUMERIC, NAMED),
            "%": (FORMAT, PYFORMAT),
            }

    def __new__(cls, sql, values):
        bound, names = cls.bind(sql, values)
        obj = super(cls, cls).__new__(cls, bound)
        obj.names = names
        obj.sql = sql
        obj.values = values
        return obj

    def __repr__(self):
        base = type(self)
        return "%s(%s, [])" % (base.__name__, super(base, self).__repr__())

    @classmethod
    def apply_template(cls, sql, values):
        values = (render_literal_value(v) for v in values)
        return sql % tuple(values)

    @classmethod
    def extract_template(cls, sql):
        """Turn bindable vars into '%s' and map any names to indices.

        This will vary from database engine to engine.  By default we'll
        match to one of the paramtypes listed in PEP 349.

        """

        newsql = ""
        names = []

        paramstyle = None
        matcher = None
        remainder = sql
        while remainder:
            if matcher:
                match = matcher(remainder)
            else:
                for style in cls.PARAMSTYLES.get(remainder[0], ()):
                    match = style.matcher(remainder)
                    if match:
                        matcher = style.matcher
                        paramstyle = style
                        break
                else:
                    match = None
            if not match:
                newsql += remainder[0]
                remainder = remainder[1:]
                continue
            name, index, original, remainder = match
            names.append(name or index)
            newsql += "%s"
        return newsql, names

    @classmethod
    def bind(cls, sql, values):
        """Apply the values to the parameters in the SQL statement."""
        sql, names = cls.extract_template(sql)

        nparams = len(names)
        if nparams == 0 and not values:
            return sql, () # common case, no bindings needed or supplied
        if nparams > 0 and not values:
            msg = "Statement has %d bindings but you didn't supply any!"
            raise Error(msg % nparams)

        args = []
        if isinstance(values, Mapping):
            for i in range(cls.PARAM_BASE, nparams + cls.PARAM_BASE):
                key = names[i].name
                if key is None:
                    raise Error(("binding %d has no name, but you supplied a "
                                 "mapping (which only has names).") % i)
                args.append(values[key])
        elif isinstance(values, Sequence):
            if nparams != len(values):
                msg = ("Incorrect number of bindings supplied. The current "
                       "statement uses %d, and there are %d supplied.")
                raise Error(msg % (nparams, len(values)))
            args = values
        else:
            raise Error("expecting sequence or mapping, got %s" % type(values))

        return cls.apply_template(sql, args), names


BoundStatement("select * from ?", ("x",))
BoundStatement("select * from :0", ("x",))
BoundStatement("select * from table where id=? and name=?", (12, "x"))


#class SQLiteBoundStatement(BoundStatement):
#    @classmethod
#    def extract_template(cls, sql):
#        raise NotImplementedError


def sqlite_mogrify(statement, values):
    """Bind the values to the SQL statement.
    
    Based on:
      http://code.google.com/p/apsw/source/browse/src/cursor.c
      APSWCursor_dobindings() and APSWCursor_dobinding()

    See the sqlite C API:
      http://www.sqlite.org/c3ref/bind_blob.html

    Also see:
      http://code.google.com/p/pysqlite/issues/detail?id=20

    Parameter Binding:
      http://www.sqlite.org/lang_expr.html#varparam
      http://www.sqlite.org/c3ref/bind_blob.html
      http://www.sqlite.org/c3ref/bind_parameter_count.html
      http://www.sqlite.org/c3ref/bind_parameter_name.html
      http://www.sqlite.org/c3ref/bind_parameter_index.html
      http://www.postgresql.org/docs/9.1/static/libpq-exec.html#LIBPQ-EXEC-MAIN
      http://www.postgresql.org/docs/9.1/static/libpq-exec.html#LIBPQ-EXEC-ESCAPE-STRING
      http://www.postgresql.org/docs/9.1/static/sql-expressions.html#AEN1822
      https://dndg.it/cgi-bin/gitweb.cgi?p=public/psycopg2.git;a=blob;f=psycopg/cursor_type.c

    """

    for paramstyle in (QMARK, NAMED):
        nargs = parameter_count(statement, paramstyle)
        if nargs == 0 and not values:
            continue # common case, no bindings needed or supplied

        if nargs > 0 and not values:
            msg = "Statement has %d bindings but you didn't supply any!"
            raise Error(msg % nargs)

        bindfunc = VALUES_TYPES[type(values)]
        statement = bindfunc(statement, values, paramtype)

    return statement


