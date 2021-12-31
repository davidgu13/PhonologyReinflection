# This file links between hyper_params_config.py and utils.py & main.py
from os import mkdir
from os.path import join, isdir
from torch.utils.tensorboard import SummaryWriter  # to print to tensorboard
from hyper_params_config import lang, POS, training_mode, inp_phon_type, out_phon_type, analogy_type, SEED, device_idx,\
    PHON_USE_ATTENTION, PHON_UPGRADED, ANALOGY_MODE
from hyper_params_config import num_epochs, learning_rate, batch_size, encoder_embedding_size, decoder_embedding_size, hidden_size

user_params_config = f"{lang}_{POS}_{training_mode}_{inp_phon_type[0]}_{out_phon_type[0]}_{analogy_type}_{SEED}" \
                     f"_{device_idx}{'_attn' if PHON_USE_ATTENTION else ''}" # used below for files naming

user_params_config_to_print = f"""Run arguments configuration:
- language = {lang}, part-of-speech = {POS}
- split-type = {training_mode}
- input_format = {inp_phon_type}, output_format = {out_phon_type}, phon_upgraded = {PHON_UPGRADED}, phon_self_attention = {PHON_USE_ATTENTION}
- analogy_mode = {ANALOGY_MODE}{f", analogy_type = {analogy_type}" if ANALOGY_MODE else ''}"""

train_file = join(".data", "Reinflection", f"{lang}.{POS}", f"{lang}.{POS}.{training_mode}.train.tsv")
dev_file =   join(".data", "Reinflection", f"{lang}.{POS}", f"{lang}.{POS}.{training_mode}.dev.tsv")
test_file =  join(".data", "Reinflection", f"{lang}.{POS}", f"{lang}.{POS}.{training_mode}.test.tsv") # used only in testing.py

# region output folders
resultsFolder = "Results"
evaluation_graphs_folder =  join(resultsFolder, "EvaluationGraphs")
prediction_files_folder =   join(resultsFolder, "PredictionFiles")
model_checkpoints_folder =  join(resultsFolder, "Checkpoints")
logs_folder =               join(resultsFolder, "Logs")
summaryWriter_logs_folder = join(resultsFolder, "SummaryWriterLogs")

if not isdir(evaluation_graphs_folder):  mkdir(evaluation_graphs_folder)
if not isdir(prediction_files_folder):   mkdir(prediction_files_folder)
if not isdir(model_checkpoints_folder):  mkdir(model_checkpoints_folder)
if not isdir(logs_folder):               mkdir(logs_folder)
if not isdir(summaryWriter_logs_folder): mkdir(summaryWriter_logs_folder)
# endregion output folders

def get_time_now_str(allow_colon:bool):
    from datetime import datetime
    s = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return s if allow_colon else s.replace(':', '')
time_stamp = get_time_now_str(allow_colon=False) # the time when the run started
user_params_with_time_stamp = f"{time_stamp}_{user_params_config}"

# region output files
evaluation_graphs_file = join(evaluation_graphs_folder, f"EvaluationGraph_{user_params_with_time_stamp}.png")
model_checkpoint_file =  join(model_checkpoints_folder, f"Model_Checkpoint_{user_params_with_time_stamp}.pth.tar")
logs_file =              join(logs_folder, f"{user_params_with_time_stamp}.txt")
predictions_file =       join(prediction_files_folder, f"Predictions_{user_params_with_time_stamp}.txt")
# endregion output files

def printF(s:str, fn=logs_file):
    print(s)
    open(fn, 'a+', encoding='utf8').write(s + '\n')

printF(user_params_config_to_print)
printF(f"""
Logs file: {logs_file}
Predictions file: {predictions_file}
Loss & Accuracy graph: {evaluation_graphs_file}
""")

hyper_params_to_print = f"""#epochs = {num_epochs},
lr = {learning_rate},
batch = {batch_size},
encoder_embed_size = {encoder_embedding_size},
decoder_embed_size = {decoder_embedding_size},
hidden_size = {hidden_size},
time_stamp = {time_stamp}"""

printF(f"- Hyper-Params: {hyper_params_to_print}")
printF("- Defining a SummaryWriter object")
# use Tensorboard to get nice loss plot
hyper_params_to_print = hyper_params_to_print.replace("\n", " ") # more compact + needed later
summary_writer = SummaryWriter(summaryWriter_logs_folder, comment=hyper_params_to_print)
