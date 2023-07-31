
# import packages
from abc import abstractmethod
import pandas as pd
from scipy import stats
import Consts.Consts as Consts

# a Base class for outliers, implementations will be a type of outlier rejection criteria
class OutliersBase:
    rejections = {}
    def __init__(self, df: pd.DataFrame, to_reject: list):

        # by initialization reject participants that should not be included in any analysis
        self.df = df[~df[Consts.SUBJECTNUMBER].isin(to_reject)]
        self.criterion_name = 'Base'

    # I use the decorator design pattern to allow creating instances of all outliers
    # types without having to explicitly write the string of type on action
    @classmethod
    def register_rejection(cls, rejection_type):
        def decorator(rejection):
            cls.rejections[rejection_type] = rejection
            return rejection
        return decorator

    @classmethod
    def build(cls, rejection_type, df, to_reject):
        if rejection_type not in cls.rejections:
            raise ValueError
        rejection = cls.rejections[rejection_type](df, to_reject)
        return rejection

    # return self to allow chaining outliers
    @abstractmethod
    def reject(self):
        pass

    @abstractmethod
    def set_criterion_name(self):
        pass

    def get_op(self, left, right, op):
        import operator
        if op == '==':
            return operator.eq(left, right)
        elif op == '!=':
            return operator.ne(left, right)
        else:
            raise ValueError

    def slice(self, column: str, value: str):
        df = self.get_df()
        df = df[df[column] == value]
        self.set_df(df)
        return self

    def slice_on_rts(self) -> pd.DataFrame:
        df = self.get_df()
        if Consts.WORDINDEX not in df.columns or Consts.WORDREACTIONTIME not in df.columns:
            return df
        df = df[df[Consts.WORDINDEX] != '-']
        df.loc[:, Consts.WORDREACTIONTIME] = pd.to_numeric(df[Consts.WORDREACTIONTIME])
        return df

    def slice_on_questions(self, keep_fillers=False) -> pd.DataFrame:
        df = self.get_df()
        df = df[df[Consts.QUESTIONANSWER] != '-']
        if not keep_fillers:
            df = df[df[Consts.SENTENCETYPE] != Consts.FILLER]
        return df

    def slice_on_fillers(self, sign='==') -> pd.DataFrame:
        df = self.slice_on_rts()
        df = df[self.get_op(df[Consts.SENTENCETYPE], Consts.FILLER, sign)]
        df[[Consts.WORDREACTIONTIME]] = df[[Consts.WORDREACTIONTIME]].apply(pd.to_numeric)
        return df

    def slice_on_main_verb(self, orc_index=4, src_index=5, sign='==') -> pd.DataFrame:
        df = self.slice_on_rts()
        df = df[(df[Consts.SENTENCETYPE] == Consts.ORC) & (self.get_op(df[Consts.WORDINDEX], orc_index, sign)) |
                (df[Consts.SENTENCETYPE] == Consts.SRC) & (self.get_op(df[Consts.WORDINDEX], src_index, sign))]
        df[[Consts.WORDREACTIONTIME]] = df[[Consts.WORDREACTIONTIME]].apply(pd.to_numeric)
        return df

    def get_criterion_name(self) -> str:
        return self.criterion_name

    def set_df(self, df:pd.DataFrame) -> None:
        self.df = df

    def get_df(self) -> pd.DataFrame:
        return self.df

    def slice_rejected(self, df:pd.DataFrame) -> None:
        df = df[~df[self.get_criterion_name()]]
        self.set_df(df)

    def mark(self, main_df: pd.DataFrame, indexes: list, value:bool) -> pd.DataFrame:
        for i in indexes:
            main_df.loc[i, self.get_criterion_name()] = value
        return main_df

    def correct_length(self):

        self.set_df(self.get_df().assign(LengthAdjustedReactionTime=0))
        self.criterion_name = self.get_df().columns[-1]

        df = self.slice_on_main_verb()
        df[[Consts.WORDLENGTH]] = df[[Consts.WORDLENGTH]].apply(pd.to_numeric)

        # calculate regression per word_length
        slope, intercept, _, __, ___ = stats.linregress(df[Consts.WORDLENGTH], df[Consts.WORDREACTIONTIME])
        df[self.criterion_name] = df[Consts.WORDREACTIONTIME] - (slope * (df[Consts.WORDLENGTH] - 0) + intercept)
        return df

