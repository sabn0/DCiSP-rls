
# import packages
from Plotters.PlotBase import PlotBase
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


@PlotBase.register_plotter(plotter_type='Point')
class PlotPoint(PlotBase):
    def __init__(self,
                 ci=68,
                 scale=1.5,
                 errwidth=4,
                 capsize=0.1,
                 grid="whitegrid",
                 figsize=(13, 7),
                 dodge=False,
                 ax=None):
        super(PlotPoint, self).__init__(ax=ax)

        self.ci = ci
        self.scale = scale
        self.errwidth = errwidth
        self.capsize = capsize
        self.dodge = dodge
        self.grid = grid
        self.figsize = figsize
        self.legend_lines = []

    @classmethod
    def build(cls, plotter_type):
        return super(PlotPoint, cls).build(plotter_type)

    def plot(self, df: pd.DataFrame, **kwargs) -> PlotBase:

        _ = plt.figure(figsize=self.figsize)
        sns.set_style(self.grid)
        ax = sns.pointplot(
            x=kwargs['x'],
            order=kwargs['order'],
            y=kwargs['y'],
            data=df,
            hue=kwargs['hue'],
            palette=kwargs['palette'],
            hue_order=kwargs['hue_order'],
            capsize=self.capsize,
            errorbar=('ci', self.ci),
            scale=self.scale,
            errwidth=self.errwidth,
            dodge=kwargs['dodge'],
            ax=self.get_ax()
        )

        self.set_ax(ax)
        return self

    def get_ax(self) -> plt.Axes:
        return super(PlotPoint, self).get_ax()

    def set_ax(self, ax: plt.Axes) -> None:
        super(PlotPoint, self).set_ax(ax=ax)

    def garnish(self, **kwargs):

        # this garnish condition is specific for setting the x ax ticks and labels of M5
        if 'regions' in kwargs:
            self.get_ax().set_xticks([])
            x_indexes = self.get_ax().lines[0].get_xdata()
            y_indexes = self.get_ax().lines[0].get_ydata()
            for t, shift in {'ORC': 0.25, 'SRC': 0.5}.items():
                tick_set = kwargs['set_xticks_{}'.format(t)]
                for i, ticks_label in enumerate(tick_set):
                    x = x_indexes[i]-0.2 if i != 2 else x_indexes[i]
                    y = kwargs['set_yticks'][0]-1*shift*(kwargs['set_yticks'][1]-kwargs['set_yticks'][0])
                    self.get_ax().annotate(ticks_label,
                                           xy=(x,y),
                                           color=kwargs['color'][t],
                                           annotation_clip=False,
                                           fontsize=kwargs['font_size']-5,
                                           fontweight='bold')

            self.get_ax().plot([x_indexes[kwargs['orc_skip'][0]], x_indexes[kwargs['orc_skip'][1]]],
                               [y_indexes[kwargs['orc_skip'][0]], y_indexes[kwargs['orc_skip'][1]]],
                               linestyle='dotted', color=kwargs['color']['ORC'], zorder=0)

        return super(PlotPoint, self).garnish(**kwargs)

    def legend(self, **kwargs) -> None:
        super(PlotPoint, self).legend(**kwargs)

    def save(self, out_path: str) -> None:
        super(PlotPoint, self).save(out_path)

