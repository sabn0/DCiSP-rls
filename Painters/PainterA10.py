
# import packages
import numpy as np
from scipy import stats
from Painters.PainterBase import *
import Consts.Consts as Consts


@PainterBase.register_painter(painter_type='A10')
class PainterA10(PainterBase):
    def init__(self, *args):
        super(PainterA10, self).__init__(*args)

    def prepare(self, outliers: list, kv_slicer: dict):

        # build a base outliers (only ongoing) and slice on reaction times
        df = self.get_df()
        for outlier in outliers:
            df = OutliersBase.build(outlier, df=df, to_reject=self.get_to_reject()).reject().get_df()
        df = OutliersBase.build('None', df=df, to_reject=self.get_to_reject()).slice_on_fillers(sign='!=')

        # slice on session and sort
        for k,v in kv_slicer.items():
            df = df[df[k].isin(v)]

        # ORC in embedded noun or ORC in embedded verb
        df = df[(df[Consts.SENTENCETYPE] == Consts.ORC) & (df[Consts.COMPLEXINDEX].isin([self.plot_kws['position']]))]

        # set the df for paint
        self.set_df(df)
        return self

    def paint(self):

        # plot all plots on top of averages
        plotter = PlotBase.build('Scatter')
        for alpha in [0.1, 1.0]:

            df = self.get_df()

            if alpha >= 1.0:
                df = df.groupby([Consts.SENTENCEITEM], as_index=False)[[Consts.SURPRISAL, Consts.WORDREACTIONTIME]].mean()

            # calc correlation
            _ = stats.spearmanr(df[Consts.WORDREACTIONTIME].tolist(), df[Consts.SURPRISAL].tolist())
            print(_)

            max_y, min_y = max(self.garnish_kws['set_yticks']), min(self.garnish_kws['set_yticks'])
            df = df[(df[Consts.WORDREACTIONTIME] > min_y) & (df[Consts.WORDREACTIONTIME] < max_y)]
            plotter = plotter.set_alpha(alpha).plot(df=df, **self.plot_kws)

        plotter.garnish(**self.garnish_kws).save(self.garnish_kws['out_path'])

