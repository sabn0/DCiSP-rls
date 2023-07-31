
import argparse
import pandas as pd
from abc import abstractmethod
import Consts.Consts as Consts


class Merge:

    mergers = {}

    def __init__(self):
        pass

    @classmethod
    def register_merger(cls, merge_type):
        def decorator(merger):
            cls.mergers[merge_type] = merger
            return merger
        return decorator

    @classmethod
    def build(cls, merge_type):
        if merge_type not in cls.mergers:
            raise ValueError
        merger = cls.mergers[merge_type]()
        return merger

    def load_df(self, df: str) -> pd.DataFrame:
        return pd.read_json(df, orient='table')

    def save_df(self, df: pd.DataFrame, out_file: str):
        assert out_file.endswith('.json')
        _ = df.to_json(out_file, orient='table')

    @abstractmethod
    def merge(self, df1: str, df2: str, out_file: str) -> None:
        pass


@Merge.register_merger(merge_type='WM')
class RTtoWM(Merge):
    def __init__(self):
        super(RTtoWM, self).__init__()
        # df1 is spr, df2 is WM

    def merge(self, df1: str, df2: str, out_file: str) -> None:

        df1 = self.load_df(df1)
        df2 = self.load_df(df2)
        # wm df has [SubjectNumber, Group, Session, WMResult, Script]

        # convert df2 session values for compliance
        df2[Consts.SESSION] = df2[Consts.SESSION].replace(['Start'], 'Before')
        df2[Consts.SESSION] = df2[Consts.SESSION].replace(['End'], 'After')

        df = df1.merge(df2, on=[Consts.SUBJECTNUMBER, Consts.SESSION, Consts.GROUP, Consts.TOEXCLUDE], how='outer').fillna('-')

        # check that there are not empty cells without need
        empty = df[df[Consts.WMRESULT] == '-'].values.tolist()
        assert len(empty) == 0, len(empty)

        # save to file
        self.save_df(df, out_file)


@Merge.register_merger(merge_type='SUP')
class RTtoSup(Merge):
    def __init__(self):
        super(RTtoSup, self).__init__()
        # df1 is spr, df2 is sup

    def merge(self, df1: str, df2: str, out_file: str) -> None:

        df1 = self.load_df(df1)
        df2 = self.load_df(df2)

        # sup df has values only for ORCs and SRCs, for all items
        # columns: ['SerialIndex', 'ComplexIndex', 'Tok', 'SentenceType', 'SentenceItem', 'Surprisal']

        # spr df only has 'WordIndex' relevant
        df1[Consts.COMPLEXINDEX] = df1[Consts.WORDINDEX]
        df2 = df2[df2[Consts.COMPLEXINDEX] > 0]
        df2 = df2.groupby([Consts.SENTENCEITEM, Consts.COMPLEXINDEX, Consts.SENTENCETYPE], as_index=False, sort=False)[Consts.SURPRISAL].mean()

        # merge
        df = df1.merge(df2, on=[Consts.SENTENCEITEM, Consts.COMPLEXINDEX, Consts.SENTENCETYPE], how='outer').fillna('-')

        # check that there are not empty cells without need
        empty = df[df[Consts.SUBJECTNUMBER] == '-'].values.tolist()
        assert len(empty) == 0, len(empty)

        # save to file
        self.save_df(df, out_file)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-a', '--DF1', required=True, help='df in json file, spr')
    parser.add_argument('-b', '--DF2', required=True, help='df in json file, other')
    parser.add_argument('-o', '--OutFile', required=True, help='Path to save merged df')
    parser.add_argument('-m', '--MergeType', required=True, help='SUP or WM')
    args = parser.parse_args()

    assert args.MergeType in ['SUP', 'WM']

    Merge().build(args.MergeType).merge(args.DF1, args.DF2, args.OutFile)