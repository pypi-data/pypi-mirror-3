import glob
import re
import os

_include_rx  = re.compile(" *include\s+(.*)")
_variable_rx = re.compile(" *([a-zA-Z][a-zA-Z0-9_]+)\s*=\s*(.*)")
_findvar_rx  = re.compile(r"\$((?P<paren>\()|{)"+
                          r"(?P<name>[A-Za-z][A-Za-z0-9_]*)"+
                          r"(?(paren)\)|})")

def _interpolate(key, value, defs):
    while True:
        # mask any "$$"s so our regex doesn't try to use them
        m = _findvar_rx.search(value.replace('$$', '  '))
        if not m: break

        name = m.group("name")
        if name == key:
            raise Exception("Variable %s reference itself (eventually)" % key)
        sub = defs.get(name) or os.getenv(name) or ""
        value = value[:m.start()] + sub + value[m.end():]
    return value
        

def parse_makefile(filename):
    """Parse a Makefile-style file.

    A dictionary containing name/value pairs is returned.
    """
    from distutils.text_file import TextFile
    fp = TextFile(filename, strip_comments=1, skip_blanks=1, join_lines=1)
    oldpath = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(filename)))
    variables = {}

    while True:
        line = fp.readline()
        if line is None:  # eof
            break
        m = _include_rx.match(line)
        if m:
            include = _interpolate(None, m.group(1), variables)
            for f in glob.iglob(include):
                variables.update(parse_makefile(f))
            continue

        m = _variable_rx.match(line)
        if m:
            variables[m.group(1)] = m.group(2).strip()
            continue

    for name in variables:
        variables[name] = _interpolate(name, variables[name], variables)
    for name in variables:
        variables[name] = variables[name].replace('$$', '$')

    os.chdir(oldpath)
    fp.close()
    return variables
