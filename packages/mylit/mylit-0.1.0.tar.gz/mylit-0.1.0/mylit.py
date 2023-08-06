#!/usr/bin/env python

## title = "mylit"
## if True:
##     import sys
##     print >> sys.stderr, "Processing..."

# <h1>mylit</h1>
# <var>mylit</var> is a simple tool for literate programming in <a
# href="http://www.python.org/">Python</a>.  To convert a literate Python
# program called <samp>somefile.py</samp> to HTML, run <samp>python mylit.py
# somefile.py > somefile.html</samp>.

#! TODO: automatic links between identifiers

# We use <a href="http://docs.python.org/library/itertools.html">itertools</a>
# for <a href="#chain">chaining sequences</a>.
import itertools

# We use <a href="http://pygments.org/">Pygments</a> for syntax highlighting.
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

# This is the HTML template that will be filled with code:
template = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <title>%(title)s</title>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <link rel="stylesheet" href="http://pygments.org/media/pygments_style.css">
  </head>
  <body>
    %(body)s
  </body>
</html>
"""

# <code>strip_left()</code> removes whitespace from each line in
# <code>block</code>, plus additional <code>amount</code> characters.  This is
# defined as a function because the list comprehension cannot be used directly
# in <code>format_lines()</code>, which uses an <code>exec</code> statement.
def strip_left(block, amount=0):
    return [x.lstrip()[amount:] for x in block]

# <code>format_lines</code> iterates over the <code>lines</code> object and
# returns HTML.
def format_lines(lines, title=""):
    # The HTML body is stored in <code>body</code>.
    body = []

    # Adjacent lines of the same type are aggregated in <code>block</code> and
    # formatted together.
    block = []
    # The type of the last block is stored in <code>last_block_type</code>.
    last_block_type = None

    # Now we iterate over the lines, formatting comments and code as
    # appropriate.  <a name="chain"><code>None</code> is appended to the list
    # of lines to terminate the last block.</a>
    for line in itertools.chain(lines, [None]):
        # Lines starting with <code>#!</code> are ignored. This includes the traditional
        # "shebang" line as well as any code the user may want to exclude from
        # the output.
        if line is not None and line.strip().startswith("#!"):
            continue

        # A <code>None</code> line terminates the previous block.
        if line is None:
            block_type = None
        # Lines starting with <code>##</code> are executed. This can be used to set
        # configuration variables, for example.
        elif line.strip().startswith("##"):
            block_type = "exec"
        # Any other line starting with <code>#</code> is a comment.
        elif line.strip().startswith("#"):
            block_type = "comment"
        # All other lines are considered code.
        else:
            block_type = "code"

        # Adjacent lines of the same type are aggregated.
        if block_type == last_block_type:
            block.append(line)
        # As soon as the block type changes, the previous block is formatted.
        else:
            # Code is formatted by Pygments.
            if last_block_type == "code":
                body.append('<div class="syntax">' + highlight("".join(block), PythonLexer(), HtmlFormatter()) + '</div>')
            # Exec lines are executed and not copied to the output.
            elif last_block_type == "exec":
                exec("".join(strip_left(block, len(block[0]) - len(block[0].lstrip()[2:].lstrip()))))
            # Comments are copied verbatim to the output.
            elif last_block_type == "comment":
                body.extend(strip_left(block, 1))
            last_block_type = block_type
            block = [line]

    # Insert missing variables into the template and return.
    body = "\n".join(body)
    return template % locals()

# When the script is called from the command line, parse the arguments and run
# <code>format_lines</code>.
if __name__ == "__main__":
    # <a href="http://docs.python.org/dev/library/argparse.html">argparse</a>
    # is used for parsing the command line arguments.
    import argparse
    # <a href="http://docs.python.org/dev/library/os.html">os</a> is used for
    # file name manipulation.
    import os
    # <a href="http://docs.python.org/dev/library/sys.html">sys</a> contains
    # the standard output stream.
    import sys

    # The parser is constructed here.
    parser = argparse.ArgumentParser(description="Convert a literate Python program to HTML.")
    # <code>infilename</code> is a mandatory positional argument.
    parser.add_argument("infilename", help="the input file")
    # <code>outfilename</code> is an optional argument.
    parser.add_argument("outfilename", nargs="?", help="the output file, '-' for standard output")
    # <code>title</code> can be specified to set the document title if the
    # script does not do so itself.
    parser.add_argument("--title", "-t", default="", help="the document title")
    # Parse the arguments.
    args = parser.parse_args()
    # If <code>outfilename</code> is not specified, it is generated from <code>infilename</code>.
    if args.outfilename is None:
        args.outfilename = os.path.splitext(args.infilename)[0] + os.path.extsep + "html"

    # Open the input file and format it.
    with open(args.infilename, "r") as f:
        result = format_lines(f, args.title)
    # Write the results. This happens after the input file is closed, so that
    # in-place formatting is possible.
    with sys.stdout if args.outfilename == "-" else open(args.outfilename, "w") as f:
        f.write(result)

