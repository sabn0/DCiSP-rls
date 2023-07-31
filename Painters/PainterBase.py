
# import packages
from abc import abstractmethod
import pandas as pd
import json
from Plotters.PlotBase import PlotBase
from Plotters.PlotStrip import PlotStrip
from Plotters.PlotBar import PlotBar
from Plotters.PlotPoint import PlotPoint
from Plotters.PlotLine import PlotLine
from Plotters.PlotScatter import PlotScatter
from Outliers.OutliersBase import OutliersBase
from Outliers.OutliersNone import OutliersNone
from Outliers.OutliersHardBoundRT import OutliersHardBoundRT
from Outliers.OutliersQuestionsRT import OutliersQuestionsRT
from Outliers.OutliersStdRT import OutliersStdRT

# A base class to plot a figure
class PainterBase:
    painters = {}

    def __init__(self, df: pd.DataFrame, to_reject: list, json_plot: str, json_garnish: str, out_path: str):
        self.df = df
        self.to_reject = to_reject
        self.plot_kws = self.read_json(json_plot)
        self.garnish_kws = self.read_json(json_garnish, out_path)

    # I use the decorator design pattern to allow creating instances of all painters
    # types without having to explicitly write the string of type on action
    @classmethod
    def register_painter(cls, painter_type):
        def decorator(painter):
            cls.painters[painter_type] = painter
            return painter
        return decorator

    @classmethod
    def build(cls, painter_type, *args):
        if painter_type not in cls.painters:
            raise ValueError
        painter = cls.painters[painter_type](*args)
        return painter

    def read_json(self, json_file, out_path=None) -> dict:
        with open(json_file, 'r') as f:
            d = json.load(f)
        if out_path is not None:
            d['out_path'] = out_path
        return d

    def get_to_reject(self) -> list:
        return self.to_reject

    def get_df(self) -> pd.DataFrame:
        return self.df

    def set_df(self, df:pd.DataFrame):
        self.df = df

    # return self for chaining methods
    # kv_slicer is a dict of slicers for the data (such as group, session etc)
    @abstractmethod
    def prepare(self, outlier: list, fl_slicer: dict):
        pass

    @abstractmethod
    def paint(self):
        pass