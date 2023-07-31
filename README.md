# Dynamic changes in syntactic processing

## Overview
Code for data visualization and statistical analyses in the thesis (). \
The project is about changes in syntactic predictions of humans after reading exposures, and the interactions between those human predictions and
NLP language models (GPT) outputs, in hebrew. The code runs all the figures, tables and appendices in the document with minor changes.

## How to run (Linux)
- prerequisites: python >= 3.8, R.
- Clone the repo, then change direction to the main folder.
- for example via a new virtual environment and pip:
```
python3.8 -m venv venv;
source venv/bin/activate;
pip install --upgrade pip;
pip install -r requirements.txt;
```
- Now, the analyses can be run from the .sh script within the Scripts folder as follows: \
```bash Scripts/run.sh m PATH_TO_DATA PATH_TO_CORPUS```

- PATH_TO_DATA (mandatory) : json files of the raw data (not released here).
- PATH_TO_CORPUS (optional) : a hebrew corpus in a conll format. I used the corpus from [here](https://u.cs.biu.ac.il/~yogo/hebwiki/). \
If not given, sections that use the corpus will be skipped.

## Software
I used python 3.8, see the packages in the [requirements.txt file](https://github.com/sabn0/SPIH/blob/main/requirements.txt). \
I used R 3.4.4 and the lme4 package.
