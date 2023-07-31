
import os
import argparse
import pyconll
from RC_Counts.CountStructure import Counter, Split

if __name__ == "__main__":

    """
    The program counts SRCs and ORCs in a given a parsed corpus of sentences.
    The corpus is loaded with pyconll. The program makes a split corpus
    since the entire corpus was too big to fit the memory of my machine.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-i', '--inputFile', required=True, type=str)
    parser.add_argument('-o', '--outFile', required=True, type=str)
    args = parser.parse_args()

    counter = Counter()
    if os.path.exists(args.outFile):
        counter.loadDict(args.outFile)
    else:
        for conll_str in Split().yield_splits(args.inputFile):
            conll = pyconll.load_from_string(conll_str)
            counter.count_conll(conll, out_file=args.outFile)
    counter.pretty_print()
