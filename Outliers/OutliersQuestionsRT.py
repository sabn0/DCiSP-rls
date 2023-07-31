
# import packages
from Outliers.OutliersBase import OutliersBase
import pandas as pd
import Consts.Consts as Consts

# mark subjects that had a below 0.75 accuracy across the experiment
@OutliersBase.register_rejection(rejection_type='QuestionsRT')
class OutliersQuestionsRT(OutliersBase):
    def __init__(self, df: pd.DataFrame, to_reject: list, min_acc=0.75):
        super(OutliersQuestionsRT, self).__init__(df=df, to_reject=to_reject)
        self.min_acc= min_acc
        self.set_criterion_name()

    def set_criterion_name(self):
        self.set_df(self.get_df().assign(OutliersQuestionsRT=False))
        self.criterion_name = self.get_df().columns[-1]

    def reject(self):

        # slice df on questions only
        main_df = self.get_df()
        df = self.slice_on_questions(keep_fillers=True).copy()

        from collections import defaultdict
        counter = defaultdict(lambda : 0)

        for subject in df[Consts.SUBJECTNUMBER].unique().tolist():

            indexes = main_df[main_df[Consts.SUBJECTNUMBER] == subject].index.tolist()
            counter[1] += 1

            # calculate the accuracy for the subject
            sub_df = df[df[Consts.SUBJECTNUMBER] == subject]
            sub_acc = sub_df[Consts.QUESTIONANSWER].sum() / len(sub_df[Consts.QUESTIONANSWER])

            # mark outliers if much criterion
            if sub_acc < self.min_acc + 1e-06:
                counter[0] += 1
                main_df = self.mark(main_df=main_df, indexes=indexes, value=True)

        print("rejecting a total of {}% on questions".format(100*round(counter[0]/(sum(list(counter.values()))), 3)))
        self.slice_rejected(main_df)
        return self