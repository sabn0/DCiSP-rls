
# import packages
from Painters.PainterBase import *


@PainterBase.register_painter(painter_type='M6')
class PainterM6(PainterBase):
    def init__(self, *args):
        super(PainterM6, self).__init__(*args)

    def prepare(self, outliers: list, kv_slicer: dict):

        # build a base outliers (only ongoing) and slice on reaction times
        df = self.get_df()
        for outlier in outliers:
            df = OutliersBase.build(outlier, df=df, to_reject=self.get_to_reject()).reject().get_df()
        df = OutliersBase.build('None', df=df, to_reject=self.get_to_reject()).slice_on_main_verb()

        # slice on group
        for k,v in kv_slicer.items():
            df = df[df[k].isin(v)]

        # set the df for paint
        self.set_df(df)
        return self

    def paint(self):
        PlotBase.build('Point').plot(df=self.get_df(), **self.plot_kws).garnish(**self.garnish_kws).save(self.garnish_kws['out_path'])
