import time
from os.path import join
from datetime import timedelta, datetime
from torchtext.legacy.data import TabularDataset
from torch import load

import hyper_params_config as hp
from functools import partial

def printF(s:str, fn):
    print(s)
    open(fn, 'a+', encoding='utf8').write(s + '\n')

def set_configuration_hyper_parameters(device_idx):
    """
    parse the hyper-parameters, as well as the run configuration, from the model's file name. Based on the format:
    f"Model_Checkpoint_{epoch}_{time_stamp}_{lang}_{POS}_{training_mode}_{inp_phon_type}_{out_phon_type}_{analogy_type}_{SEED}_{device_idx}.pth.tar",
    for example "Model_Checkpoint_50_2022-01-07 080812_fin_N_form_f_p_None_42_0_attn.pth.tar"
    :return: time_stamp, the only parameter that is not defined as a parameter.
    """
    hyper_parameters = model_file.replace("Model_Checkpoint_","").replace(".pth.tar","").split("_")
    model_time_stamp, lang, POS, training_mode, input_type, output_type, analogy_type = hyper_parameters[1:8]
    if analogy_type == 'src1':
        analogy_type = 'src1_cross1'
        seed = int(hyper_parameters[9])
    else:
        seed = int(hyper_parameters[8])

    phon_use_attention = hyper_parameters[-1] == 'attn'

    hp.lang = lang
    hp.POS = POS
    hp.training_mode = training_mode
    hp.inp_phon_type = hp.data_types[input_type]
    hp.out_phon_type = hp.data_types[output_type]
    hp.ANALOGY_MODE = analogy_type!='None'
    hp.analogy_type = analogy_type
    hp.SEED = seed
    hp.device_idx = device_idx
    hp.PHON_USE_ATTENTION = phon_use_attention
    hp.PHON_UPGRADED = hp.inp_phon_type=='features'
    hp.PHON_REEVALUATE = hp.out_phon_type != 'graphemes' # evaluation at the graphemes-level is also required
    return model_time_stamp

def print_testing_configuration(test_printF, train_file, dev_file, test_file, model_full_path, test_log_file, test_predictions_file):
    test_printF(f"""\nTesting Configuration:
- language = {hp.lang}, part-of-speech = {hp.POS}
- split-type = {hp.training_mode}
- input_format = {hp.inp_phon_type}, output_format = {hp.out_phon_type}, phon_upgraded = {hp.PHON_UPGRADED}, phon_self_attention = {hp.PHON_USE_ATTENTION}
- analogy_mode = {hp.ANALOGY_MODE}{f", analogy_type = {hp.analogy_type}" if hp.ANALOGY_MODE else ''}
- seed = {hp.SEED}
Trained on file: {train_file}"
Validated on file: {dev_file}"
Gonna test on file: {test_file}"
Model checkpoint file: {model_full_path}
Test-Log file: {test_log_file}
Test-Predictions file: {test_predictions_file}\n\n
Original run's parameters:""")

def get_train_dev_test_files():
    if hp.analogy_type == 'None':
        train_file = join(".data", "Reinflection", f"{hp.lang}.{hp.POS}", f"{hp.lang}.{hp.POS}.{hp.training_mode}.train.tsv")
        dev_file =   join(".data", "Reinflection", f"{hp.lang}.{hp.POS}", f"{hp.lang}.{hp.POS}.{hp.training_mode}.dev.tsv")
        test_file =  join(".data", "Reinflection", f"{hp.lang}.{hp.POS}", f"{hp.lang}.{hp.POS}.{hp.training_mode}.test.tsv") # used only in testing.py
    else: # hp.analogy_type == 'src1_cross1'
        train_file = join(".data", "Reinflection", f"{hp.lang}.{hp.POS}", "src1_cross1", f"{hp.lang}.{hp.POS}.{hp.training_mode}.train.src1_cross1.tsv")
        dev_file =   join(".data", "Reinflection", f"{hp.lang}.{hp.POS}", "src1_cross1", f"{hp.lang}.{hp.POS}.{hp.training_mode}.dev.src1_cross1.tsv")
        test_file =  join(".data", "Reinflection", f"{hp.lang}.{hp.POS}", "src1_cross1", f"{hp.lang}.{hp.POS}.{hp.training_mode}.test.src1_cross1.tsv") # used only in testing.py
    return train_file, dev_file, test_file

def delete_unwanted_log_file(folder_path, model_configuration_string: str):
    from os import remove

    def add_and_replace_time_stamp(src_string:str, old_timestamp: str, seconds_to_add: int) -> str:
        dt = datetime.strptime(old_timestamp, "%Y-%m-%d %H%M%S")
        dt += timedelta(0, seconds_to_add)
        return src_string.replace(old_timestamp, dt.strftime("%Y-%m-%d %H%M%S"))

    log_file_to_remove = join(folder_path, f"Logs_{model_configuration_string}.txt")
    try:
        remove(log_file_to_remove)
    except FileNotFoundError:
        seconds, done = 5, False
        for _ in range(seconds):
            if not done:
                try:
                    model_configuration_string = add_and_replace_time_stamp(model_configuration_string,
                                                model_configuration_string[:17], 1)
                    log_file_to_remove = join(folder_path, f"Logs_{model_configuration_string}.txt")
                    remove(log_file_to_remove)
                    done = True
                except FileNotFoundError: pass
            else: break



def main(model_file, device_idx):
    t0=time.time()
    inference_time_stamp = datetime.now().strftime("%Y-%m-%d %H%M%S")
    model_time_stamp = set_configuration_hyper_parameters(device_idx)

    model_full_configuration_string = f"{model_time_stamp}_{hp.lang}_{hp.POS}_{hp.training_mode}_{hp.inp_phon_type[0]}_" \
     f"{hp.out_phon_type[0]}_{hp.analogy_type}_{hp.SEED}_{hp.device_idx}{'_attn' if hp.PHON_USE_ATTENTION else ''}" # the unique ID of this run

    model_full_path = join("Results", "Checkpoints", model_file)
    test_log_file = join("Results", "Logs", model_file.replace("Model_Checkpoint", f"Test-Logs-{inference_time_stamp}-for-model").replace(".pth.tar", ".txt"))
    test_predictions_file = join("Results", "PredictionFiles", f"Test-Predictions-{inference_time_stamp}-for-model_{model_full_configuration_string}.txt")

    test_printF = partial(printF, fn=test_log_file)

    train_file, dev_file, test_file = get_train_dev_test_files()

    print_testing_configuration(test_printF, train_file, dev_file, test_file, model_full_path, test_log_file, test_predictions_file)

    from utils import bleu, srcField, trgField, device
    from network import Encoder, Decoder, Seq2Seq

    train_data, dev_data, test_data = TabularDataset.splits(path='', train=train_file, validation=dev_file,
        test=test_file, fields=[("src", srcField), ("trg", trgField)], format='tsv') # test data is out of the game.

    srcField.build_vocab(train_data, dev_data) # no limitation of max_size or min_freq is needed.
    trgField.build_vocab(train_data, dev_data) # no limitation of max_size or min_freq is needed.

    input_size_encoder = len(srcField.vocab)
    input_size_decoder = len(trgField.vocab)
    output_size = len(trgField.vocab)

    encoder_net = Encoder(input_size_encoder, hp.encoder_embedding_size, hp.hidden_size, hp.num_layers, hp.enc_dropout).to(device)
    decoder_net = Decoder(input_size_decoder, hp.decoder_embedding_size, hp.hidden_size, output_size, hp.num_layers, hp.dec_dropout,).to(device)
    model = Seq2Seq(encoder_net, decoder_net)

    test_printF("Loading the model")
    model.load_state_dict(load(model_full_path, map_location=device)["state_dict"])
    model.to(device)

    model.eval()
    for name, test_set in zip(['dev', 'test'], [dev_data, test_data]):

        test_printF(f"Applying on {name} set")
        if hp.PHON_REEVALUATE:
            from analogies_phonology_preprocessing import combined_phonology_processor
            ED_phon, accuracy_phon, ED_morph, accuracy_morph = bleu(test_set, model, srcField, trgField, device,
                                    converter=combined_phonology_processor, output_file=test_predictions_file)
            test_printF(f"Phonological level: ED score on {name} set is {ED_phon}. Avg-Accuracy is {accuracy_phon}.")
        else:
            ED_morph, accuracy_morph = bleu(test_set, model, srcField, trgField, device, output_file=test_predictions_file)
        test_printF(f"Morphological level: ED = {ED_morph}, Avg-Accuracy = {accuracy_morph}.\n")

    delete_unwanted_log_file(join("Results", "Logs"), model_full_configuration_string.replace(model_time_stamp, inference_time_stamp))

    test_printF(f'Elapsed time is {str(timedelta(seconds=time.time()-t0))}. Goodbye!')


if __name__ == '__main__':
    model_file = "Model_Checkpoint_49_2022-01-14 213919_sqi_V_form_f_p_src1_cross1_21_2_attn.pth.tar"
    device_idx = 0
    main(model_file, device_idx)
