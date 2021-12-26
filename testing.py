import random
import os
from torchtext.legacy.data import TabularDataset
from datetime import timedelta
from torch import load
from torch.optim import Adam
import time

from analogies_phonology_preprocessing import combined_phonology_processor
from utils import bleu, load_checkpoint, srcField, trgField, device
from network import Encoder, Decoder, Seq2Seq
from hyper_params_config import training_mode, inp_phon_type, out_phon_type, PHON_REEVALUATE, PHON_UPGRADED, ANALOGY_MODE,\
    analogy_type, learning_rate, encoder_embedding_size, train_file, dev_file, test_file, \
    decoder_embedding_size, hidden_size, num_layers, enc_dropout, dec_dropout, predictionFilesFolder

def main():
    t0=time.time()
    ckpt_path = os.path.join("Results/Checkpoints", "ckpt_41_2021-09-01 123810_lemma_src1_cross1.pth.tar")
    preds_file = os.path.join(predictionFilesFolder, os.path.split(ckpt_path)[1].replace(".pth.tar", ".txt"))
    assert training_mode in ckpt_path
    if PHON_REEVALUATE: assert '_phon' in ckpt_path
    if ANALOGY_MODE: assert analogy_type in ckpt_path

    print(f"\nConfiguration: split-type = {training_mode}, inp_phon_type = {inp_phon_type}, analogy_mode = {ANALOGY_MODE}\n"
          f"Trained on file: {train_file}\n"
          f"Validation file: {dev_file}\n"
          f"Checkpoint file: {ckpt_path}")

    train_data, dev_data = TabularDataset.splits(path='', train=train_file, validation=dev_file,
                                                 fields=[("src", srcField), ("trg", trgField)], format='tsv') # test data is out of the game.

    srcField.build_vocab(train_data, dev_data) # no limitation of max_size or min_freq is needed.
    trgField.build_vocab(train_data, dev_data) # no limitation of max_size or min_freq is needed.

    input_size_encoder = len(srcField.vocab)
    input_size_decoder = len(trgField.vocab)
    output_size = len(trgField.vocab)

    random.seed(42)
    encoder_net = Encoder(input_size_encoder, encoder_embedding_size, hidden_size, num_layers, enc_dropout).to(device)
    decoder_net = Decoder(input_size_decoder, decoder_embedding_size, hidden_size, output_size, num_layers, dec_dropout,).to(device)
    model2 = Seq2Seq(encoder_net, decoder_net).to(device)
    optimizer2 = Adam(model2.parameters(), lr=learning_rate)
    print("Loading the model")
    ckpt = load(ckpt_path)
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
    print("Note: not tested in the new version!")
    main()