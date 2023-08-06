`mylit` is a simple tool for literate programming in Python.

Literate Python programs are just regular Python source files with extensive
comments. When `mylit` is run with a literate Python program as input, it
creates an HTML file containing the comments and highlighted source code.  You
can use HTML markup in comments as you may see fit.

In addition to simple comments, the HTML compilation process can be customized
by starting a comment line with `##`. Anything that follows on such a line will
be executed in the parser's context. The code can, for example, set variables,
manipulate the generated HTML, or generate debug output. Look at the `mylit`
source code to see what it can do.

Lines starting with `#!` are ignored completely. This way, you can comment out
things that are not meant to be included in the final HTML file.

Here's a simple example of what a literate program might look like::

    #!/usr/bin/env python
    #! This line is ignored, as is the previous line.

    #! Set the title variable of the parser:
    ## title = "mylit example"

    # <h1>A simple mylit example</h1>
    # This is a simple example of literate <a
    # href="http://www.python.org/">Python</a> programming with <a
    # href="http://pypi.python.org/pypi/mylit">mylit</a>.

    # Here we define a function that checks whether a given pair of coordinates
    # lies within a circle of radius <code>r</code>.
    def in_circle(x, y, r):
        # We first square both <code>x</code> and <code>y</code>, and sum them up.
        s = x ** 2 + y ** 2

        # <p>Note how the above comment contains HTML markup. The indentation of
        # the highlighted Python code is unaffected by interspersed comments.</p>

        # Here we check whether the coordinates (<code>x</code>, <code>y</code>)
        # lie within a circle of radius <code>r</code>.
        if s < r ** 2:
            # Everything's okay, so we can return <code>True</code>:
            return True
        else:
            # We may have a problem here. Better print a warning.
            import warnings
            warnings.warn("Danger, Will Robinson!")
            return False

    # When this program is run from the command line, it performs a simple test.
    if __name__ == "__main__":
        assert in_circle(3, 4, 5.1) == True
        assert in_circle(3, 4, 4.9) == False

Of course, `mylit` itself is a literate Python program.

