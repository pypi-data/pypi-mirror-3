

from ccruft import fprintf, struct


(
    OPT_FLAG,  OPT_INT,  OPT_DBL,  OPT_STR,
    OPT_FFLAG, OPT_FINT, OPT_FDBL, OPT_FSTR
    ) = range(1, 9)

s_options = struct(
    's_options',
    (
        'type',
        'label',
        'arg',
        'message',
        )
    )


argv = None
op = None
errstream = None


def ISOPT(X):
    if len(X) == 0:
        return False
    return X[0] == '-' or X[0] == '+' or X.find('=') != -1


def errline(n, k, err):
    ''' Print the command line with a carrot pointing to the k-th character
    of the n-th field.'''

    if argv[0]:
        fprintf(err, "%s", argv[0])

    spcnt = len(argv[0]) + 1
    i = 1
    while i < n and argv[i]:
        fprintf(err, " %s", argv[i])
        spcnt += len(argv[i]) + 1
        i += 1

    spcnt += k
    while argv[i]:
        fprintf(err, " %s", argv[i])
        i += 1

    if spcnt < 20:
        fprintf(err, "\n%*s^-- here\n", spcnt, "")
    else:
        fprintf(err, "\n%*shere --^\n", spcnt - 7, "")

    return


def argindex(n):
    '''Return the index of the N-th non-switch argument.  Return -1
    if N is out of range.'''

    dashdash = False
    if argv and argv[0]:
        i = 1
        while argv[i]:
            if dashdash or not ISOPT(argv[i]):
                if n == 0:
                    return i
                n -= 1
            if argv[i] == "--":
                dashdash = True
            i += 1

    return -1


emsg = "Command line syntax error: "

def handleflags(i, flags, err):
    '''Process a flag command line argument.'''

    errcnt = 0
    for o in op:
        if argv[i][1:].startswith(o.label):
            break
    else:
        if err:
            fprintf(err, "%sundefined option.\n", emsg)
            errline(i, 1, err)
        errcnt += 1
        return errcnt

    v = (argv[i][0] == '-')
    if o.type == OPT_FLAG:
        flags[o.arg] = v
    elif o.type == OPT_FFLAG:
        o.arg(v)
    elif o.type == OPT_FSTR:
        o.arg(argv[i][2:])
    else:
        if err:
            fprintf(err, "%smissing argument on switch.\n", emsg)
            errline(i, 1, err)
        errcnt += 1

    return errcnt


def handleswitch(i, flags, err):
    '''Process a command line switch which has an argument.'''

    lv = 0
    dv = 0.0
    sv = None
    errcnt = 0

    cp = argv[i].find('=')
    assert cp != -1
    lhs = argv[i][:cp]
    rhs = argv[i][cp+1:]
    for o in op:
        if lhs == o.label:
            break
    else:
        if err:
            fprintf(err, "%sundefined option.\n", emsg)
            errline(i, 0, err)
        errcnt += 1
        return errcnt

    if o.type in (OPT_FLAG, OPT_FFLAG):
        if err:
            fprintf(err, "%soption requires an argument.\n", emsg)
            errline(i, 0, err)
        errcnt += 1

    elif o.type in (OPT_DBL, OPT_FDBL):
        try:
            dv = float(rhs)
        except ValueError:
            if err:
                fprintf(err, "%sillegal character in floating-point argument.\n", emsg)
                errline(i, 0, err)
            errcnt += 1

    elif o.type in (OPT_INT, OPT_FINT):
        try:
            lv = int(rhs)
        except ValueError:
            if err:
                fprintf(err, "%sillegal character in integer argument.\n", emsg)
                errline(i, 0, err)
            errcnt += 1

    elif o.type in (OPT_STR, OPT_FSTR):
        sv = rhs


    if o.type in (OPT_FLAG, OPT_FFLAG):
        pass

    elif o.type == OPT_DBL:
        flags[o.arg] = dv

    elif o.type == OPT_FDBL:
        o.arg(dv)

    elif o.type == OPT_INT:
        flags[o.arg] = lv

    elif o.type == OPT_FINT:
        o.arg(lv)

    elif o.type == OPT_STR:
        flags[o.arg] = sv

    elif o.type == OPT_FSTR:
        o.arg(sv)

    return errcnt


def OptInit(a, o, flags, err):
    global argv, op, errstream
    from sys import exit

    errcnt = 0
    argv = a
    op = o
    errstream = err

    if argv and argv[0] and op:
        i = 1
        for i, arg in enumerate(argv):
            if arg[0] == '+' or arg[0] == '-':
                errcnt += handleflags(i, flags, err)
            elif arg.find('=') != -1:
                errcnt += handleswitch(i, flags, err)

    if errcnt > 0:
        fprintf(err, 'Valid command line options for "%s" are:\n', a[0])
        OptPrint()
        exit(1)

    return 0


def OptNArgs():
    cnt = 0
    dashdash = False
    if argv and argv[0]:
        for arg in argv[1:]:
            if dashdash or not ISOPT(arg):
                cnt += 1
            if arg == "--":
                dashdash = True
    return cnt


def OptArg(n):
    i = argindex(n)
    return argv[i] if i >= 0 else None


def OptErr(n):
    i = argindex(n)
    if i >= 0:
        errline(i, 0, errstream)
    return


def OptPrint():
    max = 0

    for o in op:
        l = len(o.label) + 1

        if o.type in (OPT_FLAG, OPT_FFLAG):
            pass

        elif o.type in (OPT_INT, OPT_FINT):
            l += len("<integer>")

        elif o.type in (OPT_DBL, OPT_FDBL):
            l += len("<real>")

        elif o.type in (OPT_STR, OPT_FSTR):
            l += len("<string>")

        if l > max:
            max = l


    for o in op:
        if o.type in (OPT_FLAG, OPT_FFLAG):
            fprintf(errstream, "  -%-*s  %s\n",
                    max, o.label, o.message)

        elif o.type in (OPT_INT, OPT_FINT):
            fprintf(errstream, "  %s=<integer>%*s  %s\n",
                    o.label, (max - len(o.label)) - 9, "", o.message)

        elif o.type in (OPT_DBL, OPT_FDBL):
            fprintf(errstream, "  %s=<real>%*s  %s\n",
                    o.label, (max - len(o.label)) - 6, "", o.message)

        elif o.type in (OPT_STR, OPT_FSTR):
            fprintf(errstream, "  %s=<string>%*s  %s\n",
                    o.label, (max - len(o.label)) - 8, "", o.message)

    return

