'''
Procedures for generating reports and tables in the LEMON parser generator.
'''

from action import *
from acttab import *
from ccruft import *
from struct import *
from table import *

from sys import stderr


def file_makename(lemp, suffix):
    '''Generate a filename with the given suffix.'''

    from os.path import basename, splitext

    # 2009-07-16 lcs: Put output files in working directory.
    name = basename(lemp.filename)

    name = splitext(name)[0]
    name += suffix
    return name


def file_open(lemp, suffix, mode):
    '''Open a file with a name based on the name of the input file,
    but with a different (specified) suffix, and return the new
    stream.
    '''

    lemp.outname = file_makename(lemp, suffix)

    fp = None

    try:
        fp = open(lemp.outname, mode)
    except:
        if 'w' in mode:
            fprintf(stderr, "Can't open file \"%s\".\n", lemp.outname)
            lemp.errorcnt += 1

    return fp


def Reprint(lemp):
    '''Duplicate the input file without comments and without actions
    on rules.
    '''
    
    printf("// Reprint of input file \"%s\".\n// Symbols:\n", lemp.filename)

    maxlen = 10
    for i in range(lemp.nsymbol):
        sp = lemp.symbols[i]
        l = len(sp.name)
        if l > maxlen:
            maxlen = l

    ncolumns = 76 / (maxlen + 5)
    if ncolumns < 1:
        ncolumns = 1

    skip = (lemp.nsymbol + ncolumns - 1) / ncolumns
    for i in range(skip):
        printf("//")
        for j in range(i, lemp.nsymbol, skip):
            sp = lemp.symbols[j]
            assert sp.index == j
            printf(" %3d %-*.*s", j, maxlen, maxlen, sp.name)
        printf("\n")

    for rp in iterlinks(lemp.rule):
        printf("%s", rp.lhs.name)
        printf(" ::=")
        for i in range(rp.nrhs):
            sp = rp.rhs[i]
            printf(" %s", sp.name)
            if sp.type == MULTITERMINAL:
                for j in range(1, sp.nsubsym):
                    printf("|%s", sp.subsym[j].name)
        printf(".")
        if rp.precsym:
            printf(" [%s]", rp.precsym.name)
        printf("\n")

    return


def ConfigPrint(fp, cfp):
    rp = cfp.rp

    fprintf(fp, "%s ::=", rp.lhs.name)

    for i in range(rp.nrhs + 1):
        if i == cfp.dot:
            fprintf(fp, " *")

        if i == rp.nrhs:
            break

        sp = rp.rhs[i]
        fprintf(fp, " %s", sp.name)
        if sp.type == MULTITERMINAL:
            for j in range(1, sp.nsubsym):
                fprintf(fp, "|%s", sp.subsym[j].name)

    return


def PrintAction(ap, fp, indent):
    '''Print an action to the given file stream.  Return False if
    nothing was actually printed.
    '''
    
    result = True

    if ap.type == SHIFT:
        fprintf(fp, "%*s shift  %d", indent, ap.sp.name, ap.x.stp.statenum)

    elif ap.type == REDUCE:
        fprintf(fp, "%*s reduce %d", indent, ap.sp.name, ap.x.rp.index)

    elif ap.type == ACCEPT:
        fprintf(fp, "%*s accept", indent, ap.sp.name)

    elif ap.type == ERROR:
        fprintf(fp, "%*s error", indent, ap.sp.name)

    elif ap.type in (SRCONFLICT, RRCONFLICT):
        fprintf(fp, "%*s reduce %-3d ** Parsing conflict **",
                indent, ap.sp.name, ap.x.rp.index)

    elif ap.type == SSCONFLICT:
        fprintf(fp, "%*s shift  %d ** Parsing conflict **",
                indent, ap.sp.name, ap.x.stp.statenum)

    elif ap.type in (SH_RESOLVED, RD_RESOLVED, NOT_USED):
        result = False

    return result


def ReportOutput(lemp):
    '''Generate the "y.output" log file.'''

    from set import SetFind

    fp = file_open(lemp, ".out", "wb")
    if fp is None:
        return

    for i in range(lemp.nstate):
        stp = lemp.sorted[i]
        fprintf(fp, "State %d:\n", stp.statenum)
        if lemp.basisflag:
            cfp = stp.bp
        else:
            cfp = stp.cfp

        while cfp:
            if cfp.dot == cfp.rp.nrhs:
                buf = "(%d)" % cfp.rp.index
                fprintf(fp, "    %5s ", buf)
            else:
                fprintf(fp, "          ")

            ConfigPrint(fp, cfp)
            fprintf(fp, "\n")
            if lemp.basisflag:
                cfp = cfp.bp
            else:
                cfp = cfp.next

        fprintf(fp, "\n")
        for ap in iterlinks(stp.ap):
            if PrintAction(ap, fp, 30):
                fprintf(fp, "\n")

        fprintf(fp, "\n")

    fprintf(fp, "----------------------------------------------------\n")
    fprintf(fp, "Symbols:\n")

    for i in range(lemp.nsymbol):
        sp = lemp.symbols[i]
        fprintf(fp, "  %3d: %s", i, sp.name)
        if sp.type == NONTERMINAL:
            fprintf(fp, ":")
            if sp._lambda:
                fprintf(fp, " <lambda>")

            for j in range(lemp.nterminal):
                if sp.firstset and SetFind(sp.firstset, j):
                    fprintf(fp, " %s", lemp.symbols[j].name)

        fprintf(fp, "\n")

    fp.close()

    return


def compute_action(lemp, ap):
    '''Given an action, compute the integer value for that action
    which is to be put in the action table of the generated machine.
    Return negative if no action should be generated.
    '''
    
    if ap.type == SHIFT:
        act = ap.x.stp.statenum

    elif ap.type == REDUCE:
        act = ap.x.rp.index + lemp.nstate

    elif ap.type == ERROR:
        act = lemp.nstate + lemp.nrule

    elif ap.type == ACCEPT:
        act = lemp.nstate + lemp.nrule + 1

    else:
        act = -1

    return act



# The next cluster of routines are for reading the template file and
# writing the results to the generated parser.


def tplt_xfer(name, _in, out, lineno):
    '''Transfer data from "in" to "out" until a line is seen which
    begins with "%%".  The line number is tracked.

    If "name" is given, then any word that begins with "Parse" is
    changed to begin with *name instead.
    '''

    import re

    for line in _in:
        if line[:2] == '%%':
            break

        lineno[0] += 1

        if name:
            l = re.split('([^A-Za-z])(Parse)', line)
            line = ''.join([name if s == 'Parse' else s for s in l])

        fprintf(out, "%s", line)

    return


def tplt_open(lemp):
    '''Find the template file and open it, returning a stream.'''

    from os.path import dirname, splitext, isfile
    import os
    
    templatename = "lempar.c"
    buf = splitext(lemp.filename)[0] + ".lt"

    if isfile(buf):
        tpltname = buf
    elif isfile(templatename):
        tpltname = templatename
    else:
        from os.path import dirname, join
        tpltname = join(dirname(__file__), templatename)
        if not isfile(tpltname):
            tpltname = None

    if tpltname is None and os.sep in lemp.filename:
        # 2009-07-16 lcs
        buf = join(dirname(lemp.filename), templatename)
        if isfile(buf):
            tpltname = buf

    if tpltname is None:
        fprintf(stderr,
                "Can't find the parser driver template file \"%s\".\n",
                templatename)
        lemp.errorcnt += 1
        return None

    try:
        _in = open(tpltname, "rb")
    except IOError:
        fprintf(stderr,
                "Can't open the template file \"%s\".\n",
                templatename)
        lemp.errorcnt += 1
        return None

    return _in


def tplt_linedir(out, lineno, filename):
    '''Print a #line directive line to the output file.'''
    filename = filename.replace('\\', '\\\\')
    fprintf(out, '#line %d "%s"\n', lineno, filename)
    return


def tplt_print(out, lemp, str, lineno):
    '''Print a string to the file and keep the linenumber up to date.'''

    if not str:
        return

    lineno[0] += 1 + str.count('\n')

    out.write(str)

    if str[-1] != '\n':
        fputc('\n', out)
        lineno[0] += 1

    lineno[0] += 2
    tplt_linedir(out, lineno[0], lemp.outname)

    return


def emit_destructor_code(out, sp, lemp, lineno):
    '''Emit code for the destructor for the symbol sp.'''

    cp = None
    linecnt = 0

    if sp.type == TERMINAL:
        cp = lemp.tokendest
        if cp is None:
            return
        fprintf(out, "{\n")
        lineno[0] += 1
    elif sp.destructor:
        cp = sp.destructor
        fprintf(out, "{\n")
        lineno[0] += 1
    elif lemp.vardest:
        cp = lemp.vardest
        if cp is None:
            return
        fprintf(out, "{\n")
        lineno[0] += 1
    else:
        assert False # Cannot happen

    cp.replace('$$', "(yypminor->yy%d)" % sp.dtnum)
    linecnt += cp.count('\n')
    out.write(cp)

    lineno[0] += 3 + linecnt
    fprintf(out, "\n")
    tplt_linedir(out, lineno[0], lemp.outname)
    fprintf(out, "}\n")

    return


def has_destructor(sp, lemp):
    '''Return True if the given symbol has a destructor.'''
    if sp.type == TERMINAL:
        ret = lemp.tokendest is not None
    else:
        ret = (lemp.vardest is not None) or (sp.destructor is not None)
    return ret


def translate_code(lemp, rp):
    '''Take the string that is the action associated with a rule and
    expand the symbols so that they refer to elements of the parser
    stack.
    '''

    from parse import MAXRHS
    from error import ErrorMsg
    import re
    
    lhsused = False          # True if the LHS element has been used
    used = [False] * MAXRHS  # True for each RHS element which is used

    if rp.code is None:
        rp.code = "\n"
        rp.line = rp.ruleline

    z = ""
    l = re.split('(@?[_A-Za-z][_A-Za-z0-9]*)', rp.code)

    for index, item in enumerate(l):
        if index % 2 == 0:
            z += item
            continue

        if item.startswith('@'):
            at = '@'
            cp = item[1:]
        else:
            at = ''
            cp = item

        if cp == rp.lhsalias:
            z += at + "yygotominor.yy%d" % rp.lhs.dtnum
            lhsused = True
        else:
            for i in range(rp.nrhs):
                if cp == rp.rhsalias[i]:
                    if at:
                        # If the argument is of the form @X then
                        # substitute the token number of X, not the
                        # value of X.
                        z += "yymsp[%d].major" % (i - rp.nrhs + 1)
                    else:
                        sp = rp.rhs[i]
                        if sp.type == MULTITERMINAL:
                            dtnum = sp.subsym[0].dtnum
                        else:
                            dtnum = sp.dtnum
                        z += "yymsp[%d].minor.yy%d" % (i - rp.nrhs + 1, dtnum)
                    used[i] = True
                    break
            else:
                z += item

    # Check to make sure the LHS has been used
    if rp.lhsalias and not lhsused:
        ErrorMsg(lemp.filename, rp.ruleline,
                 'Label "%s" for "%s(%s)" is never used.',
                 rp.lhsalias, rp.lhs.name, rp.lhsalias)
        lemp.errorcnt += 1

    # Generate destructor code for RHS symbols which are not used in
    # the reduce code
    for i in range(rp.nrhs):
        if rp.rhsalias[i] and not used[i]:
            ErrorMsg(lemp.filename, rp.ruleline,
                     'Label %s for "%s(%s)" is never used.',
                     rp.rhsalias[i], rp.rhs[i].name, rp.rhsalias[i])
            lemp.errorcnt += 1
        elif rp.rhsalias[i] is None:
            if has_destructor(rp.rhs[i], lemp):
                z += ("  yy_destructor(%d,&yymsp[%d].minor);\n" %
                      (rp.rhs[i].index, i - rp.nrhs + 1))
            else:
                # No destructor defined for this term
                pass

    if rp.code:
        rp.code = Strsafe(z if z else "")

    return


def emit_code(out, rp, lemp, lineno):
    '''Generate code which executes when the rule "rp" is reduced.
    Write the code to "out".  Make sure lineno stays up-to-date.
    '''
    # Generate code to do the reduce action
    if rp.code:
        tplt_linedir(out, rp.line, lemp.filename)
        fprintf(out, "{%s", rp.code)
        lineno[0] += 3 + rp.code.count('\n')
        fprintf(out, "}\n")
        tplt_linedir(out, lineno[0], lemp.outname)
    return


def print_stack_union(out, lemp, plineno, mhflag):
    """Print the definition of the union used for the parser's data
    stack.  This union contains fields for every possible data type
    for tokens and nonterminals.  In the process of computing and
    printing this union, also set the '.dtnum' field of every terminal
    and nonterminal symbol.
    """

    # out:      The output stream
    # lemp:     The main info structure for this parser
    # plineno:  Pointer to the line number
    # mhflag:   True if generating makeheaders output
    

    # Build a hash table of datatypes. The ".dtnum" field of each
    # symbol is filled in with the hash index plus 1.  A ".dtnum"
    # value of 0 is used for terminal symbols.  If there is no
    # %default_type defined then 0 is also used as the .dtnum value
    # for nonterminals which do not specify a datatype using the %type
    # directive.

    arraysize = lemp.nsymbol * 2  # Size of the "types" array
    types = [None] * arraysize # A hash table of datatypes

    for i in range(lemp.nsymbol):

        sp = lemp.symbols[i]
        if sp == lemp.errsym:
            sp.dtnum = arraysize + 1
            continue

        if sp.type != NONTERMINAL or (sp.datatype is None and lemp.vartype is None):
            sp.dtnum = 0
            continue

        # Standardized name for a datatype
        stddt = (sp.datatype or lemp.vartype).strip()

        hash = 0
        for c in stddt:
            hash = (hash * 53) + ord(c)
        hash = (hash & 0x7fffffff) % arraysize
        
        while types[hash]:
            if strcmp(types[hash], stddt) == 0:
                sp.dtnum = hash + 1
                break
            hash += 1
            if hash >= arraysize:
                hash = 0

        if types[hash] is None:
            sp.dtnum = hash + 1
            types[hash] = stddt


    # Print out the definition of YYTOKENTYPE and YYMINORTYPE

    name = lemp.name if lemp.name else "Parse" # Name of the parser
    lineno = plineno[0] # The line number of the output

    if mhflag:
        fprintf(out, "#if INTERFACE\n")
        lineno += 1

    fprintf(out, "#define %sTOKENTYPE %s\n",
            name, lemp.tokentype if lemp.tokentype else "void*")
    lineno += 1
    
    if mhflag:
        fprintf(out, "#endif\n")
        lineno += 1

    fprintf(out, "typedef union {\n")
    lineno += 1
    fprintf(out, "  %sTOKENTYPE yy0;\n", name)
    lineno += 1
    
    for i, t in enumerate(types):
        if t is None:
            continue
        fprintf(out, "  %s yy%d;\n", t, i + 1)
        lineno += 1

    if lemp.errsym.useCnt:
        fprintf(out, "  int yy%d;\n", lemp.errsym.dtnum)
        lineno += 1

    fprintf(out, "} YYMINORTYPE;\n")
    lineno += 1

    plineno[0] = lineno

    return


def minimum_size_type(lwr, upr):
    '''Return the name of a C datatype able to represent values
    between lwr and upr, inclusive.'''

    if lwr >= 0:
        if upr <= 255:
            return "unsigned char"
        elif upr < 65535:
            return "unsigned short int"
        else:
            return "unsigned int"

    elif lwr >= -127 and upr <= 127:
        return "signed char"
    elif lwr >= -32767 and upr < 32767:
        return "short"
    else:
        return "int"


# Each state contains a set of token transaction and a set of
# nonterminal transactions.  Each of these sets makes an instance of
# the following structure.  An array of these structures is used to
# order the creation of entries in the yy_action[] table.

axset = struct(
    'axset', (
        'stp',      # A state
        'isTkn',    # True to use tokens.  False for non-terminals
        'nAction',  # Number of actions
        )
    )


def axset_compare(a, b):
    '''Compare to axset structures for sorting purposes.'''
    return b.nAction - a.nAction


def writeRuleText(out, rp):
    '''Write text on "out" that describes the rule "rp".'''
    fprintf(out, "%s ::=", rp.lhs.name)
    for j in range(rp.nrhs):
        sp = rp.rhs[j]
        fprintf(out, " %s", sp.name)
        if sp.type == MULTITERMINAL:
            for k in range(1, sp.nsubsym):
                fprintf(out, "|%s", sp.subsym[k].name)
    return


def ReportTable(lemp, mhflag):
    '''Generate C source code for the parser.'''

    # mhflag: Output in makeheaders format if true

    _in = tplt_open(lemp)
    if _in is None:
        return

    out = file_open(lemp, ".c", "wb")
    if out is None:
        _in.close()
        return

    lineno = [1]
    tplt_xfer(lemp.name, _in, out, lineno)


    #
    # Generate the include code, if any
    #
    
    tplt_print(out, lemp, lemp.include, lineno)

    if mhflag:
        name = file_makename(lemp, ".h")
        fprintf(out, "#include \"%s\"\n", name)
        lineno[0] += 1

    tplt_xfer(lemp.name, _in, out, lineno)


    #
    # Generate #defines for all tokens
    #
    
    if mhflag:
        fprintf(out, "#if INTERFACE\n")
        lineno[0] += 1
        prefix = lemp.tokenprefix or ""
        for i in range(1, lemp.nterminal):
            fprintf(out, "#define %s%-30s %2d\n",
                    prefix, lemp.symbols[i].name, i)
            lineno[0] += 1
        fprintf(out, "#endif\n")
        lineno[0] += 1

    tplt_xfer(lemp.name, _in, out, lineno)


    #
    # Generate the defines
    #
    
    fprintf(out, "#define YYCODETYPE %s\n",
            minimum_size_type(0, lemp.nsymbol + 5))
    lineno[0] += 1
    fprintf(out, "#define YYNOCODE %d\n", lemp.nsymbol + 1)
    lineno[0] += 1
    fprintf(out, "#define YYACTIONTYPE %s\n",
            minimum_size_type(0, (lemp.nstate + lemp.nrule) + 5))
    lineno[0] += 1
    if lemp.wildcard:
        fprintf(out, "#define YYWILDCARD %d\n",
                lemp.wildcard.index)
        lineno[0] += 1

    print_stack_union(out, lemp, lineno, mhflag)
    fprintf(out, "#ifndef YYSTACKDEPTH\n")
    lineno[0] += 1
    if lemp.stacksize:
        fprintf(out, "#define YYSTACKDEPTH %s\n", lemp.stacksize)
        lineno[0] += 1
    else:
        fprintf(out, "#define YYSTACKDEPTH 100\n")
        lineno[0] += 1

    fprintf(out, "#endif\n")
    lineno[0] += 1
    if mhflag:
        fprintf(out, "#if INTERFACE\n")
        lineno[0] += 1

    name = lemp.name if lemp.name else "Parse"

    if lemp.arg and lemp.arg[0]:
        i = len(lemp.arg)
        while i >= 1 and lemp.arg[i - 1].isspace():
            i -= 1
        while i >= 1 and (lemp.arg[i - 1].isalnum() or lemp.arg[i - 1] == '_'):
            i -= 1
        arg = lemp.arg[i:]

        fprintf(out, "#define %sARG_SDECL %s;\n", name, lemp.arg)
        lineno[0] += 1
        fprintf(out, "#define %sARG_PDECL ,%s\n", name, lemp.arg)
        lineno[0] += 1
        fprintf(out, "#define %sARG_FETCH %s = yypParser->%s\n", name, lemp.arg, arg)
        lineno[0] += 1
        fprintf(out, "#define %sARG_STORE yypParser->%s = %s\n", name, arg, arg)
        lineno[0] += 1
    else:
        fprintf(out, "#define %sARG_SDECL\n", name)
        lineno[0] += 1
        fprintf(out, "#define %sARG_PDECL\n", name)
        lineno[0] += 1
        fprintf(out, "#define %sARG_FETCH\n", name)
        lineno[0] += 1
        fprintf(out, "#define %sARG_STORE\n", name)
        lineno[0] += 1

    if mhflag:
        fprintf(out, "#endif\n")
        lineno[0] += 1

    fprintf(out, "#define YYNSTATE %d\n", lemp.nstate)
    lineno[0] += 1
    fprintf(out, "#define YYNRULE %d\n", lemp.nrule)
    lineno[0] += 1
    if lemp.errsym.useCnt:
        fprintf(out, "#define YYERRORSYMBOL %d\n", lemp.errsym.index)
        lineno[0] += 1
        fprintf(out, "#define YYERRSYMDT yy%d\n", lemp.errsym.dtnum)
        lineno[0] += 1

    if lemp.has_fallback:
        fprintf(out, "#define YYFALLBACK 1\n")
        lineno[0] += 1

    tplt_xfer(lemp.name, _in, out, lineno)


    # Generate the action table and its associates:
    #
    #  yy_action[]        A single table containing all actions.
    #  yy_lookahead[]     A table containing the lookahead for each entry in
    #                     yy_action.  Used to detect hash collisions.
    #  yy_shift_ofst[]    For each state, the offset into yy_action for
    #                     shifting terminals.
    #  yy_reduce_ofst[]   For each state, the offset into yy_action for
    #                     shifting non-terminals after a reduce.
    #  yy_default[]       Default action for each state.


    #
    # Compute the actions on all states and count them up
    #

    ax = [None] * (lemp.nstate * 2)

    for i in range(lemp.nstate):
        stp = lemp.sorted[i]
        ax[i*2] = axset(
            stp = stp,
            isTkn = True,
            nAction = stp.nTknAct,
            )
        ax[i*2+1] = axset(
            stp = stp,
            isTkn = False,
            nAction = stp.nNtAct,
            )


    # Compute the action table.  In order to try to keep the size of
    # the action table to a minimum, the heuristic of placing the
    # largest action sets first is used.

    mxTknOfst = mnTknOfst = 0
    mxNtOfst = mnNtOfst = 0

    ax.sort(cmp = axset_compare)
    pActtab = acttab_alloc()

    i = 0
    while i < lemp.nstate*2 and ax[i].nAction > 0:
        stp = ax[i].stp

        if ax[i].isTkn:
            for ap in iterlinks(stp.ap):
                if ap.sp.index >= lemp.nterminal:
                    continue

                action = compute_action(lemp, ap)
                if action < 0:
                    continue

                acttab_action(pActtab, ap.sp.index, action)

            stp.iTknOfst = acttab_insert(pActtab)
            if stp.iTknOfst < mnTknOfst:
                mnTknOfst = stp.iTknOfst

            if stp.iTknOfst > mxTknOfst:
                mxTknOfst = stp.iTknOfst

        else:
            for ap in iterlinks(stp.ap):
                if ap.sp.index < lemp.nterminal:
                    continue

                if ap.sp.index == lemp.nsymbol:
                    continue

                action = compute_action(lemp, ap)
                if action < 0:
                    continue

                acttab_action(pActtab, ap.sp.index, action)

            stp.iNtOfst = acttab_insert(pActtab)

            if stp.iNtOfst < mnNtOfst:
                mnNtOfst = stp.iNtOfst
            if stp.iNtOfst > mxNtOfst:
                mxNtOfst = stp.iNtOfst

        i += 1
    
    ax = None


    #
    # Output the yy_action table
    #
    
    fprintf(out, "static const YYACTIONTYPE yy_action[] = {\n")
    lineno[0] += 1

    n = acttab_size(pActtab)

    j = 0
    for i in range(n):
        action = acttab_yyaction(pActtab, i)
        if action < 0:
            action = lemp.nstate + lemp.nrule + 2

        if j == 0:
            fprintf(out, " /* %5d */ ", i)

        fprintf(out, " %4d,", action)

        if j == 9 or i == n - 1:
            fprintf(out, "\n")
            lineno[0] += 1
            j = 0
        else:
            j += 1

    fprintf(out, "};\n")
    lineno[0] += 1


    #
    # Output the yy_lookahead table
    #
    
    fprintf(out, "static const YYCODETYPE yy_lookahead[] = {\n")
    lineno[0] += 1

    j = 0
    for i in range(n):
        la = acttab_yylookahead(pActtab, i)
        if la < 0:
            la = lemp.nsymbol

        if j == 0:
            fprintf(out, " /* %5d */ ", i)

        fprintf(out, " %4d,", la)
        if j == 9 or i == n - 1:
            fprintf(out, "\n")
            lineno[0] += 1
            j = 0
        else:
            j += 1

    fprintf(out, "};\n")
    lineno[0] += 1


    #
    # Output the yy_shift_ofst[] table
    #

    fprintf(out, "#define YY_SHIFT_USE_DFLT (%d)\n", mnTknOfst - 1)
    lineno[0] += 1

    n = lemp.nstate
    while n > 0 and lemp.sorted[n-1].iTknOfst == NO_OFFSET:
        n -= 1

    fprintf(out, "#define YY_SHIFT_MAX %d\n", n - 1)
    lineno[0] += 1
    fprintf(out, "static const %s yy_shift_ofst[] = {\n", minimum_size_type(mnTknOfst - 1, mxTknOfst))
    lineno[0] += 1

    j = 0
    for i in range(n):
        stp = lemp.sorted[i]
        ofst = stp.iTknOfst

        if ofst == NO_OFFSET:
            ofst = mnTknOfst - 1

        if j == 0:
            fprintf(out, " /* %5d */ ", i)

        fprintf(out, " %4d,", ofst)

        if j == 9 or i == n - 1:
            fprintf(out, "\n")
            lineno[0] += 1
            j = 0
        else:
            j += 1

    fprintf(out, "};\n")
    lineno[0] += 1


    #
    # Output the yy_reduce_ofst[] table
    #
    
    fprintf(out, "#define YY_REDUCE_USE_DFLT (%d)\n", mnNtOfst - 1)
    lineno[0] += 1
    
    n = lemp.nstate
    while n > 0 and lemp.sorted[n-1].iNtOfst == NO_OFFSET:
        n -= 1

    fprintf(out, "#define YY_REDUCE_MAX %d\n", n - 1)
    lineno[0] += 1
    fprintf(out, "static const %s yy_reduce_ofst[] = {\n", minimum_size_type(mnNtOfst - 1, mxNtOfst))
    lineno[0] += 1

    j = 0
    for i in range(n):
        stp = lemp.sorted[i]
        ofst = stp.iNtOfst

        if ofst == NO_OFFSET:
            ofst = mnNtOfst - 1

        if j == 0:
            fprintf(out, " /* %5d */ ", i)

        fprintf(out, " %4d,", ofst)

        if j == 9 or i == n - 1:
            fprintf(out, "\n")
            lineno[0] += 1
            j = 0
        else:
            j += 1

    fprintf(out, "};\n")
    lineno[0] += 1


    #
    # Output the default action table
    #
    
    fprintf(out, "static const YYACTIONTYPE yy_default[] = {\n")
    lineno[0] += 1

    n = lemp.nstate

    j = 0
    for i in range(n):
        stp = lemp.sorted[i]

        if j == 0:
            fprintf(out, " /* %5d */ ", i)

        fprintf(out, " %4d,", stp.iDflt)

        if j == 9 or i == n - 1:
            fprintf(out, "\n")
            lineno[0] += 1
            j = 0
        else:
            j += 1

    fprintf(out, "};\n")
    lineno[0] += 1
    tplt_xfer(lemp.name, _in, out, lineno)


    #
    # Generate the table of fallback tokens.
    #

    if lemp.has_fallback:
        for i in range(lemp.nterminal):
            p = lemp.symbols[i]
            
            if p.fallback is None:
                fprintf(out, "    0,  /* %10s => nothing */\n", p.name)
            else:
                fprintf(out, "  %3d,  /* %10s => %s */\n",
                        p.fallback.index, p.name, p.fallback.name)

            lineno[0] += 1

    tplt_xfer(lemp.name, _in, out, lineno)


    #
    # Generate a table containing the symbolic name of every symbol
    #

    for i in range(lemp.nsymbol):
        line = "\"%s\"," % lemp.symbols[i].name
        fprintf(out, "  %-15s", line)
        
        if (i & 3) == 3:
            fprintf(out, "\n")
            lineno[0] += 1

    if (i & 3) != 0:
        fprintf(out, "\n")
        lineno[0] += 1

    tplt_xfer(lemp.name, _in, out, lineno)


    # Generate a table containing a text string that describes every
    # rule in the rule set of the grammer.  This information is used
    # when tracing REDUCE actions.

    for i, rp in enumerate(iterlinks(lemp.rule)):
        assert rp.index == i
        fprintf(out, " /* %3d */ \"", i)
        writeRuleText(out, rp)
        fprintf(out, "\",\n")
        lineno[0] += 1

    tplt_xfer(lemp.name, _in, out, lineno)

    
    # Generate code which executes every time a symbol is popped from
    # the stack while processing errors or while destroying the
    # parser.  (In other words, generate the %destructor actions)

    if lemp.tokendest:
        for i in range(lemp.nsymbol):
            sp = lemp.symbols[i]

            if sp is None or sp.type != TERMINAL:
                continue

            fprintf(out, "    case %d: /* %s */\n",
                    sp.index, sp.name)
            lineno[0] += 1

        for i in range(lemp.nsymbol):
            if lemp.symbols[i].type == TERMINAL:
                emit_destructor_code(out, lemp.symbols[i], lemp, lineno)
                fprintf(out, "      break;\n")
                lineno[0] += 1
                break

    if lemp.vardest:
        dflt_sp = None

        for i in range(lemp.nsymbol):
            sp = lemp.symbols[i]

            if (sp is None or sp.type == TERMINAL or
                sp.index <= 0 or sp.destructor is not None):
                continue

            fprintf(out, "    case %d: /* %s */\n", sp.index, sp.name)
            lineno[0] += 1
            dflt_sp = sp

        if dflt_sp:
            emit_destructor_code(out, dflt_sp, lemp, lineno)
            fprintf(out, "      break;\n")
            lineno[0] += 1

    for i in range(lemp.nsymbol):
        sp = lemp.symbols[i]

        if sp is None or sp.type == TERMINAL or sp.destructor is None:
            continue

        fprintf(out, "    case %d: /* %s */\n", sp.index, sp.name)
        lineno[0] += 1

        # Combine duplicate destructors into a single case
        for j in range(i + 1, lemp.nsymbol):
            sp2 = lemp.symbols[j]
            if (sp2 and sp2.type != TERMINAL and sp2.destructor
                and sp2.dtnum == sp.dtnum
                and strcmp(sp.destructor, sp2.destructor) == 0):
                fprintf(out, "    case %d: /* %s */\n", sp2.index, sp2.name)
                lineno[0] += 1
                sp2.destructor = None

        emit_destructor_code(out, lemp.symbols[i], lemp, lineno)
        fprintf(out, "      break;\n")
        lineno[0] += 1

    tplt_xfer(lemp.name, _in, out, lineno)


    #
    # Generate code which executes whenever the parser stack overflows
    #
    
    tplt_print(out, lemp, lemp.overflow, lineno)
    tplt_xfer(lemp.name, _in, out, lineno)


    # Generate the table of rule information 
    #
    # Note: This code depends on the fact that rules are number
    # sequentually beginning with 0.
  
    for rp in iterlinks(lemp.rule):
        fprintf(out, "  { %d, %d },\n", rp.lhs.index, rp.nrhs)
        lineno[0] += 1
    tplt_xfer(lemp.name, _in, out, lineno)


    #
    # Generate code which execution during each REDUCE action
    #
    
    for rp in iterlinks(lemp.rule):
        translate_code(lemp, rp)

    for rp in iterlinks(lemp.rule):
        if rp.code is None:
            continue

        fprintf(out, "      case %d: /* ", rp.index)
        writeRuleText(out, rp)
        fprintf(out, " */\n")
        lineno[0] += 1

        for rp2 in iterlinks(rp.next):
            if rp2.code == rp.code:
                fprintf(out, "      case %d: /* ", rp2.index)
                writeRuleText(out, rp2)
                fprintf(out, " */\n")
                lineno[0] += 1
                rp2.code = None

        emit_code(out, rp, lemp, lineno)
        fprintf(out, "        break;\n")
        lineno[0] += 1

    tplt_xfer(lemp.name, _in, out, lineno)


    #
    # Generate code which executes if a parse fails
    #
    
    tplt_print(out, lemp, lemp.failure, lineno)
    tplt_xfer(lemp.name, _in, out, lineno)


    #
    # Generate code which executes when a syntax error occurs
    #
    
    tplt_print(out, lemp, lemp.error, lineno)
    tplt_xfer(lemp.name, _in, out, lineno)


    #
    # Generate code which executes when the parser accepts its input
    #
    
    tplt_print(out, lemp, lemp.accept, lineno)
    tplt_xfer(lemp.name, _in, out, lineno)


    #
    # Append any addition code the user desires
    #
    
    tplt_print(out, lemp, lemp.extracode, lineno)
    

    _in.close()
    out.close()

    return


def ReportHeader(lemp):
    '''Generate a header file for the parser.'''

    prefix = lemp.tokenprefix or ""

    _in = file_open(lemp, ".h", "rb")
    if _in:
        for index, line in enumerate(_in):
            i = index + 1
            if i >= lemp.nterminal:
                # No change in the file.  Don't rewrite it.
                _in.close()
                return
            pattern = "#define %s%-30s %2d\n" % (prefix, lemp.symbols[i].name, i)
            if line != pattern:
                # File changed.
                break
        _in.close()

    out = file_open(lemp, ".h", "wb")
    if out:
        for i in range(1, lemp.nterminal):
            fprintf(out, "#define %s%-30s %2d\n", prefix, lemp.symbols[i].name, i)
        out.close()

    return


def CompressTables(lemp):
    '''Reduce the size of the action tables, if possible, by making use
    of defaults.'''

    # In this version, we take the most frequent REDUCE action and
    # make it the default.  Except, there is no default if the
    # wildcard token is a possible look-ahead.

    for i in range(lemp.nstate):
        stp = lemp.sorted[i]
        nbest = 0
        rbest = None
        usesWildcard = False
        
        for ap in iterlinks(stp.ap):
            if ap.type == SHIFT and ap.sp == lemp.wildcard:
                usesWildcard = True

            if ap.type != REDUCE:
                continue

            rp = ap.x.rp
            if rp.lhsStart:
                continue

            if rp == rbest:
                continue

            n = 1
            for ap2 in iterlinks(ap.next):
                if ap2.type != REDUCE:
                    continue

                rp2 = ap2.x.rp
                if rp2 == rbest:
                    continue

                if rp2 == rp:
                    n += 1

            if n > nbest:
                nbest = n
                rbest = rp

        # Do not make a default if the number of rules to default is
        # not at least 1 or if the wildcard token is a possible
        # lookahead.
        if nbest < 1 or usesWildcard:
            continue

        # Combine matching REDUCE actions into a single default
        for ap in iterlinks(stp.ap):
            if ap.type == REDUCE and ap.x.rp == rbest:
                break
        assert ap
        ap.sp = Symbol_new("{default}")
        for ap in iterlinks(ap.next):
            if ap.type == REDUCE and ap.x.rp == rbest:
                ap.type = NOT_USED
        stp.ap = Action_sort(stp.ap)

    return


def stateResortCompare(a, b):
    '''Compare two states for sorting purposes.  The smaller state is
    the one with the most non-terminal actions.  If they have the same
    number of non-terminal actions, then the smaller is the one with
    the most token actions.
    '''
    n = b.nNtAct - a.nNtAct
    if n == 0:
        n = b.nTknAct - a.nTknAct
    return n


def ResortStates(lemp):
    '''Renumber and resort states so that states with fewer choices
    occur at the end.  Except, keep state 0 as the first state.
    '''

    for i in range(lemp.nstate):
        stp = lemp.sorted[i]
        stp.nTknAct = stp.nNtAct = 0
        stp.iDflt = lemp.nstate + lemp.nrule
        stp.iTknOfst = NO_OFFSET
        stp.iNtOfst = NO_OFFSET

        for ap in iterlinks(stp.ap):
            if compute_action(lemp, ap) >= 0:
                if ap.sp.index < lemp.nterminal:
                    stp.nTknAct += 1
                elif ap.sp.index < lemp.nsymbol:
                    stp.nNtAct += 1
                else:
                    stp.iDflt = compute_action(lemp, ap)

    lemp.sorted = ([lemp.sorted[0]] +
                   sorted(lemp.sorted[1:], cmp = stateResortCompare))

    for i in range(lemp.nstate):
        lemp.sorted[i].statenum = i

    return

