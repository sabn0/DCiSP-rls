
import spacy
from abc import abstractmethod
from spacy import displacy
from pathlib import Path
import Consts.Consts as Consts

# manual dependencies for spacy displacy
class PlotDep:

	deps = {}
	def __init__(self):
		pass

	@classmethod
	def register_dep(cls, dep_type):
		def decorator(dep):
			cls.deps[dep_type] = dep
			return dep
		return decorator

	@classmethod
	def build(cls, dep_type):
		if dep_type not in cls.deps:
			raise ValueError
		dep = cls.deps[dep_type]()
		return dep

	def save(self, out_path: str):
		assert out_path.endswith('svg')
		svg = displacy.render(self.sent(), style="dep", manual=True)
		output_path = Path(out_path)
		output_path.open("w", encoding="utf-8").write(svg)

	@abstractmethod
	def sent(self) -> dict:
		pass


@PlotDep.register_dep(dep_type=Consts.ORC_BEGINNING)
class ORC_Beginning(PlotDep):
	def __init__(self):
		super(ORC_Beginning).__init__()

	def sent(self) -> dict:
		return {
			"words":[
				{"text": "ha (the)", "tag": "DEF"},
				{"text": "more (teacher)", "tag": "NN"},
				{"text": "she (that)", "tag": "REL"},
				{"text": "ha (the)", "tag": "DEF"},
				{"text": "talmid (student)", "tag": "NN"}
			],
			"arcs":[
				{"start": 0, "end": 1, "label": "def", "dir": "left"},
				{"start": 1, "end": 2, "label": "rcmod", "dir": "right"},
				{"start": 3, "end": 4, "label": "def", "dir": "left"}
			]
		}


@PlotDep.register_dep(dep_type=Consts.ORC_EMBEDDED)
class ORC_Embedded(PlotDep):
	def __init__(self):
		super(ORC_Embedded).__init__()

	def sent(self) -> dict:
		return {
			"words":[
				{"text": "she (that)", "tag": "REL"},
				{"text": "ha (the)", "tag": "DEF"},
				{"text": "talmid (student)", "tag": "NN"},
				{"text": "ra'a (saw)", "tag": "VB"},
			],
			"arcs":[
				{"start": 0, "end": 3, "label": "relcomp", "dir": "right"},
				{"start": 2, "end": 3, "label": "subj", "dir": "left"},
				{"start": 1, "end": 2, "label": "def", "dir": "left"}
			]
		}


@PlotDep.register_dep(dep_type=Consts.SRC_BEGINNING)
class SRC_Beginning(PlotDep):
	def __init__(self):
		super(SRC_Beginning).__init__()

	def sent(self) -> dict:
		return {
			"words":[
				{"text": "ha (the)", "tag": "DEF"},
				{"text": "more (teacher)", "tag": "NN"},
				{"text": "she (that)", "tag": "REL"},
				{"text": "ra'a (saw)", "tag": "VB"},
			],
			"arcs":[
				{"start": 0, "end": 1, "label": "def", "dir": "left"},
				{"start": 1, "end": 2, "label": "rcmod", "dir": "right"},
				{"start": 2, "end": 3, "label": "relcomp", "dir": "right"}
			]
		}


@PlotDep.register_dep(dep_type=Consts.SRC_EMBEDDED)
class SRC_Embedded(PlotDep):
	def __init__(self):
		super(SRC_Embedded).__init__()

	def sent(self) -> dict:
		return {
			"words":[
				{"text": "she (that)", "tag": "REL"},
				{"text": "ra'a (saw)", "tag": "VB"},
				{"text": "et (Acc)", "tag": "AT"},
				{"text": "ha (the)", "tag": "DEF"},
				{"text": "talmid (student)", "tag": "NN"}
			],
			"arcs":[
				{"start": 0, "end": 1, "label": "relcomp", "dir": "right"},
				{"start": 1, "end": 2, "label": "obj", "dir": "right"},
				{"start": 2, "end": 4, "label": "hd", "dir": "right"},
				{"start": 3, "end": 4, "label": "def", "dir": "left"}
			]
		}


