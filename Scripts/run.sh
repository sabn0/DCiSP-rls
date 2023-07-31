
#!/bin/bash

# bash Scripts/run.sh data corpus
  # data = path to folder made jsons + meta
  # corpus = path to corpus of heb sentences in conll format

# exit if error
set -e

# env versions
py_version=$(python --version)
r_version=$(R --version)
echo -e "using ${py_version}\n"
echo -e "${r_version}\n"

# parse args
data_dir=$1;
corpus_file=$2;
spr_sentences="${data_dir}/Meta/spr.parsed";
i_files_dir="IFiles"

# loactions of figure prep
# json files with df (main data)
df_spr="${data_dir}/Spr.json"
df_wm="${data_dir}/WM.json"
df_exp="${data_dir}/Experience.json"

# make intermediate files
# create directory for files
if [ ! -d "./${i_files_dir}" ]; then
  mkdir ${i_files_dir}
fi

# i files with data
csv_spr="${i_files_dir}/Spr.csv"
csv_wm="${i_files_dir}/WM.csv"
csv_exp="${i_files_dir}/Experience.csv"
rc_counts_out="${i_files_dir}/rc.counts"

# make output images directory
o_images_dir="OImages"
if [ ! -d "./${o_images_dir}" ]; then
  mkdir ${o_images_dir}
fi

# set outlier rejections
rejections="QuestionsRT,HardBoundRT,StdRT"

# specify namings for files
ngram_mle_json="${i_files_dir}/ngram_mle.json"
q_mle="${i_files_dir}/q.mle"
e_mle="${i_files_dir}/e.mle"
lm_json="${i_files_dir}/lm.json"
lm_merged="${i_files_dir}/merged_lm.json"
wm_merged="${i_files_dir}/merged_wm.json"

echo "files preprocessing"
echo "MLE creation - ngrams if not exists"
if [ ! -f "./${ngram_mle_json}" ]; then
  python RunMLE.py -c=${corpus_file} -s=${spr_sentences} -n=3 -m=Ngrams -o=${ngram_mle_json} -q=${q_mle} -e=${e_mle};
fi

echo "MLE creation - lm if not exists"
if [ ! -f "./${lm_json}" ]; then
  python RunMLE.py -s=${spr_sentences} -n=1 -m=LM -o=${lm_json};
fi

echo "Megre lm data with spr if not exists"
if [ ! -f "./${lm_merged}" ]; then
  python Merge.py -a=${df_spr} -b=${lm_json} -o=${lm_merged} -m=SUP;
fi

echo "Merge wm data with spr if not exists"
if [ ! -f "./${wm_merged}" ]; then
  python Merge.py -a=${df_spr} -b=${df_wm} -o=${wm_merged} -m=WM;
fi

echo "Make outliers rejected csvs from jsons"
python MakeCSV.py -a=${df_spr} -b=${df_exp} -c=${df_wm} -o=${i_files_dir};

#plots
echo "plot figures, appendices and tables"

echo "figure M1 is a diagram, skip"

echo "figure M2 is a diagram, skip"

echo "figure M3 is a diagram, skip"

fig="M4"
echo "figure ${fig}"
python CreateFigure.py \
  -d=${df_spr} \
  -o=${o_images_dir} \
  -r=${rejections} \
  -f=${fig} \
  -l=Session:Before \
  -i="json_files/figure_${fig}_plot_kwargs.json" \
  -j="json_files/figure_${fig}_garnish_kwargs.json";

fig="M5"
echo "figure ${fig}a"
python CreateFigure.py \
  -d=${ngram_mle_json} \
  -o=${o_images_dir} \
  -l=: \
  -f=${fig} \
  -i="json_files/figure_${fig}a_plot_kwargs.json" \
  -j="json_files/figure_${fig}a_garnish_kwargs.json";
echo "figure ${fig}b"
python CreateFigure.py \
  -d=${lm_json} \
  -o=${o_images_dir} \
  -l=: \
  -f=${fig} \
  -i="json_files/figure_${fig}b_plot_kwargs.json" \
  -j="json_files/figure_${fig}b_garnish_kwargs.json";

fig="M6"
echo "figure ${fig}a"
python CreateFigure.py \
  -d=${df_spr} \
  -o=${o_images_dir} \
  -r=${rejections} \
  -f=${fig} \
  -l=Group:RC-enriched \
  -i="json_files/figure_${fig}a_plot_kwargs.json" \
  -j="json_files/figure_${fig}a_garnish_kwargs.json";
echo "figure ${fig}b"
python CreateFigure.py \
  -d=${df_spr} \
  -o=${o_images_dir} \
  -r=${rejections} \
  -f=${fig} \
  -l=Group:Control \
  -i="json_files/figure_${fig}b_plot_kwargs.json" \
  -j="json_files/figure_${fig}b_garnish_kwargs.json";

echo "figure A1 is a text, skip"

echo "figure A2 is a text, skip"

echo "figure A3 is a text, skip"

echo "figure A4 is a text, skip"

fig="A5"
echo "figure ${fig}a"
python CreateFigure.py \
  -d=${df_spr} \
  -o=${o_images_dir} \
  -r=${rejections} \
  -f=${fig} \
  -l=Group:RC-enriched \
  -i="json_files/figure_${fig}a_plot_kwargs.json" \
  -j="json_files/figure_${fig}a_garnish_kwargs.json";
echo "figure ${fig}b"
python CreateFigure.py \
  -d=${df_spr} \
  -o=${o_images_dir} \
  -r=${rejections} \
  -f=${fig} \
  -l=Group:Control \
  -i="json_files/figure_${fig}b_plot_kwargs.json" \
  -j="json_files/figure_${fig}b_garnish_kwargs.json";

fig="A6"
echo "figure ${fig}a"
python CreateFigure.py \
  -d=${wm_merged} \
  -o=${o_images_dir} \
  -r=${rejections} \
  -f=${fig} \
  -l=Session:Before \
  -i="json_files/figure_${fig}a_plot_kwargs.json" \
  -j="json_files/figure_${fig}a_garnish_kwargs.json";
echo "figure ${fig}b"
python CreateFigure.py \
  -d=${wm_merged} \
  -o=${o_images_dir} \
  -r=${rejections} \
  -f=${fig} \
  -l=Session:Before \
  -i="json_files/figure_${fig}b_plot_kwargs.json" \
  -j="json_files/figure_${fig}b_garnish_kwargs.json";

fig="A7"
echo "figure ${fig}a"
python CreateFigure.py \
  -d=${df_spr} \
  -o=${o_images_dir} \
  -r=${rejections} \
  -f=${fig} \
  -l=SentenceType:ORC \
  -i="json_files/figure_${fig}a_plot_kwargs.json" \
  -j="json_files/figure_${fig}a_garnish_kwargs.json";
echo "figure ${fig}b"
python CreateFigure.py \
  -d=${df_spr} \
  -o=${o_images_dir} \
  -r=${rejections} \
  -f=${fig} \
  -l=SentenceType:SRC \
  -i="json_files/figure_${fig}b_plot_kwargs.json" \
  -j="json_files/figure_${fig}b_garnish_kwargs.json";

echo "figure A8a A8b A9a A9b"
python CreateDeps.py -o=${o_images_dir};

fig="A10"
echo "figure ${fig}a"
python CreateFigure.py \
  -d=${lm_merged} \
  -o=${o_images_dir} \
  -r=${rejections} \
  -f=${fig} \
  -l=Session:Before \
  -i="json_files/figure_${fig}a_plot_kwargs.json" \
  -j="json_files/figure_${fig}a_garnish_kwargs.json";
echo "figure ${fig}b"
python CreateFigure.py \
  -d=${lm_merged} \
  -o=${o_images_dir} \
  -r=${rejections} \
  -f=${fig} \
  -l=Session:Before \
  -i="json_files/figure_${fig}b_plot_kwargs.json" \
  -j="json_files/figure_${fig}b_garnish_kwargs.json";

echo "table 1"
python CountRC.py -i=${corpus_file} -o=${rc_counts_out};

echo "table 2"
Rscript --vanilla LMER/exp_analysis.R ${csv_exp};

echo "table 3"
Rscript --vanilla LMER/wm_analysis.R ${csv_wm};

echo "table 4 5 A11"
Rscript --vanilla LMER/spr_analysis.R ${csv_spr};
#