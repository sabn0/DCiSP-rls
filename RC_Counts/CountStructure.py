

# import packages
import pyconll
import os
from collections import defaultdict
from abc import abstractmethod
import Consts.Consts as Consts


class PositionalRule:
    def __init__(self, sentence, rel_i):
        self.sentence = sentence
        self.rel_i = rel_i

    @abstractmethod
    def rule(self) -> bool:
        pass


class RC_Rules:
    def __init__(self, sentence: pyconll.unit.sentence.Sentence, rel_i: int):
        self.sentence = sentence
        self.rel_i = rel_i

    @abstractmethod
    def rule_base(self) -> bool:
        pass

    class RC_rule(PositionalRule):
        def __init__(self, sentence, rel_i):
            super().__init__(sentence, rel_i)

        @abstractmethod
        def rule(self) -> bool:
            pass


class SRC_Rule(RC_Rules):
    def __init__(self, sentence: pyconll.unit.sentence.Sentence, rel_i: int):
        super(SRC_Rule, self).__init__(sentence, rel_i)
        self.beginning_rule = self.BeginningRule(sentence, rel_i)
        self.embedded_rule = self.EmbeddedRule(sentence, rel_i)
        self.full_rule = self.FullRule(sentence, rel_i, self)

    # deafult length of an SRC, most start 2 token before introducer and have some space after
    def rule_base(self) -> bool:
        return (len(self.sentence) - 7) >= self.rel_i >= 2

    class FullRule(RC_Rules.RC_rule):
        def __init__(self, sentence, rel_i, outer):
            super().__init__(sentence, rel_i)
            self.name = Consts.SRC_FULL
            self.as_outer = outer

        def rule(self) -> bool:
            return all([
                self.as_outer.beginning_rule.rule(),
                self.as_outer.embedded_rule.rule(),
                self.sentence[self.rel_i + 5].xpos == 'VB'
            ])

    class BeginningRule(RC_Rules.RC_rule):
        def __init__(self, sentence, rel_i):
            super().__init__(sentence, rel_i)
            self.name = Consts.SRC_BEGINNING

        # checking for forms, tags and dep relations in the conll sentence that match an SRC beginning
        def rule(self) -> bool:
            return all([
                self.sentence[self.rel_i - 2].upos == 'DEF',
                self.sentence[self.rel_i - 2].head == self.sentence[self.rel_i - 1].id,
                self.sentence[self.rel_i - 2].deprel == 'def',
                self.sentence[self.rel_i - 1].upos == 'NN',
                self.sentence[self.rel_i].head == self.sentence[self.rel_i - 1].id,
                self.sentence[self.rel_i].deprel == 'rcmod',
                self.sentence[self.rel_i].xpos == 'REL-SUBCONJ',
                self.sentence[self.rel_i + 1].upos == 'VB',
                self.sentence[self.rel_i + 1].head == self.sentence[self.rel_i].id,
                self.sentence[self.rel_i + 1].deprel == 'relcomp',
            ])

    class EmbeddedRule(RC_Rules.RC_rule):
        def __init__(self, sentence, rel_i):
            super().__init__(sentence, rel_i)
            self.name = Consts.SRC_EMBEDDED

        # checking for forms, tags and dep relations in the conll sentence that match an SRC embedded
        def rule(self) -> bool:
            return all([
                self.sentence[self.rel_i].xpos == 'REL-SUBCONJ',
                self.sentence[self.rel_i + 1].upos == 'VB',
                self.sentence[self.rel_i + 1].head == self.sentence[self.rel_i].id,
                self.sentence[self.rel_i + 1].deprel == 'relcomp',
                self.sentence[self.rel_i + 2].upos == 'ACC',
                self.sentence[self.rel_i + 2].head == self.sentence[self.rel_i + 1].id,
                self.sentence[self.rel_i + 2].deprel == 'obj',
                self.sentence[self.rel_i + 3].upos == 'DEF',
                self.sentence[self.rel_i + 3].head == self.sentence[self.rel_i + 4].id,
                self.sentence[self.rel_i + 3].deprel == 'def',
                self.sentence[self.rel_i + 4].upos == 'NN',
                self.sentence[self.rel_i + 4].head == self.sentence[self.rel_i + 2].id,
                self.sentence[self.rel_i + 4].deprel == 'hd'
            ])


class ORC_Rule(RC_Rules):
    def __init__(self, sentence: pyconll.unit.sentence.Sentence, rel_i: int):
        super(ORC_Rule, self).__init__(sentence, rel_i)
        self.beginning_rule = self.BeginningRule(sentence, rel_i)
        self.embedded_rule = self.EmbeddedRule(sentence, rel_i)
        self.full_rule = self.FullRule(sentence, rel_i, self)

    # deafult length of an SRC, most start 2 token before introducer and have some space after
    def rule_base(self) -> bool:
        return (len(self.sentence) - 6) >= self.rel_i >= 2

    class FullRule(RC_Rules.RC_rule):
        def __init__(self, sentence, rel_i, outer):
            super().__init__(sentence, rel_i)
            self.name = Consts.ORC_FULL
            self.as_outer = outer

        def rule(self) -> bool:
            return all([
                self.as_outer.beginning_rule.rule(),
                self.as_outer.embedded_rule.rule(),
                self.sentence[self.rel_i + 4].xpos == 'VB'
            ])

    class BeginningRule(RC_Rules.RC_rule):
        def __init__(self, sentence, rel_i):
            super().__init__(sentence, rel_i)
            self.name = Consts.ORC_BEGINNING

        # checking for forms, tags and dep relations in the conll sentence that match an ORC beginning
        def rule(self) -> bool:
            return all([
                self.sentence[self.rel_i - 2].upos == 'DEF',
                self.sentence[self.rel_i - 2].head == self.sentence[self.rel_i - 1].id,
                self.sentence[self.rel_i - 2].deprel == 'def',
                self.sentence[self.rel_i - 1].upos == 'NN',
                self.sentence[self.rel_i].head == self.sentence[self.rel_i - 1].id,
                self.sentence[self.rel_i].deprel == 'rcmod',
                self.sentence[self.rel_i].xpos == 'REL-SUBCONJ',
                self.sentence[self.rel_i + 1].upos == 'DEF',
                self.sentence[self.rel_i + 1].head == self.sentence[self.rel_i + 2].id,
                self.sentence[self.rel_i + 1].deprel == 'def',
                self.sentence[self.rel_i + 2].upos == 'NN'
            ])

    class EmbeddedRule(RC_Rules.RC_rule):
        def __init__(self, sentence, rel_i):
            super().__init__(sentence, rel_i)
            self.name = Consts.ORC_EMBEDDED

        # checking for forms, tags and dep relations in the conll sentence that match an ORC embedded
        def rule(self) -> bool:
            return all([
                self.sentence[self.rel_i].xpos == 'REL-SUBCONJ',
                self.sentence[self.rel_i + 1].upos == 'DEF',
                self.sentence[self.rel_i + 1].head == self.sentence[self.rel_i + 2].id,
                self.sentence[self.rel_i + 1].deprel == 'def',
                self.sentence[self.rel_i + 2].upos == 'NN',
                self.sentence[self.rel_i + 2].head == self.sentence[self.rel_i + 3].id,
                self.sentence[self.rel_i + 2].deprel == 'subj',
                self.sentence[self.rel_i + 3].upos == 'VB',
                self.sentence[self.rel_i + 3].head == self.sentence[self.rel_i].id,
                self.sentence[self.rel_i + 3].deprel == 'relcomp'
            ])


class Counter:
    def __init__(self):
        self.total_counts = defaultdict(lambda : 0)

    def findRcIntroducer(self, conll: pyconll.unit.conll.Conll, out_file: str) -> defaultdict:
        """
        given a conll, find all relative clause
        complement's that introduce RC ( shin ), in all sentences.
        :param conll: conll loaded from file, with sentences
        :return: dict with counts, and the actual sentences
        """

        counter = defaultdict(lambda : 0)

        def write_func(sentence, out_name, t='', rel_pos=None):
            text_and_pos = []
            count_skips = 0
            for i, token in enumerate(sentence._tokens):
                text, pos = token.form, token.upos
                if text.startswith('*') and text.endswith('*'):
                    if rel_pos is not None and rel_i > i:
                        count_skips += 1
                    continue
                item = '/'.join([text, pos])
                text_and_pos += [item]
            if count_skips > 0:
                rel_pos -= count_skips
            text_and_pos = ' '.join(text_and_pos)
            prefix = '{}\t'.format(t) if len(t) > 0 else ''
            prefix = '{}{}\t'.format(prefix, str(rel_pos)) if prefix != '' else prefix
            write_str = "{}{}".format(prefix, text_and_pos)
            write_str = write_str.strip()
            with open(out_name, 'a+') as f:
                f.write("{}\n".format(write_str))

        rel_rule = lambda token: token.xpos in ['REL', 'REL-SUBCONJ'] and token.deprel == 'rcmod'
        head_rule = lambda token, id2index: token.head in id2index and id2index[token.id] > 1 and token.head != '0'

        for j, sentence in enumerate(conll):

            counter[Consts.SENTENCE] += 1

            for rel_i, token in enumerate(sentence._tokens):

                # find a relativizer position, that his head is not the root
                if not rel_rule(token) or not head_rule(token, sentence._ids_to_indexes):
                    continue
                counter[Consts.RC] += 1

                # go over rc rules
                rc_rules = [SRC_Rule(sentence, rel_i), ORC_Rule(sentence, rel_i)]
                for rc_rule in rc_rules:

                    if not rc_rule.rule_base():
                        continue

                    pos_rules = [rc_rule.beginning_rule, rc_rule.embedded_rule, rc_rule.full_rule]
                    for pos_rule in pos_rules:

                        if pos_rule.rule():
                            counter[pos_rule.name] += 1
                            write_func(sentence=sentence, out_name=out_file, t=pos_rule.name, rel_pos=rel_i)

        return counter

    def loadDict(self, file_name: str):
        with open(file_name, 'r') as f:
            lines = f.read().splitlines()
        for line in lines:
            rc = line.split('\t')[0]
            self.total_counts[rc] += 1

    def addDicts(self, x: defaultdict):
        """
        merge two dicts and sum values
        :param x: dict
        :param y: dict
        :return: a summarized dict
        """
        keys = list(set(list(x.keys()) + list(self.total_counts.keys())))
        z = {k: x.get(k, 0) + self.total_counts.get(k, 0) for k in keys}
        self.total_counts = z

    def count_conll(self, conll: pyconll.unit.conll.Conll, out_file: str):

        # updated counts of rc
        counting_dict = self.findRcIntroducer(conll, out_file=out_file)
        self.addDicts(counting_dict)

        # sort dict
        self.total_counts = {k: v for k, v in sorted(self.total_counts.items(), key=lambda item: item[1])}

    def run_from_files(self, corpus_dir: str, out_file: str):

        # iterate over conll files
        corpus_files = os.listdir(corpus_dir)
        for i, corpus_file in enumerate(corpus_files):

            # load file to conll format
            file_path = os.path.join(corpus_dir, corpus_file)
            conll = pyconll.load_from_file(file_path)
            # count rcs in the conll
            self.count_conll(conll, out_file=out_file)

    def pretty_print(self):
        for k, v in self.total_counts.items():
            print("{} : {}".format(k, v))


class Split:
    def __init__(self):
        pass

    # splits a file of conll to N files
    def yield_splits(self, file_name: str) -> str:

        # create splits from data
        count_lines = total_sentences = 0
        output_string = ""
        with open(file_name) as f:
            for line in f:

                # add data line to output string
                line = line.rstrip()
                output_string += line + '\n'
                count_lines += 1

                if len(line) == 0:

                    if count_lines > 0 and 1e06 / count_lines <= 1.0:

                        yield output_string
                        output_string = ""
                        count_lines = 0

                    total_sentences += 1

        if len(output_string) > 0:
            yield output_string


    # unused when loading conll's from strings
    def save_splits(self, file_name: str, out_dir: str) -> None:

        # create output dir is not exists
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        for count_files, output_string in self.yield_splits(file_name):

            # write to file
            out_name = '{0}/{1}.txt'.format(out_dir, count_files)
            with open(out_name, 'w+') as f:
                f.write("{}".format(output_string))





