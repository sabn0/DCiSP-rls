
# import packages
import pandas as pd
from abc import abstractmethod
import numpy as np
from MLE.MLE import LM
import Consts.Consts as Consts

"""
Base class to estimate the surprisal value of a token in a sequence based on its precesing context
"""
class NgramEstimator:

    estimators = {}

    def __init__(self, emissions_file=None, transitions_file=None):
        self.emissions_file = emissions_file
        self.transitions_file = transitions_file
        self.start_tok = Consts.START_TOK
        self.end_tok = Consts.END_TOK
        self.start_tag = Consts.START_TAG
        self.end_tag = Consts.END_TAG
        self.rare_tok = Consts.RARE_TOK
        self.epsilon = float('1e-20')
        self.index_mapping = Consts.INDEX_MAPPING
        self.emission_prob = None
        self.transition_prob = None
        self.all_tags = None

    @classmethod
    def register_estimator(cls, estimator_type):
        def decorator(estimator):
            cls.estimators[estimator_type] = estimator
            return estimator
        return decorator

    @classmethod
    def build(cls, estimator_type, emissions_file, transitions_file):
        if estimator_type not in cls.estimators:
            raise ValueError
        estimator = cls.estimators[estimator_type](emissions_file, transitions_file)
        return estimator

    @abstractmethod
    def get_transition_prob(self, prev_prev_tag: str, prev_tag: str, tag: str):
        pass

    @abstractmethod
    def calc_transitions_probs(self, transitions: dict, all_tags:list):
        pass

    @abstractmethod
    def calc_greedy(self, sentences_file: str, out_file: str):
        pass

    def get_emission_prob(self, tok: str, tag: str):
        # unknown words are replaced with RARE prob
        p = max(self.emission_prob.get(' '.join([tok, tag]), 0), self.emission_prob[' '.join([self.rare_tok, tag])])
        return p

    # computation of a probability of a POS + Form pair (Form given POS)
    # for all the possible pairs in the emissions file
    def calc_emission_probs(self, emissions: dict, transitions: dict):
        self.emission_prob = {}
        for item, count in emissions.items():
            if ' ' not in item: continue
            _, tag = item.rsplit(' ', 1)
            self.emission_prob[item] = count / transitions.get(tag, 0)
            assert 0 <= self.emission_prob[item] <= 1, [item, count]

        assert self.all_tags is not None
        for tag in self.all_tags:
            item = ' '.join([self.rare_tok, tag])
            self.emission_prob[item] = 1 / transitions.get(tag, 0)


    def calc_probabilities(self):

        assert self.emissions_file, "emissions_file not given"
        assert self.transitions_file, "transitions_file not given"

        # load emissions from file
        df_emissions = pd.read_csv(self.emissions_file, delimiter='\t', header=None)
        emissions = {k.strip(): v for k, v in zip(df_emissions[0], df_emissions[1])}

        # load transitions from file
        df_transitions = pd.read_csv(self.transitions_file, delimiter='\t', header=None)
        transitions = {k.strip(): v for k, v in zip(df_transitions[0], df_transitions[1])}

        # get probabilities
        self.all_tags = list(set([tag for tag in transitions if ' ' not in tag]))
        self.calc_emission_probs(emissions=emissions,transitions=transitions)
        self.calc_transitions_probs(transitions=transitions, all_tags=self.all_tags)
        return self

    # extract tokens, tags and introducer position from a Form / POS file
    def read_sequences(self, sentences_file: str, n: int):
        with open(sentences_file, 'r') as f:
            lines = f.read().splitlines()

        for i, line in enumerate(lines):

            rc_type, rel_i, text = line.strip().split('\t')
            rel_i = int(float(rel_i))
            if rel_i <= 0:
                continue

            tokens = n*[self.start_tok] + [item.split('/')[0] for item in text.split()] + n*[self.end_tok]
            tokens = [t for t in tokens if len(t) > 0]

            tags = n*[self.start_tag] + [item.split('/')[1] for item in text.split()] + n*[self.end_tag]
            tags = [t for t in tags if len(t) > 0]

            assert len(tokens) == len(tags)

            yield rc_type, rel_i, tokens, tags, int(i+1)


"""
A concrete implementation to calculate surprisal values for trigrams
The computation is greedy on the known next tag at each position
Sup(x, t) = -log ( p (t | t-1 , t-2) * p(x | t) )
The syntactic version only uses
Sup(_, t) = -log ( p (t | t-1 , t-2))
"""
@NgramEstimator.register_estimator(estimator_type='3')
class TrigramsEstimate(NgramEstimator):
    def __init__(self,  emissions_file: str, transitions_file: str, transitions_ngrams=3):
        super(TrigramsEstimate, self).__init__(emissions_file=emissions_file, transitions_file=transitions_file)
        self.transitions_ngrams = transitions_ngrams

    def get_transition_prob(self, prev_prev_tag: str, prev_tag: str, tag: str):
        # manually checked - lowest transition prob is 2.21e-10, set non-existence to 0.5 of that
        p = max(self.transition_prob.get(' '.join([prev_prev_tag, prev_tag, tag]).strip(), 0), 0.5 * 2.21e-10)
        return p

    """
    A computation of the p (t | t-1 , t-2) components:
    p (t | t-1 , t-2) = a * (#(t, t-1, t-2) / #(t-1, t-2)) + b * (#(t, t-1) / #(t-1)) + (1-a-b) * (#(t) / all)
    """
    def calc_transitions_probs(self, transitions: dict, all_tags:list):
        self.transition_prob = {}
        unigrams_count = sum([transitions[tag] for tag in all_tags])
        a, b = 0.7, 0.2
        for prev_prev_tag in all_tags:
            for prev_tag in all_tags:
                for tag in all_tags:
                    trigram = transitions.get(' '.join([prev_prev_tag, prev_tag, tag]), 0) / (transitions.get(' '.join([prev_prev_tag, prev_tag]), 0)+self.epsilon)
                    bigram = transitions.get(' '.join([prev_tag, tag]), 0) / (transitions.get(prev_tag, 0)+self.epsilon)
                    unigram = transitions.get(tag, 0) / unigrams_count
                    prob = a*trigram + b*bigram + (1-a-b)*unigram
                    assert 0 <= prob <= 1
                    self.transition_prob[' '.join([prev_prev_tag, prev_tag, tag])] = prob

    """
    Calculate surprisal values sequentially for each sentence in the input file, token by token starting
    with an empty string. saved to json df
    """
    def calc_greedy(self, sentences_file: str, out_file: str):

        if None in [self.emission_prob, self.transition_prob, self.all_tags]:
            raise AssertionError("load probabilities before calculation")

        shift = self.transitions_ngrams-1

        rows = []
        for rc_type, rel_i, tokens, tags, sen_enum in self.read_sequences(sentences_file, n=shift):

            # identify the rc structure beginning
            rc_start = int(rel_i) - 1 - 1 + shift
            rc_extension = max(list(self.index_mapping[rc_type].keys()))
            rc_range = range(rc_start, rc_start+rc_extension)

            # first item and second item are sure (SOS), start from shift's element
            syntactics, lexicals, both = [], [], []
            for index, (prev_prev_tag, prev_tag, tag, tok) in enumerate(zip(tags[:-shift], tags[1:-1], tags[shift:], tokens[shift:])):

                # word from sentences _ file
                lexical_prob = self.get_emission_prob(tok=tok, tag=tag)
                syntactic_prob = self.get_transition_prob(prev_prev_tag=prev_prev_tag, prev_tag=prev_tag, tag=tag)
                both += [lexical_prob * syntactic_prob]
                lexicals += [lexical_prob]
                syntactics += [syntactic_prob]

                # surprisal calc
                lexical_sup = -np.log2(lexical_prob).item()
                syntactic_sup = -np.log2(syntactic_prob).item()
                sup = -np.log2(both[-1]).item()

                struct_i = 1 + index - rc_start + shift if index + shift in rc_range else 0
                struct_i = self.index_mapping[rc_type][struct_i] if struct_i in self.index_mapping[rc_type] else 0

                rows += [
                    [
                        index+1, struct_i, tok, rc_type, sen_enum, lexical_sup, syntactic_sup, sup
                    ]
                ]

        # word index should be compatible with reaction time word indexes (rts start from 1)
        df = pd.DataFrame(data=rows, columns=Consts.COLUMNS_NGRAMS)
        _ = df.to_json(out_file, orient='table')


"""
Similar to the above but with n=2 over 3
"""
@NgramEstimator.register_estimator(estimator_type='2')
class BigramsEstimate(NgramEstimator):
    def __init__(self,  emissions_file: str, transitions_file: str, transitions_ngrams=2):
        super(BigramsEstimate, self).__init__(emissions_file=emissions_file, transitions_file=transitions_file)
        self.transitions_ngrams = transitions_ngrams

    def get_transition_prob(self, prev_prev_tag: str, prev_tag: str, tag: str):
        # manually checked - lowest transition prob is 2.21e-10, set non-existence to 0.5 of that
        p = max(self.transition_prob.get(' '.join([prev_tag, tag]).strip(), 0), 0.5 * 2.21e-10)
        return p

    def calc_transitions_probs(self, transitions: dict, all_tags:list):
        self.transition_prob = {}
        unigrams_count = sum([transitions[tag] for tag in all_tags])
        a = 0.9
        for prev_tag in all_tags:
            for tag in all_tags:
                bigram = transitions.get(' '.join([prev_tag, tag]), 0) / (transitions.get(prev_tag, 0)+self.epsilon)
                unigram = transitions.get(tag, 0) / unigrams_count
                prob = a*bigram + (1-a)*unigram
                assert 0 <= prob <= 1
                self.transition_prob[' '.join([prev_tag, tag])] = prob

    def calc_greedy(self, sentences_file: str, out_file: str):

        if None in [self.emission_prob, self.transition_prob, self.all_tags]:
            raise AssertionError("load probabilities before calculation")

        shift = self.transitions_ngrams-1

        rows = []
        for rc_type, rel_i, tokens, tags, sen_enum in self.read_sequences(sentences_file, n=shift):

            # identify the rc structure beginning
            rc_start = int(rel_i) - 1 - 1 + shift
            rc_extension = max(list(self.index_mapping[rc_type].keys()))
            rc_range = range(rc_start, rc_start+rc_extension)

            # first item and second item are sure (SOS), start from shift's element
            syntactics, lexicals, both = [], [], []
            for index, (prev_tag, tag, tok) in enumerate(zip(tags[:-shift], tags[shift:], tokens[shift:])):

                # word from sentences _ file
                lexical_prob = self.get_emission_prob(tok=tok, tag=tag)
                syntactic_prob = self.get_transition_prob(prev_prev_tag='', prev_tag=prev_tag, tag=tag)
                both += [lexical_prob * syntactic_prob]
                lexicals += [lexical_prob]
                syntactics += [syntactic_prob]

                # surprisal calc
                lexical_sup = -np.log2(np.product(lexicals[:index+1])).item()
                syntactic_sup = -np.log2(np.product(syntactics[:index+1])).item()
                sup = -np.log2(np.product(both[:index+1])).item()

                struct_i = 1+index-rc_start+shift if index+shift in rc_range else 0
                struct_i = self.index_mapping[rc_type][struct_i] if struct_i in self.index_mapping[rc_type] else 0

                rows += [
                    [
                        index+1, struct_i, tok, rc_type, sen_enum, lexical_sup, syntactic_sup, sup
                    ]
                ]

        # word index should be compatible with reaction time word indexes (rts start from 1)
        df = pd.DataFrame(data=rows, columns=Consts.COLUMNS_NGRAMS)
        _ = df.to_json(out_file, orient='table')


"""
An implementation for the outputs of a language model, that produces a "probability" for the next
item in the sequence based on context. computed as -log (p (x)).
If x is encoded by LM as more than one token, the probs are averaged.
"""
@NgramEstimator.register_estimator(estimator_type='1')
class LMEstimate(NgramEstimator):
    def __init__(self, emissions_file: str, transitions_file: str, transitions_ngrams=1):
        super(LMEstimate, self).__init__(emissions_file=emissions_file, transitions_file=transitions_file)
        self.lm = LM()

    def get_transition_prob(self, prev_prev_tag: str, prev_tag: str, tag: str):
        pass

    def calc_transitions_probs(self, transitions: dict, all_tags:list):
        pass

    # overrides
    def calc_probabilities(self):
        return self

    def calc_emission_probs(self, emissions: dict, transitions: dict):
        pass

    def get_emission_prob(self, tok: str, tag: str):
        pass

    def calc_greedy(self, sentences_file: str, out_file: str):

        rows = []
        for rc_type, rel_i, tokens, __, sen_enum in self.read_sequences(sentences_file, n=0):

            # sentence reconstruction increment
            sentence = ''

            # iterate over the whole sentence and generate word by word
            for index, tok in enumerate(tokens):

                # get output model increment , # probs of shape (N, vocab_size), target_ids of shape (M)
                target_ids, probs = self.lm.prepare(sentence, tok)
                target_probs = [probs[i][t].item() for i, t in enumerate(target_ids.tolist())]

                # calc sup
                target_sup = np.mean([-np.log2(p) for p in target_probs])

                struct_i = self.index_mapping[rc_type][index+1] if (index+1) in self.index_mapping[rc_type] else 0

                rows += [
                    [
                        index+1, struct_i, tok, rc_type, sen_enum, target_sup
                    ]
                ]

                # add target to sentence
                sentence = ' '.join([sentence, tok]).strip()

        df = pd.DataFrame(data=rows, columns=Consts.COLUMNS_LM)
        _ = df.to_json(out_file, orient='table')