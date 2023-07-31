
# import packages
from Painters.PainterBase import *
import Consts.Consts as Consts


@PainterBase.register_painter(painter_type='M4')
class PainterM4(PainterBase):
    def init__(self, *args):
        super(PainterM4, self).__init__(*args)

    def prepare(self, outliers: list, kv_slicer: dict):

        # build a base outliers (only ongoing) and slice on reaction times
        df = self.get_df()
        for outlier in outliers:
            df = OutliersBase.build(outlier, df=df, to_reject=self.get_to_reject()).reject().get_df()
        df = OutliersBase.build('None', df=df, to_reject=self.get_to_reject()).slice_on_main_verb()

        # slice on session and sort
        for k,v in kv_slicer.items():
            df = df[df[k].isin(v)]
        df = df.sort_values(by=Consts.SENTENCETYPE, ascending=True)

        # seems as if the df must be averaged over subjects before entering scatter since units not functional in
        # ScatterPlot since this is the case, I average on subjects and sentence type and use units only in the LinePlot
        average_variables = [Consts.SUBJECTNUMBER, Consts.SENTENCETYPE]
        averages = df.groupby(average_variables)[Consts.WORDREACTIONTIME].mean().reset_index(name=Consts.AVGWORDREACTIONTIME)
        df = pd.merge(left=df, right=averages, left_on=average_variables, right_on=average_variables)
        df = df[[Consts.SUBJECTNUMBER, Consts.SENTENCETYPE, Consts.GROUP, Consts.AVGWORDREACTIONTIME]].drop_duplicates()

        # set the df for paint
        self.set_df(df)
        return self

    def paint(self):
        PlotBase\
            .build('Line')\
            .plot(df=self.get_df(), **self.plot_kws)\
            .build('Strip')\
            .plot(df=self.get_df(), **self.plot_kws)\
            .garnish(**self.garnish_kws)\
            .save(self.garnish_kws['out_path'])
