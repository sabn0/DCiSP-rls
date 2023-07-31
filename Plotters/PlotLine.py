
# import packages
from Plotters.PlotBase import PlotBase
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


@PlotBase.register_plotter(plotter_type='Line')
class PlotLine(PlotBase):
    def __init__(self,
                 ci=68,
                 linewidth=3,
                 grid="whitegrid",
                 figsize=(10, 10),
                 ax=None):
        super(PlotLine, self).__init__(ax=ax)

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        plt.rc('font', **{'size':20})

        self.ci = ci
        self.grid = grid
        self.figsize = figsize
        self.linewidth = linewidth
        self.axes = []


    @classmethod
    def build(cls, plotter_type):
        return super(PlotLine, cls).build(plotter_type)

    def plot(self, df: pd.DataFrame, **kwargs) -> PlotBase:

        self.grid = self.grid if 'grid' not in kwargs else kwargs['grid']
        _ = plt.figure(figsize=self.figsize)
        sns.set_style(self.grid)
        g = sns.lineplot(
            x=kwargs['x'],
            y=kwargs['y'],
            data=df,
            hue=kwargs['hue'],
            palette=kwargs['palette'],
            color=kwargs['color'],
            units=kwargs['units'],
            estimator=kwargs['estimator'],
            lw=self.linewidth,
            ax=self.get_ax(),
            err_style="bars",
            errorbar=('ci', self.ci)
        )

        if kwargs['twinx']:
            g.set_xlabel("")
            ax = g.axes.twinx()
            self.set_ax(ax)
            self.axes.append(ax)
        else:
            self.set_ax(g)
            self.axes.append(g)
        return self

    def get_ax(self) -> plt.Axes:
        return super(PlotLine, self).get_ax()

    def set_ax(self, ax: plt.Axes) -> None:
        super(PlotLine, self).set_ax(ax=ax)

    def garnish(self, **kwargs):

        # this garnish condition is specific for setting the x ax ticks and labels of A7
        ax = super(PlotLine, self).get_ax()
        ax.set(xticklabels=[])
        x_indexes = ax.lines[0].get_xdata()
        for i, ticks_label in enumerate(kwargs['set_xticks']):
            x = x_indexes[i] - 0.2 if i != 2 else x_indexes[i]-0.3
            ax.annotate(ticks_label, xy=(x, 0), annotation_clip=False)

        self.legend(**kwargs)
        return self

    def legend(self, **kwargs) -> None:
        if kwargs['legend_loc']:
            from matplotlib.lines import Line2D
            self.get_ax().legend(
                handles=[Line2D([], [], marker='_', color=kwargs["color"][0], label=kwargs["y_label"][0]),
                         Line2D([], [], marker='_', color=kwargs["color"][1], label=kwargs["y_label"][1])]
            )

    def save(self, out_path: str) -> None:
        super(PlotLine, self).save(out_path)