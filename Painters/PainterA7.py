
# import packages
import numpy as np
from Painters.PainterBase import *
import Consts.Consts as Consts


@PainterBase.register_painter(painter_type='A7')
class PainterA7(PainterBase):
    def init__(self, *args):
        super(PainterA7, self).__init__(*args)

    def prepare(self, outliers: list, kv_slicer: dict):

        # build a base outliers (only ongoing) and slice on reaction times
        df = self.get_df()
        for outlier in outliers:
            df = OutliersBase.build(outlier, df=df, to_reject=self.get_to_reject()).reject().get_df()
        df = OutliersBase.build('None', df=df, to_reject=self.get_to_reject()).slice_on_fillers(sign='!=')

        # slice on session and sort
        for k,v in kv_slicer.items():
            df = df[df[k].isin(v)]

        # for pre-exposure data only
        df = df[df[Consts.SESSION] == 'Before']

        # unify reaction times
        # add DLT prediction (manual computation)
        # if orc - remove trailing
        if Consts.ORC in list(kv_slicer.values())[0]:
            df = df[df[Consts.WORDINDEX] <= 5]
            df = df.assign(Prediction=0)
            df.loc[df[Consts.WORDINDEX] == 5, Consts.PREDICTION] = (1/3)
            df.loc[df[Consts.WORDINDEX] == 4, Consts.PREDICTION] = 3
            df.loc[df[Consts.WORDINDEX] == 3, Consts.PREDICTION] = 3
            df.loc[df[Consts.WORDINDEX] == 2, Consts.PREDICTION] = (1/3)
            df.loc[df[Consts.WORDINDEX] == 1, Consts.PREDICTION] = .5

        # if src - remove trailing, unify 3+4 -> 3, 5->4, 6->5
        elif Consts.SRC in list(kv_slicer.values())[0]:
            df = df[df[Consts.WORDINDEX] <= 6]
            df.loc[df[Consts.WORDINDEX] >= 4, Consts.WORDINDEX] -= 1
            df = df.assign(Prediction=0)
            df.loc[df[Consts.WORDINDEX] == 5, Consts.PREDICTION] = (1/3)
            df.loc[df[Consts.WORDINDEX] == 4, Consts.PREDICTION] = 3
            df.loc[df[Consts.WORDINDEX] == 3, Consts.PREDICTION] = (1/3)
            df.loc[df[Consts.WORDINDEX] == 2, Consts.PREDICTION] = .5
            df.loc[df[Consts.WORDINDEX] == 1, Consts.PREDICTION] = .5

        df = df.rename(columns={Consts.WORDREACTIONTIME: 'Avg RT (ms)'})

        # set the df for paint
        self.set_df(df)
        return self

    def paint(self):

        y_axis = self.plot_kws['y']
        y_ticks_labels = self.garnish_kws['set_yticks']
        colors = self.garnish_kws["color"] = self.plot_kws['color']
        self.plot_kws['twinx'] = True
        plotter = PlotBase.build('Line')

        for y_ax, y_ticks, color in zip(y_axis, y_ticks_labels, colors):

            self.plot_kws['color'] = color
            self.plot_kws['y'] = y_ax
            self.garnish_kws['set_yticks'] = y_ticks
            plotter = plotter.plot(df=self.get_df(), **self.plot_kws)
            self.plot_kws['twinx'] = False

        plotter.garnish(**self.garnish_kws).save(self.garnish_kws['out_path'])
