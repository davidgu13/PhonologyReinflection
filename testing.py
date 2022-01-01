import random, os, time
from datetime import timedelta
from torchtext.legacy.data import TabularDataset
from torch import load
from torch.optim import Adam
from analogies_phonology_preprocessing import combined_phonology_processor
from utils import bleu, load_checkpoint, srcField, trgField, device
from network import Encoder, Decoder, Seq2Seq
from hyper_params_config import training_mode, out_phon_type, PHON_REEVALUATE, PHON_UPGRADED, ANALOGY_MODE,\
    analogy_type, learning_rate, encoder_embedding_size, decoder_embedding_size, hidden_size, \
    num_layers, enc_dropout, dec_dropout, SEED, data_types
import hyper_params_config as hp
from run_setup import train_file, dev_file, test_file, prediction_files_folder


def main(model_file):
    t0=time.time()
    model_checkpoint_file = os.path.join("Results", "Checkpoints", model_file)
    # based on the structure f""Model_Checkpoint_{epoch}_{time_stamp}_{lang}_{POS}_{training_mode}_{inp_phon_type}_{out_phon_type}_{analogy_type}_{SEED}_{device_idx}.pth.tar""
    time_stamp, lang, POS, training_mode, inp_type, out_type = model_file.replace("Model_Checkpoint_","").replace(".pth.tar","").split("_")[1:7]
    hp.inp_phon_type = data_types[inp_type]
    hp.out_phon_type = data_types[out_type]
    # TODO: Note: this script won't work because all the hyper-params should be re-configured according to the model's
    #  name. In order to fix the problem, replace all explicit usage of the HP variables with `hp.{VarName}` in all files!


    preds_file = os.path.join(prediction_files_folder, os.path.split(model_checkpoint_file)[1].replace(".pth.tar", ".txt"))
    assert training_mode in model_checkpoint_file
    assert analogy_type in model_checkpoint_file

    print(f"""\nTesting Configuration: split-type = {training_mode}, inp_phon_type = {hp.inp_phon_type}, analogy_mode = {ANALOGY_MODE}"
"Trained on file: {train_file}"
"Validation file: {dev_file}"
"Test file: {test_file}"
"Checkpoint file: {model_checkpoint_file}""")

    train_data, dev_data = TabularDataset.splits(path='', train=train_file, validation=dev_file,
                 fields=[("src", srcField), ("trg", trgField)], format='tsv') # test data is out of the game.

    srcField.build_vocab(train_data, dev_data) # no limitation of max_size or min_freq is needed.
    trgField.build_vocab(train_data, dev_data) # no limitation of max_size or min_freq is needed.

    input_size_encoder = len(srcField.vocab)
    input_size_decoder = len(trgField.vocab)
    output_size = len(trgField.vocab)

    random.seed(SEED)
    encoder_net = Encoder(input_size_encoder, encoder_embedding_size, hidden_size, num_layers, enc_dropout).to(device)
    decoder_net = Decoder(input_size_decoder, decoder_embedding_size, hidden_size, output_size, num_layers, dec_dropout,).to(device)
    model2 = Seq2Seq(encoder_net, decoder_net).to(device)
    optimizer2 = Adam(model2.parameters(), lr=learning_rate)
    print("Loading the model")
    ckpt = load(model_checkpoint_file)
    load_checkpoint(ckpt, model2, optimizer2, verbose=False)
    print("Applying on validation set")
    if out_phon_type!='graphemes' and not PHON_UPGRADED:
        result_phon, accuracy_phon, result_morph, accuracy_morph = bleu(dev_data, model2, srcField, trgField, device, converter=combined_phonology_processor, output_file=preds_file)
        print(f"Phonological level: ED score on dev set is {result_phon}. Avg-Accuracy is {accuracy_phon}.")
    else:
        result_morph, accuracy_morph = bleu(dev_data, model2, srcField, trgField, device, output_file=preds_file)
    print(f"Morphological level: ED = {result_morph}, Avg-Accuracy = {accuracy_morph}.")

    print(f'Elapsed time is {str(timedelta(seconds=time.time()-t0))}')
    pass

if __name__ == '__main__':
    model_file = "Model_Checkpoint_3_2022-01-01 214817_kat_V_form_f_f_None_42_0.pth.tar"
    main(model_file)