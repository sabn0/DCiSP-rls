
# import packages
from Plotters.PlotBase import PlotBase
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

@PlotBase.register_plotter(plotter_type='Bar')
class PlotBar(PlotBase):
    def __init__(self,
                 ci=68,
                 errwidth=4,
                 capsize=0.1,
                 grid="whitegrid",
                 figsize=(13, 7),
                 dodge=True,
                 ax=None):
        super(PlotBar, self).__init__(ax=ax)

        self.ci = ci
        self.errwidth = errwidth
        self.capsize = capsize
        self.grid = grid
        self.figsize = figsize
        self.dodge = dodge

    def plot(self, df: pd.DataFrame, **kwargs) -> PlotBase:

        _ = plt.figure(figsize=self.figsize)
        sns.set_style(self.grid)
        ax = sns.barplot(
            x=kwargs['x'],
            order=kwargs['order'],
            y=kwargs['y'],
            data=df,
            hue=kwargs['hue'],
            hue_order=kwargs['hue_order'],
            palette=kwargs['palette'],
            errorbar=('ci', self.ci),
            capsize=self.capsize,
            errwidth=self.errwidth,
            dodge=self.dodge,
            ax=self.get_ax()
        )

        self.set_ax(ax)
        return self

    @classmethod
    def build(cls, plotter_type):
        return super(PlotBar, cls).build(plotter_type)

    def get_ax(self) -> plt.Axes:
        return super(PlotBar, self).get_ax()

    def set_ax(self, ax: plt.Axes) -> None:
        super(PlotBar, self).set_ax(ax=ax)

    def garnish(self, **kwargs):
        return super(PlotBar, self).garnish(**kwargs)

    def legend(self, **kwargs) -> None:
        super(PlotBar, self).legend(**kwargs)

    def save(self, out_path: str) -> None:
        super(PlotBar, self).save(out_path)