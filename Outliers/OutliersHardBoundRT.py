
# import packages
from Outliers.OutliersBase import OutliersBase
import pandas as pd
import Consts.Consts as Consts

# mark reaction times that are out of given hard bounds
@OutliersBase.register_rejection(rejection_type='HardBoundRT')
class OutliersHardBoundRT(OutliersBase):
    def __init__(self, df:pd.DataFrame, to_reject: list, min_rt=150, max_rt=5000):
        super(OutliersHardBoundRT, self).__init__(df=df, to_reject=to_reject)

        self.max_rt = max_rt
        self.min_rt = min_rt
        self.set_criterion_name()

    def set_criterion_name(self):
        self.set_df(self.get_df().assign(OutliersHardBoundRT=False))
        self.criterion_name = self.get_df().columns[-1]

    def reject(self):

        # slice on rts only
        main_df = self.get_df()
        df = self.slice_on_fillers(sign='!=').copy()

        from collections import defaultdict
        counter = defaultdict(lambda : 0)

        for index, row in df.iterrows():
            counter[1] += 1
            if row[Consts.WORDREACTIONTIME] > self.max_rt or row[Consts.WORDREACTIONTIME] < self.min_rt:
                counter[0] += 1
                main_df = self.mark(main_df=main_df, indexes=[index], value=True)

        print("rejecting a total of {}% on hard bound".format(100*round(counter[0]/(sum(list(counter.values()))), 3)))
        self.slice_rejected(main_df)
        return self
