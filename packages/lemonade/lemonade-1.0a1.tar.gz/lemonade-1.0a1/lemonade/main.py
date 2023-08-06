'''
Main program file for the LEMON parser generator.
'''

from build import *
from option import *
from parse import *
from report import *
from struct import *

from ccruft import printf
from sys import stderr, exit


azDefine = []  # Names of the -D macros


# This routine is called with the argument to each -D command-line option.
# Add the macro defined to the azDefine array.

def handle_D_option(z):
    eq = z.find('=')
    if eq != -1:
        z = z[:eq]
    azDefine.append(z)
    return


def main(argv):
    '''The main program.  Parse the command line and do it...'''

    version = False
    rpflag = False
    basisflag = False
    compress = False
    quiet = False
    statistics = False
    mhflag = False

    options = (
        s_options(OPT_FLAG, "b", 'basisflag', "Print only the basis in report."),
        s_options(OPT_FLAG, "c", 'compress', "Don't compress the action table."),
        s_options(OPT_FSTR, "D", handle_D_option, "Define an %ifdef macro."),
        s_options(OPT_FLAG, "g", 'rpflag', "Print grammar without actions."),
        s_options(OPT_FLAG, "m", 'mhflag', "Output a makeheaders compatible file"),
        s_options(OPT_FLAG, "q", 'quiet', "(Quiet) Don't print the report file."),
        s_options(OPT_FLAG, "s", 'statistics', "Print parser stats to standard output."),
        s_options(OPT_FLAG, "x", 'version', "Print the version number."),
        )

    OptInit(argv, options, locals(), stderr)
    if version:
        printf("Lemon version 1.0\n")
        exit(0)

    if OptNArgs() != 1:
        fprintf(stderr, "Exactly one filename argument is required.\n")
        exit(1)

    lem = lemon(
        None,
        None,
        0, 0, 0, 0,
        None,
        0, # errorcnt
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        0, 0, 0, 0,
        None,
        )

    # Initialize the machine
    Strsafe_init()
    Symbol_init()
    State_init()
    lem.argv0 = argv[0]
    lem.filename = OptArg(0)
    lem.basisflag = basisflag
    Symbol_new("$")
    lem.errsym = Symbol_new("error")
    lem.errsym.useCnt = 0

    # Parse the input file
    Parse(lem)
    if lem.errorcnt:
        exit(lem.errorcnt)
    if lem.nrule == 0:
        fprintf(stderr, "Empty grammar.\n")
        exit(1)

    # Count and index the symbols of the grammar
    lem.nsymbol = Symbol_count()
    Symbol_new("{default}")
    lem.symbols = Symbol_arrayof()
    for i in range(lem.nsymbol + 1):
        lem.symbols[i].index = i
    lem.symbols.sort(cmp=Symbolcmpp)
    for i in range(lem.nsymbol + 1):
        lem.symbols[i].index = i
    i = 1
    while lem.symbols[i].name[0].isupper():
        i += 1
    lem.nterminal = i

    # Generate a reprint of the grammar, if requested on the command line
    if rpflag:
        Reprint(lem)
    else:
        # Initialize the size for all follow and first sets
        SetSize(lem.nterminal + 1)

        # Find the precedence for every production rule (that has one)
        FindRulePrecedences(lem)

        # Compute the lambda-nonterminals and the first-sets for every
        # nonterminal
        FindFirstSets(lem)

        # Compute all LR(0) states.  Also record follow-set
        # propagation links so that the follow-set can be computed
        # later
        lem.nstate = 0
        FindStates(lem)
        lem.sorted = State_arrayof()

        # Tie up loose ends on the propagation links
        FindLinks(lem)

        # Compute the follow set of every reducible configuration
        FindFollowSets(lem)

        # Compute the action tables
        FindActions(lem)

        # Compress the action tables
        if not compress:
            CompressTables(lem)

        # Reorder and renumber the states so that states with fewer
        # choices occur at the end.
        ResortStates(lem)

        # Generate a report of the parser generated.  (the "y.output" file)
        if not quiet:
            ReportOutput(lem)

        # Generate the source code for the parser
        ReportTable(lem, mhflag)

        # Produce a header file for use by the scanner.  (This step is
        # omitted if the "-m" option is used because makeheaders will
        # generate the file for us.)
        if not mhflag:
            ReportHeader(lem)


    if statistics:
        printf("Parser statistics: %d terminals, %d nonterminals, %d rules\n",
               lem.nterminal, lem.nsymbol - lem.nterminal, lem.nrule)
        printf("                   %d states, %d parser table entries, %d conflicts\n",
               lem.nstate, lem.tablesize, lem.nconflict)

    if lem.nconflict:
        fprintf(stderr, "%d parsing conflicts.\n", lem.nconflict)

    exit(lem.errorcnt + lem.nconflict)
    return lem.errorcnt + lem.nconflict

