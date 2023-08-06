#!/usr/bin/env python

"""
This module provides utility classes for string operations.
"""

__author__ = "Shyue Ping Ong"
__copyright__ = "Copyright 2011, The Materials Project"
__version__ = "1.0"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyue@mit.edu"
__status__ = "Production"
__date__ = "$Sep 23, 2011M$"

import re


def generate_latex_table(results, header=None):
    """
    Generates a string latex table from a sequence of sequence.

    Args:
        result: 2d sequence of arbitrary types.
        header: optional header

    Returns:
        String representation of Latex table with data.
    """
    body = []
    if header != None:
        body.append(" & ".join(header))
        body.append("\\hline")
    maxlength = 0
    for result in results:
        maxlength = max(maxlength, len(result))
        body.append(" & ".join([str(m) for m in result]))
    colstr = 'c' * maxlength
    output = []
    output.append('\\begin{table}[htp]')
    output.append('\\caption{Enter caption}')
    output.append('\\label{mytablelabel}')
    output.append('\\begin{tabular*}{\\textwidth}{@{\\extracolsep{\\fill}}' +
                  colstr + '}')
    output.append('\\hline')
    output.append("\\\\\n".join(body) + "\\\\")
    output.append('\\hline')
    output.append('\\end{tabular*}')
    output.append('\\end{table}')
    return "\n".join(output)


def str_delimited(results, header=None, delimiter="\t"):
    """
    Given a tuple of tuples, generate a delimited string form.
    >>> results = [['a','b','c'],['d','e','f'],[1,2,3]]
    >>> print str_delimited(results,delimiter=',')
    a,b,c
    d,e,f
    1,2,3

    Args:
        result: 2d sequence of arbitrary types.
        header: optional header

    Returns:
        Aligned string output in a table-like format.
    """
    returnstr = ''
    if header != None:
        returnstr += delimiter.join(header) + "\n"
    return returnstr + "\n".join([delimiter.join([str(m) for m in result])
                                  for result in results])


def str_aligned(results, header=None):
    """
    Given a tuple, generate a nicely aligned string form.
    >>> results = [['a','b','cz'],['d','ez','f'],[1,2,3]]
    >>> print str_aligned(results)
    a    b   cz
    d   ez    f
    1    2    3

    Args:
        result: 2d sequence of arbitrary types.
        header: optional header

    Returns:
        Aligned string output in a table-like format.
    """
    k = list(zip(*results))
    stringlengths = list()
    count = 0
    for i in k:
        col_max_len = max([len(str(m)) for m in i])
        if header != None:
            col_max_len = max([len(str(header[count])), col_max_len])
        stringlengths.append(col_max_len)
        count += 1
    format_string = "   ".join(["%" + str(d) + "s" for d in stringlengths])
    returnstr = ''
    if header != None:
        header_str = format_string % tuple(header)
        returnstr += header_str + "\n"
        returnstr += "-" * len(header_str) + "\n"
    return returnstr + "\n".join([format_string % tuple(result)
                                  for result in results])


def formula_double_format(afloat, ignore_ones=True, tol=1e-8):
    """
    This function is used to make pretty formulas by formatting the amounts.
    Instead of Li1.0 Fe1.0 P1.0 O4.0, you get LiFePO4.

    Args:
        afloat:
            a float
        ignore_ones:
            if true, floats of 1 are ignored.
        tol:
            Tolerance to round to nearest int. i.e. 2.0000000001 -> 2

    Returns:
        A string representation of the float for formulas.
    """
    if ignore_ones and afloat == 1:
        return ""
    elif abs(afloat - int(afloat)) < tol:
        return str(int(afloat))
    else:
        return str(afloat)


def latexify(formula):
    """
    Generates a latex formatted formula. E.g., Fe2O3 is transformed to
    Fe$_{2}$O$_{3}$.

    Args:
        formula:
            Input formula.

    Returns:
        Formula suitable for display as in LaTeX with proper subscripts.
    """
    return re.sub(r"(\d+)", r'$_{\1}$', formula)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
