
# import packages
from transformers import AutoTokenizer, AutoModelForCausalLM
from sklearn.feature_extraction.text import CountVectorizer
from RC_Counts.CountStructure import Split
from abc import abstractmethod
import pyconll
import torch
import Consts.Consts as Consts

"""
A base class to count ngrams in a corpus, given a file with sentences.
The outputs are q.mle and e.mle files
"""
class MLE:

    mles = {}
    def __init__(self, transitions_n_grams=None, transitions_out_file=None, emissions_out_file=None, corpus_file=None):
        pass

    @classmethod
    def register_mle(cls, mle_type):
        def decorator(mle):
            cls.mles[mle_type] = mle
            return mle
        return decorator

    @classmethod
    def build(cls, mle_type, *args):
        if mle_type not in cls.mles:
            raise ValueError
        mle = cls.mles[mle_type](*args)
        return mle

    @abstractmethod
    def make(self):
        pass


"""
an explicit implementation to count emissions and transitions in a file of sentences
The file is a conll format that will be processed to a Form / POS format for each token.
"""
@MLE.register_mle(mle_type='Ngrams')
class Ngrams:
    def __init__(
        self,
        transitions_n_grams: int,
        transitions_out_file: str,
        emissions_out_file: str,
        corpus_file: str
    ):

        self.transitions_min_df = 1
        self.emissions_min_df = 2
        self.transitions_n_grams = transitions_n_grams  # either 2 or 3 here, bigrams or trigrams
        self.transitions_out_file = transitions_out_file
        self.emissions_out_file = emissions_out_file
        self.start_tok = Consts.START_TOK
        self.end_tok = Consts.END_TOK
        self.start_tag = Consts.START_TAG
        self.end_tag = Consts.END_TAG
        self.corpus = self.build_corpus(corpus_file)

    def build_corpus(self, corpus_file: str) -> list:
        corpus = []
        for conll_str in Split().yield_splits(corpus_file):
            corpus += [' '.join(['/'.join([t.form, t.upos]) for t in sentence._tokens]) for sentence in pyconll.load_from_string(conll_str)]
        return list(set(corpus))

    def save_dict_to_file(self, _d_: dict, out_file: str) -> None:
        with open(out_file, 'w+') as f:
            for k, v in _d_.items():
                f.write("{}\t{}\n".format(k, v))

    def custom_preprocess(self, sentence: str) -> str:
        start_tup = '/'.join([self.start_tok, self.start_tag])
        end_tup = '/'.join([self.end_tok, self.end_tag])
        sentence = ' '.join([start_tup, start_tup, sentence, end_tup, end_tup])
        return sentence

    def only_tags(self, txt):
        txt = self.custom_preprocess(txt)
        return ' '.join(w.rsplit('/', 1)[1] for w in txt.split())

    def make(self):
        self.make_transitions().make_emissions()

    # counts the occurrences of POS ngrams in the corpus
    def make_transitions(self):
        vec = CountVectorizer(lowercase=False,
                              ngram_range=(1, self.transitions_n_grams),
                              min_df=self.transitions_min_df,
                              preprocessor=self.only_tags,
                              token_pattern=r"\S+")
        values = vec.fit_transform(self.corpus).sum(axis=0).A1
        names = vec.get_feature_names_out()
        self.save_dict_to_file(_d_=dict(zip(names, values)), out_file=self.transitions_out_file)
        return self

    # counts the occurrences of Form / POS uniquely in the corpus
    def make_emissions(self):
        vec = CountVectorizer(lowercase=False,
                              ngram_range=(1,1),
                              preprocessor=self.custom_preprocess,
                              token_pattern=r"\S+",
                              min_df=self.emissions_min_df)
        values = vec.fit_transform(self.corpus).sum(axis=0).A1
        names = vec.get_feature_names_out()
        names = [s.replace('/', ' ') for s in names]
        d = dict(zip(names, values))
        self.save_dict_to_file(_d_=d, out_file=self.emissions_out_file)
        return self


"""
an implementation that is under the Ngrams based but in fact uses a pretrained language model
provides probabilities for the next item given a prefix of a sequence of tokens.  
"""
@MLE.register_mle(mle_type='LM')
class LM(MLE):
    def __init__(self, transitions_n_grams=None, transitions_out_file=None, emissions_out_file=None, corpus_file=None):
        super(LM, self).__init__()

        model_str = "Norod78/hebrew-gpt_neo-small"
        self.tokenizer = AutoTokenizer.from_pretrained(model_str)
        self.model = AutoModelForCausalLM.from_pretrained(model_str, return_dict_in_generate=True, pad_token_id=self.tokenizer.eos_token_id)
        self.model.eval()

        # model parameters
        self.sample_output_num = 1
        self.max_len_add = 10
        self.basic_max_len = 5
        self.vocab_size = self.model.config.vocab_size

    def make(self):
        pass

    def prepare(self, sentence: str, target: str):

        if len(sentence) == 0:
            encoded_input = None
            max_len = self.basic_max_len
        else:
            encoded_input = self.tokenizer.encode(sentence, add_special_tokens=False, return_tensors="pt")
            max_len = self.max_len_add + len(encoded_input[0])

        target_ids = self.tokenizer.encode(target, add_special_tokens=False, return_tensors="pt") # can be more than one

        # get sequential outputs
        sample_outputs = self.model.generate(
            encoded_input,
            max_length=max_len,
            do_sample=True,
            num_return_sequences=self.sample_output_num,
            output_scores=True,
            top_k=self.vocab_size
        )

        # get probabilities
        # -> shape [sample_output_num, max_len, vocab_size]
        probs = torch.stack(sample_outputs.scores, dim=1).softmax(-1)
        assert probs.shape[0] == 1 and target_ids.shape[0] == 1
        probs = probs[0]
        target_ids = target_ids[0]

        # probs if of shape (max_len, vocab_size), target_ids is of shape (max_len)
        # will be used to extract the probabilities of the targets.
        return target_ids, probs


