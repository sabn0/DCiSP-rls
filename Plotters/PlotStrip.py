# import packages
from Plotters.PlotBase import PlotBase
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

@PlotBase.register_plotter(plotter_type='Strip')
class PlotStrip(PlotBase):
    def __init__(self,
                 jitter=0.03,
                 linewidth=2,
                 size=15,
                 edgecolor='gray',
                 grid="whitegrid",
                 figsize=(10, 10),
                 ax=None):
        super(PlotStrip, self).__init__(ax=ax)

        self.grid = grid
        self.figsize = figsize
        self.jitter = jitter
        self.linewidth = linewidth
        self.size = size
        self.edgecolor = edgecolor

    @classmethod
    def build(cls, plotter_type):
        return super(PlotStrip, cls).build(plotter_type)

    # implements the abstract
    def plot(self, df: pd.DataFrame, **kwargs) -> PlotBase:

        _ = plt.figure(figsize=self.figsize)
        sns.set_style(self.grid)
        ax = sns.stripplot(
            x=kwargs['x'],
            y=kwargs['y'],
            data=df,
            hue=kwargs['hue'],
            palette=kwargs['palette'],
            jitter=self.jitter,
            size=self.size,
            linewidth=self.linewidth,
            edgecolor=self.edgecolor,
            ax=self.get_ax(),

        )
        self.set_ax(ax)
        return self

    # overrides the super
    def legend(self, **kwargs) -> None:
        (handles, labels) = self.get_ax().get_legend_handles_labels()
        h2l = {h: l for h, l in zip(handles, labels) if type(h) != plt.Line2D}
        self.get_ax().legend(
            list(h2l.keys()),
            list(h2l.values()),
            loc='upper right',
            markerscale=kwargs['markerscale'],
            prop={'size': kwargs['font_size'] - 20, 'weight': 'bold'}
        )
        for ha in self.get_ax().legend_.legendHandles:
            ha.set_edgecolor(self.edgecolor)
            ha.set_linewidth(self.linewidth)

    def get_ax(self) -> plt.Axes:
        return super(PlotStrip, self).get_ax()

    def set_ax(self, ax: plt.Axes) -> None:
        super(PlotStrip, self).set_ax(ax=ax)

    def garnish(self, **kwargs):
        return super(PlotStrip, self).garnish(**kwargs)

    def save(self, out_path: str) -> None:
        super(PlotStrip, self).save(out_path)