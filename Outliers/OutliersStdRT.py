
# import packages
from Outliers.OutliersBase import OutliersBase
import pandas as pd
import numpy as np
import Consts.Consts as Consts

# mark Items that had an above threshold reaction time on average
@OutliersBase.register_rejection(rejection_type='StdRT')
class OutliersStdRT(OutliersBase):
    def __init__(self, df:pd.DataFrame, to_reject: list, std=2.5):
        super(OutliersStdRT, self).__init__(df=df, to_reject=to_reject)

        self.std = std
        self.set_criterion_name()

    def set_criterion_name(self):
        self.set_df(self.get_df().assign(OutliersStdRT=False))
        self.criterion_name = self.get_df().columns[-1]

    def reject(self):

        # slice on rts only
        main_df = self.get_df()
        df = self.slice_on_fillers(sign='!=').copy()

        sessions = df[Consts.SESSION].unique().tolist()
        sentence_types = df[Consts.SENTENCETYPE].unique().tolist()
        groups = df[Consts.GROUP].unique().tolist()

        from collections import defaultdict
        counter = defaultdict(lambda : 0)

        for session in sessions:
            for sentence_type in sentence_types:
                for group in groups:

                    this_df = df[(df[Consts.SESSION] == session)&(df[Consts.SENTENCETYPE] == sentence_type)&(df[Consts.GROUP] == group)]
                    indexes = this_df[Consts.WORDINDEX].unique().tolist()
                    for i in indexes:

                        i_df = this_df[this_df[Consts.WORDINDEX] == i]
                        rts = i_df[Consts.WORDREACTIONTIME].tolist()

                        m,s = np.mean(rts), np.std(rts)

                        for t, row in i_df.iterrows():
                            counter[1] += 1
                            if (m + self.std * s) < row[Consts.WORDREACTIONTIME]:
                                counter[0] +=1
                                main_df = self.mark(main_df=main_df, indexes=[t], value=True)

        print("rejecting a total of {}% on std".format(100*round(counter[0]/(sum(list(counter.values()))), 3)))
        self.slice_rejected(main_df)
        return self



