

from MLE.MLE import MLE, LM, Ngrams
from MLE.Estimate import NgramEstimator, TrigramsEstimate, BigramsEstimate, LMEstimate

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-m', '--MLE', required=True, type=str, help='support of Ngrams or LM')
    parser.add_argument('-n', '--Ngrams', required=True, type=int, help='support of bigrams and trigrams, or LM')
    parser.add_argument('-s', '--SentencesFile', required=True, help='file form sen_type\trel_i\tform/pos')
    parser.add_argument('-o', '--OutFile', required=True, type=str, help='Name of output file to save df')

    parser.add_argument('-c', '--Corpus', default=None, type=str, help='path to corpus of Hebrew conll')
    parser.add_argument('-q', '--TransitionsFile', default=None, type=str, help='transitions out name')
    parser.add_argument('-e', '--EmissionsFile', default=None, type=str, help='emissions out name')
    args = parser.parse_args()

    assert 3 >= args.Ngrams >= 1, "transitions should be for trigrams or bigrams, LM is 1"
    assert args.MLE in ['LM', 'Ngrams'], "unknown MLE type"
    assert args.OutFile.endswith('.json'), "ouput must be a json file"

    # create e.mle, q.mle files with counts
    mle_args = [args.Ngrams, args.TransitionsFile, args.EmissionsFile, args.Corpus]
    mle = MLE.build(args.MLE, *mle_args).make()

    # estimate MLE probs from counts
    estimator = NgramEstimator.build(str(args.Ngrams), emissions_file=args.EmissionsFile, transitions_file=args.TransitionsFile)
    estimator.calc_probabilities().calc_greedy(sentences_file=args.SentencesFile, out_file=args.OutFile)
