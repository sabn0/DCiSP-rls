
# import packages
from Painters.PainterBase import *


@PainterBase.register_painter(painter_type='A5')
class PainterA5(PainterBase):
    def init__(self, *args):
        super(PainterA5, self).__init__(*args)

    def prepare(self, outliers: list, kv_slicer: dict):

        # No outliers but base, slice on questions
        df = self.get_df()
        for outlier in outliers:
            df = OutliersBase.build(outlier, df=self.get_df(), to_reject=self.get_to_reject()).reject().slice_on_questions()

        # slice on group
        for k,v in kv_slicer.items():
            df = df[df[k].isin(v)]

        # set the df for paint
        self.set_df(df)
        return self

    def paint(self):
        PlotBase.build('Bar').plot(df=self.get_df(), **self.plot_kws).garnish(**self.garnish_kws).save(self.garnish_kws['out_path'])

