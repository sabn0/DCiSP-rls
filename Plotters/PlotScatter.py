# import packages
from Plotters.PlotBase import PlotBase
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

@PlotBase.register_plotter(plotter_type='Scatter')
class PlotScatter(PlotBase):
    def __init__(self,
                 grid="whitegrid",
                 figsize=(10, 10),
                 s=200,
                 ax=None,
                 alpha=1.):
        super(PlotScatter, self).__init__(ax=ax)

        self.s = s
        self.grid = grid
        self.figsize = figsize
        self.alpha = alpha

    @classmethod
    def build(cls, plotter_type):
        return super(PlotScatter, cls).build(plotter_type)

    def set_alpha(self, alpha: float):
        self.alpha = alpha
        return self

    # implements the abstract
    def plot(self, df: pd.DataFrame, **kwargs) -> PlotBase:

        _ = plt.figure(figsize=self.figsize)
        sns.set_style(self.grid)
        ax = sns.scatterplot(
            x=kwargs['x'],
            y=kwargs['y'],
            data=df,
            hue=kwargs['hue'],
            palette=kwargs['palette'],
            style=kwargs['style'],
            s=self.s,
            color=kwargs['color'],
            alpha=self.alpha,
            ax=self.get_ax(),
        )
        self.set_ax(ax)
        return self

    def legend(self, **kwargs) -> None:
        super(PlotScatter, self).legend(**kwargs)
        if kwargs['legend_loc']:
            self.get_ax().legend(
                loc=kwargs['legend_loc'],
                prop={'size': kwargs['font_size']-20, 'weight': 'bold'},
                bbox_to_anchor=(1, 1.025)
            )

    def get_ax(self) -> plt.Axes:
        return super(PlotScatter, self).get_ax()

    def set_ax(self, ax: plt.Axes) -> None:
        super(PlotScatter, self).set_ax(ax=ax)

    def garnish(self, **kwargs):
        if kwargs['set_xticks']:
            self.get_ax().set_xticks(kwargs['set_xticks'])
        return super(PlotScatter, self).garnish(**kwargs)

    def save(self, out_path: str) -> None:
        super(PlotScatter, self).save(out_path)