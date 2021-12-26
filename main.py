import random
import torch
import torch.nn as nn
import torch.optim as optim
import utils
from utils import translate_sentence, bleu, save_checkpoint, load_checkpoint, srcField, trgField, device, plt, get_time_now_str, printF
from torch.utils.tensorboard import SummaryWriter  # to print to tensorboard
from torchtext.legacy.data import BucketIterator, TabularDataset
from network import Encoder, Decoder, Seq2Seq
import os
from analogies_phonology_preprocessing import combined_phonology_processor
# Definition of tokenizers, Fields and device were moved to utils
import time
from datetime import timedelta
from hyper_params_config import training_mode, inp_phon_type, out_phon_type, PHON_REEVALUATE, SEED, POS, num_epochs,\
    learning_rate, batch_size, LR_patience, LR_factor, encoder_embedding_size, decoder_embedding_size, hidden_size,\
    num_layers, enc_dropout, dec_dropout, ckpts_dir, train_file, dev_file, all_params_str,\
    evaluationGraphsFolder, predictionFilesFolder, summaryWriterLogsFolder


def show_readable_triplet(src, trg, pred):
    # Presents the triplet in a more tidy way (no converting)
    src_print = [e.replace(',',';' if POS in e else ',' if inp_phon_type=='features' else '') for e in ','.join(src).split(',+,')]
    trg_print, pred_print = (','.join(trg), ','.join(pred)) if out_phon_type=='features' else (''.join(trg), ''.join(pred))
    return src_print, trg_print, pred_print

def main():
    # Note: the arguments parsing occurs globally at hyper_params_config.py
    t0=time.time()
    random.seed(SEED)
    torch.manual_seed(SEED)

    printF("- Generating the datasets:")
    printF(f"\ttrain_file = {train_file}, dev_file = {dev_file}")
    train_data, dev_data = TabularDataset.splits(path='', train=train_file, validation=dev_file,
                             fields=[("src", srcField), ("trg", trgField)], format='tsv') # test data is out of the game.
    printF("- Building vocabularies")
    srcField.build_vocab(train_data, dev_data) # no limitation of max_size or min_freq is needed.
    trgField.build_vocab(train_data, dev_data) # no limitation of max_size or min_freq is needed.

    ### We're ready to define everything we need for training our Seq2Seq model ###
    printF("- Defining hyper-params")
    save_model = True
    time_stamp = get_time_now_str(allow_colon=False) # the time when the run started
    if not os.path.isdir(evaluationGraphsFolder): os.mkdir(evaluationGraphsFolder)
    if not os.path.isdir(predictionFilesFolder): os.mkdir(predictionFilesFolder)
    if not os.path.isdir(ckpts_dir): os.mkdir(ckpts_dir)
    ckpt_path = os.path.join(ckpts_dir, f"ckpt_{time_stamp}_{all_params_str}.pth.tar")
    preds_file = os.path.join(predictionFilesFolder, f"preds_{time_stamp}_{all_params_str}.txt")

    comment = f"{all_params_str}, epochs={num_epochs}, lr={learning_rate}, batch={batch_size}, embed={encoder_embedding_size}, hidden_size={hidden_size}, time_stamp={time_stamp}"
    printF(f"- Hyper-Params: {comment}")
    printF("- Defining a SummaryWriter object")
    # Tensorboard to get nice loss plot
    writer, summary_step = SummaryWriter(summaryWriterLogsFolder, comment=comment), 0

    printF("- Generating BucketIterator objects")
    train_iterator, dev_iterator = BucketIterator.splits(
        (train_data, dev_data),
        batch_size=batch_size,
        sort_within_batch=True,
        sort_key= lambda x: len(x.src),
        device=device
    )

    input_size_encoder = len(srcField.vocab)
    input_size_decoder = len(trgField.vocab)
    output_size = len(trgField.vocab)

    # region defineNets
    printF("- Constructing networks & optimizer")
    encoder_net = Encoder(input_size_encoder, encoder_embedding_size, hidden_size, num_layers, enc_dropout).to(device)
    decoder_net = Decoder(input_size_decoder, decoder_embedding_size, hidden_size, output_size, num_layers, dec_dropout,).to(device)
    model = Seq2Seq(encoder_net, decoder_net).to(device)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    printF("- Defining some more stuff...")
    pad_idx = srcField.vocab.stoi["<pad>"]
    criterion = nn.CrossEntropyLoss(ignore_index=pad_idx)
    lr_scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', patience=LR_patience, verbose=True, factor=LR_factor) # mode='max' bc we want to maximize the accuracy
    # endregion defineNets

    indices = random.sample(range(len(dev_data)), k=10)
    examples_for_printing = [dev_data.examples[i] for i in indices] # For a more interpretable evaluation, we apply translate_sentence on 10 samples.
    accs_phon, EDs_phon, accs_morph, EDs_morphs, best_measures = [], [], [], [], []
    max_morph_acc, ED_phon, accuracy_phon, ED_morph, accuracy_morph = -0.001, -0.001, -0.001, -0.001, -0.001

    printF("Let's begin training!\n")
    for epoch in range(1, num_epochs + 1):
        printF(f"[Epoch {epoch} / {num_epochs}] (initial hyper-params: {comment})")
        printF(f"lr = {optimizer.state_dict()['param_groups'][0]['lr']:.7f}")
        model.train()
        printF(f"Starting the epoch on: {get_time_now_str(allow_colon=True)}.")
        for batch_idx, batch in enumerate(train_iterator):
            # Get input and targets and get to cuda
            inp_data = batch.src.to(device)
            target = batch.trg.to(device)

            # Forward prop
            output = model(inp_data, target)

            # Output is of shape (trg_len, batch_size, output_dim) but Cross Entropy Loss
            # doesn't take input in that form. For example if we have MNIST we want to have
            # output to be: (N, 10) and targets just (N). Here we can view it in a similar
            # way that we have output_words * batch_size that we want to send in into
            # our cost function, so we need to do some reshapin. While we're at it
            # Let's also remove the start token while we're at it
            output = output[1:].reshape(-1, output.shape[2])
            target = target[1:].reshape(-1)

            optimizer.zero_grad()
            loss = criterion(output, target)

            # Back prop
            loss.backward()

            # Clip to avoid exploding gradient issues, makes sure grads are
            # within a healthy range
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1)

            # Gradient descent step
            optimizer.step()

            # Plot to tensorboard
            writer.add_scalar("Training loss", loss, global_step=summary_step)
            summary_step += 1

        model.eval()
        # Evaluate the performances on examples_for_printing
        for i,ex in enumerate(examples_for_printing, start=1):
            translated_sent = translate_sentence(model, ex.src, srcField, trgField, device, max_length=50)
            if translated_sent[-1]=='<eos>':
                translated_sent = translated_sent[:-1]
            src, trg, pred = ex.src, ex.trg, translated_sent # all the outputs are [str]; represents phonological stuff only if out_phon_type!='graphemes'
            phon_ed = utils.editDistance(trg, pred)
            src_print, trg_print, pred_print = show_readable_triplet(src, trg, pred)
            printF(f"{i}. input: {src_print} ; gold: {trg_print} ; pred: {pred_print} ; ED = {phon_ed}")

            # The next steps:
            # 1. If needed, convert the samples to a readable format (graphemes). Handle separately sources and trgs-preds.
            # 2. If needed, supply another evaluation of the prediction (for now, only graphemes-evaluation)
            # 3. Print the results. Refer to whether 1. and 2. were applied.

            # Convert non-graphemic formats to words
            if inp_phon_type!='graphemes' or out_phon_type!='graphemes':
                src_morph, trg_morph, pred_morph = combined_phonology_processor.phon_elements2morph_elements_generic(src, trg, pred)
                if out_phon_type!='graphemes': # another evaluation metric is needed; the source format is irrelevant
                    morph_ed_print = utils.editDistance(trg_morph, pred_morph)
                    printF(f"{i}. input_morph: {src_morph} ; gold_morph: {trg_morph} ; pred_morph: {pred_morph} ; morphlvl_ED = {morph_ed_print}\n")
                else:
                    printF(f"{i}. input_morph: {src_morph} ; gold_morph: {''.join(trg_morph)} ; pred_morph: {''.join(pred_morph)}\n")


        if PHON_REEVALUATE:
            ED_phon, accuracy_phon, ED_morph, accuracy_morph = bleu(dev_data, model, srcField, trgField, device, converter=combined_phonology_processor, output_file=preds_file)
            writer.add_scalar("Dev set Phon-Accuracy", accuracy_phon, global_step=epoch)
            extra_str = f"; avgED_phon = {ED_phon}; avgAcc_phon = {accuracy_phon}"
            accs_phon.append(accuracy_phon)
            EDs_phon.append(ED_phon)
        else:
            ED_morph, accuracy_morph = bleu(dev_data, model, srcField, trgField, device)
            extra_str=''
        writer.add_scalar("Dev set Morph-Accuracy", accuracy_morph, global_step=epoch)
        printF(f"avgEDmorph = {ED_morph}; avgAcc_morph = {accuracy_morph}{extra_str}\n")

        accs_morph.append(accuracy_morph)
        EDs_morphs.append(ED_morph)
        printF(f"Ending the epoch on: {get_time_now_str(allow_colon=True)}.")

        # region model_selection
        if save_model and epoch==1: # first epoch
            save_checkpoint(model, optimizer, filename=ckpt_path.replace('ckpt',f'ckpt_1'))
        elif save_model:
            # Check whether the last morph_accuracy was higher than the max. If yes, replace the ckpt with the last one.
            if accuracy_morph > max_morph_acc:
                max_morph_acc = accuracy_morph
                best_measures = [ED_phon, accuracy_phon, ED_morph, accuracy_morph, epoch] if PHON_REEVALUATE else [ED_morph, accuracy_morph, epoch]
                assert len([f for f in os.listdir(ckpts_dir) if time_stamp in f])==1
                ckpt_to_delete = [os.path.join(ckpts_dir, f) for f in os.listdir(ckpts_dir) if time_stamp in f][0]
                temp_ckpt_name = ckpt_path.replace('ckpt',f'ckpt_{epoch}')
                save_checkpoint(model, optimizer, filename=temp_ckpt_name, file_to_delete=ckpt_to_delete)
            else: printF(f"Checkpoint didn't change. Current best (Accuracy={max_morph_acc}) achieved at epoch {best_measures[-1]}")
        # endregion model_selection
        lr_scheduler.step(accuracy_morph) # update only after model_selection

    # Load the best checkpoint and apply it on the dev set one last time. Report the results and make sure they are equal to best_measures.
    printF("Loading the best model")
    ckpt_path = [os.path.join(ckpts_dir, f) for f in os.listdir(ckpts_dir) if time_stamp in f][0]
    load_checkpoint(torch.load(ckpt_path), model, optimizer)
    printF("Applying model on validation set")
    if PHON_REEVALUATE:
        ED_phon, accuracy_phon, ED_morph, accuracy_morph = bleu(dev_data, model, srcField, trgField, device, converter=combined_phonology_processor, output_file=preds_file)
        assert [ED_phon, accuracy_phon, ED_morph, accuracy_morph] == best_measures[:-1] # sanity check
        printF(f"Phonological level: ED score on dev set is {ED_phon}. Avg-Accuracy is {accuracy_phon}.")
    else:
        ED_morph, accuracy_morph = bleu(dev_data, model, srcField, trgField, device, output_file=preds_file)
        assert [ED_morph, accuracy_morph] == best_measures[:-1] # sanity check, for debugging purposes
    printF(f"Morphological level: ED = {ED_morph}, Avg-Accuracy = {accuracy_morph}.")

    # region plotting
    plt.figure(figsize=(10,8)), plt.suptitle(f'Development Set Results, {training_mode}-split')
    if PHON_REEVALUATE:
        plt.subplot(221), plt.title("Phon-ED"), plt.plot(EDs_phon)
        plt.subplot(222), plt.title("Phon-Acc"), plt.plot(accs_phon)
        plt.subplot(223), plt.title("Morph-ED"), plt.plot(EDs_morphs)
        plt.subplot(224), plt.title("Morph-Acc"), plt.plot(accs_morph)
    else:
        plt.subplot(121), plt.title("Morph-Acc"), plt.plot(accs_morph)
        plt.subplot(122), plt.title("Morph-ED"), plt.plot(EDs_morphs)
    img_path = os.path.join("Results/EvaluationGraphs", f"EvaluationGraph_{time_stamp}_{all_params_str}.png")
    printF(f'Saving the plot of the results on {img_path}')
    plt.savefig(img_path)
    # endregion plotting
    printF(f'Elapsed time is {str(timedelta(seconds=time.time()-t0))}')


if __name__ == '__main__':
    main()