
# import packages
from Painters.PainterBase import *
import Consts.Consts as Consts


@PainterBase.register_painter(painter_type='M5')
class PainterM5(PainterBase):
    def init__(self, *args):
        super(PainterM5, self).__init__(*args)

    def prepare(self, outliers: list, kv_slicer: dict):

        # build a base outliers (only ongoing) and slice on reaction times
        df = self.get_df()

        # alignment of SRCs to ORCs
        df = df[df[Consts.COMPLEXINDEX] > 0]
        df.loc[(df[Consts.COMPLEXINDEX] >= 3) & (df[Consts.SENTENCETYPE] == Consts.ORC), Consts.COMPLEXINDEX] += 1

        # set the df for paint
        self.set_df(df)
        return self

    def paint(self):
        PlotBase\
            .build('Point')\
            .plot(df=self.get_df(), **self.plot_kws)\
            .garnish(**self.garnish_kws)\
            .save(self.garnish_kws['out_path'])
