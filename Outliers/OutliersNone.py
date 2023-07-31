
# import packages
from Outliers.OutliersBase import OutliersBase
import pandas as pd

# no outliers (only base)
@OutliersBase.register_rejection(rejection_type='None')
class OutliersNone(OutliersBase):
    def __init__(self, df:pd.DataFrame, to_reject: list):
        super(OutliersNone, self).__init__(df=df, to_reject=to_reject)
        self.set_criterion_name()

    def set_criterion_name(self):
        self.criterion_name = 'None'

    def reject(self):
        return self
