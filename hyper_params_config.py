from os.path import join
from argparse import ArgumentParser

data_types = {'g': 'graphemes', 'p': 'phonemes', 'f': 'features'}

resultsFolder = "Results"
evaluationGraphsFolder = join(resultsFolder, "EvaluationGraphs")
predictionFilesFolder = join(resultsFolder, "PredictionFiles")
ckpts_dir = join(resultsFolder, "Checkpoints")
logsFolder = join(resultsFolder, "Logs")
summaryWriterLogsFolder = join(resultsFolder, "SummaryWriterLogs")

# region HPs
# Training hyperparameters
num_epochs = 3 # orignal=50. Note: must be >1 !!!
learning_rate = 3e-4
batch_size = 32 # original=32
LR_patience = 6
LR_factor = 0.82

# Model hyperparameters
encoder_embedding_size = 300 # original=300
decoder_embedding_size = 300 # original=300
hidden_size = 256 # original=256
num_layers = 1
enc_dropout = 0.1 # 0.0 is equivalent to Identity function
dec_dropout = 0.1 # 0.0 is equivalent to Identity function
# endregion HPs

parser = ArgumentParser(description="Parse arguments for linguistic configuration")
parser.add_argument('lang', type=str, choices=['bul', 'fin', 'hun', 'kat', 'lav', 'sqi', 'swc', 'tur'], help="Language to be processed")
parser.add_argument('POS', type=str, choices=['V','N','ADJ'], help="Part of speech to be processed")
parser.add_argument('training_mode', type=str, choices=['form', 'lemma'], help="Can be either form-split or lemma-split")
parser.add_argument('inp_phon_type', type=str, choices=['g','p','f'], help="Phonological representation of the input")
parser.add_argument('out_phon_type', type=str, choices=['g','p','f'], help="Phonological representation of the output")
parser.add_argument('analogy_type', type=str, choices=['src2', 'src1_cross1', 'src1_cross2', 'None'], help='The analogies type to be applied')
parser.add_argument('SEED', type=int, help='Initial seed for all random operations')
parser.add_argument('device_idx', type=str, help='GPU index')
parser.add_argument('--ATTN', action='store_true', help="If True and inp_phon_type=='f', input features are combined in a Self-Attention layer to form a single vector.")
args = parser.parse_args()
lang, POS, SEED, device_idx = args.lang, args.POS, args.SEED, args.device_idx
analogy_type = args.analogy_type
training_mode, inp_phon_type, out_phon_type = args.training_mode, args.inp_phon_type, args.out_phon_type
inp_phon_type, out_phon_type = data_types[inp_phon_type], data_types[out_phon_type]
ANALOGY_MODE = analogy_type!='None'

assert not (analogy_type=='src2' and training_mode=='lemma'), "2-Source is undefined for lemma-split mode!"

PHON_UPGRADED = inp_phon_type=='features'
PHON_REEVALUATE = out_phon_type != 'graphemes' # evaluation at the graphemes-level is also required
PHON_USE_ATTENTION = args.ATTN and PHON_UPGRADED # apply self-attention to the features when extracting the average (olny if PHON_UPGRADED)


# A file to which all logs will be printed. Automatically generated in logsFolder:
all_params_str = f"{lang}_{POS}_{training_mode}_{inp_phon_type[0]}_{out_phon_type[0]}_{analogy_type}_{SEED}_{device_idx}{'_attn' if PHON_USE_ATTENTION else ''}"
log_file = join(logsFolder, all_params_str+'.txt')


settings = f"""Run settings:
- language = {lang}, part-of-speech = {POS}, log file = {log_file}
- split-type = {training_mode}
- input_format = {inp_phon_type}, output_format = {out_phon_type}, phon_upgraded = {PHON_UPGRADED}, phon_self_attention = {PHON_USE_ATTENTION}
- analogy_mode = {ANALOGY_MODE}{f", analogy_type = {analogy_type}" if ANALOGY_MODE else ''}"""
print(settings)
open(log_file, 'w', encoding='utf8').write(settings + '\n')

train_file = join(".data", "Reinflection", f"{lang}.{POS}", f"{lang}.{POS}.{training_mode}.train.tsv")
dev_file =   join(".data", "Reinflection", f"{lang}.{POS}", f"{lang}.{POS}.{training_mode}.dev.tsv")
test_file =  join(".data", "Reinflection", f"{lang}.{POS}", f"{lang}.{POS}.{training_mode}.test.tsv") # used only in testing.py
