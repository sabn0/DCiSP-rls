
# import packages
import numpy as np
from Painters.PainterBase import *
from scipy import stats
import Consts.Consts as Consts


@PainterBase.register_painter(painter_type='A6')
class PainterA6(PainterBase):
    def init__(self, *args):
        super(PainterA6, self).__init__(*args)

    def prepare(self, outliers: list, kv_slicer: dict):

        # build a base outliers (only ongoing) and slice on reaction times
        df = self.get_df()
        for outlier in outliers:
            df = OutliersBase.build(outlier, df=df, to_reject=self.get_to_reject()).reject().get_df()
        df = OutliersBase.build('None', df=df, to_reject=self.get_to_reject()).slice_on_main_verb()

        # slice on session and sort
        for k,v in kv_slicer.items():
            df = df[df[k].isin(v)]

        # make y values
        df = df.groupby([Consts.SENTENCETYPE, Consts.SUBJECTNUMBER], as_index=False)[[self.plot_kws['x'], self.plot_kws['y']]].mean()
        n_subjects = len(pd.unique(df[Consts.SUBJECTNUMBER]).tolist())
        assert n_subjects * 2 == len(df)

        if self.plot_kws['y_type'] == 'a':
            df['Temp'] = df[self.plot_kws['y']].shift(periods=n_subjects)
            df[self.plot_kws['y']] = (df['Temp'] - df[self.plot_kws['y']])
            df = df.dropna().drop(columns=[Consts.SENTENCETYPE, 'Temp'])

        # this is for ORC alone
        elif self.plot_kws['y_type'] == 'b':
            df = df[df[Consts.SENTENCETYPE] == Consts.ORC]
            df[df[self.plot_kws['y']]] = df[self.plot_kws['y']]
            df = df.dropna().drop(columns=[Consts.SENTENCETYPE])
        else:
            raise ValueError("unknown figure type {}".format(self.plot_kws['y_type']))

        _ = stats.spearmanr(df[self.plot_kws['x']].tolist(), df[self.plot_kws['y']].tolist())
        print(_)

        # set the df for paint
        self.set_df(df)
        return self

    def paint(self):
        PlotBase.build('Scatter').plot(df=self.get_df(), **self.plot_kws).garnish(**self.garnish_kws).save(self.garnish_kws['out_path'])

