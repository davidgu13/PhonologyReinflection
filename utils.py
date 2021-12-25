# The code is based on https://github.com/aladdinpersson/Machine-Learning-Collection/tree/master/ML/Pytorch/more_advanced/Seq2Seq_attention, with some adjustments ;)
from os.path import join
import numpy as np
import torch
import torch_scatter # super important! The link I used for installing it is https://pytorch-geometric.readthedocs.io/en/latest/notes/installation.html#quick-start
from torchtext.legacy.data import Field
from copy import deepcopy

from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
from analogies_phonology_preprocessing import combined, GenericPhonologyProcessing
from hyper_params_config import SEED, inp_phon_type, out_phon_type, device_idx, log_file
from languages_setup import MAX_FEAT_SIZE

device = torch.device(f"cuda:{device_idx}" if torch.cuda.is_available() else "cpu")
torch.manual_seed(SEED)

src_tokenizer = lambda x: x.split(',')
trg_tokenizer = lambda x: x.split(',')

# The acrtual Fields are defined below
# german = Field(tokenize=tokenize_ger, lower=True, init_token="<sos>", eos_token="<eos>")
# english = Field(tokenize=tokenize_eng, lower=True, init_token="<sos>", eos_token="<eos>")

def printF(s:str, fn=log_file):
    print(s)
    open(fn, 'a+', encoding='utf8').write(s + '\n')


def get_abs_offsets(x: torch.Tensor, phon_delim, phon_max_len=MAX_FEAT_SIZE):
    # Given a 1D input tensor, finds the starting indices of all tuples that represent phonological bundles.
    inds = torch.where(x==phon_delim)[0]
    return torch.cat((torch.tensor([inds[0]-phon_max_len], device=device, dtype=inds.dtype), inds+1))

def postprocessBatch(src:torch.Tensor, offsets):
    """
    Takes a tensor of embeddings, and averages the vectors that represent phonological features.
    :param src: a tensor of shape [seq_len, embed_size]. Represents embbedings of the sequence (Emb(x)) or the output of the Self-Attention layer (SelfAttn(Emb(x))).
    :param offsets: the beginnning indices of the phonological features.
    :return: The new tensor, after the averaging. It's shape is [new_seq_len, embed_size].
    """
    M, N = src.shape[0], len(offsets)
    new_len = M-MAX_FEAT_SIZE*N
    assert new_len>0
    offsets -= MAX_FEAT_SIZE*torch.arange(N, device=device) #  = 3 = max_size-1 +1 (counting the phoneme index)
    repeats = torch.ones(new_len, dtype=torch.long, device=device)
    repeats[offsets] = MAX_FEAT_SIZE+1 # 4 = max_size +1
    final_offsets = torch.repeat_interleave(torch.arange(new_len, device=device), repeats)
    new_emb = torch_scatter.segment_mean_coo(src, final_offsets)
    return new_emb


# def pad_to_maxfeats(spl:[[str]], maxLen=MAX_FEAT_SIZE):
#     l = [e.split(',') for e in spl]
#     l = [e+['NA']*(maxLen-len(e)) for e in l]
#     spl = l
#     return spl

# Implement here extended preproc methods that convert the data to the formats required at inp_phon_type and out_phon_type.
# Also, supply some preproc to g-g reinflection (the standard variation), to maintain consistency (see the first code lines).
def phon_ext_src_preproc(x: [str]) -> [str]:
    # Covnert the sample (which can be in Analogies format) to phonemes/features representation. Pad with NA tokens if in features mode.
    if inp_phon_type=='graphemes':
        return x # do nothing
    else:
        new_x, _ = combined.line2phon_line_generic(','.join(x), '', convert_trg=False)
        return new_x

def phon_ext_trg_preproc(x: [str]) -> [str]:
    # Covnert the sample (which can be in Analogies format) to phonemes/features representation. Pad with NA tokens if in features mode.
    if out_phon_type=='graphemes':
        return x # do nothing
    else:
        _, new_x = combined.line2phon_line_generic('', ','.join(x), convert_src=False)
        return new_x

preproc_func_ext = {'src':phon_ext_src_preproc, 'trg':phon_ext_trg_preproc}
srcField = Field(tokenize=src_tokenizer, init_token="<sos>", eos_token="<eos>", preprocessing=preproc_func_ext['src'])
trgField = Field(tokenize=trg_tokenizer, init_token="<sos>", eos_token="<eos>", preprocessing=preproc_func_ext['trg'])


def translate_sentence(model, sentence, german, english, device, max_length=50, return_attn=False):
    # Load german tokenizer
    # spacy_ger = spacy.load("de_core_news_sm")
    # Create tokens using spacy and everything in lower case (which is what our vocab is)
    # if type(sentence) == str:
    #     tokens = [token.text.lower() for token in spacy_ger(sentence)]
    # else:
    #     tokens = [token.lower() for token in sentence]
    assert type(sentence) == list
    tokens = deepcopy(sentence)

    # Add <SOS> and <EOS> in beginning and end respectively
    tokens.insert(0, german.init_token)
    tokens.append(german.eos_token)

    # Go through each german token and convert to an index
    text_to_indices = [german.vocab.stoi[token] for token in tokens]

    # Convert to Tensor
    sentence_tensor = torch.LongTensor(text_to_indices).unsqueeze(1).to(device)

    # Build encoder hidden, cell state
    with torch.no_grad():
        outputs_encoder, hiddens, cells = model.encoder(sentence_tensor)

    outputs = [english.vocab.stoi["<sos>"]]
    attention_matrix = torch.zeros(max_length, max_length)
    for i in range(max_length):
        previous_word = torch.LongTensor([outputs[-1]]).to(device)
        with torch.no_grad():
            output, hiddens, cells, attn = model.decoder(previous_word, outputs_encoder, hiddens, cells, return_attn=return_attn)
            best_guess = output.argmax(1).item()
            if return_attn: attention_matrix[i] = torch.cat((attn.squeeze(), torch.zeros(max_length-attn.shape[0]).to(device)),dim=0)

        outputs.append(best_guess)

        # Model predicts it's the end of the sentence
        if output.argmax(1).item() == english.vocab.stoi["<eos>"]:
            break

    translated_sentence = [english.vocab.itos[idx] for idx in outputs]
    # remove start token
    if return_attn:
        return translated_sentence[1:], attention_matrix[:len(translated_sentence)+2, :len(sentence)+2]
    else:
        return translated_sentence[1:]

def bleu(data, model, german:Field, english:Field, device, converter:GenericPhonologyProcessing=None, output_file=''):
    sources, targets, outputs = [], [], []
    morph_sources, morph_targets, morph_outputs = [], [], [] # only necessary if phon_mode

    for example in data:
        src = vars(example)["src"]
        trg = vars(example)["trg"]

        prediction = translate_sentence(model, src, german, english, device)
        prediction = prediction[:-1]  # remove <eos> token

        sources.append(src)
        targets.append(trg) # instead of .append([trg])
        outputs.append(prediction)

    # Count also Accuracy. Ignore <eos>, obviously.

    accs, EDs = zip(*[(t == o, editDistance(t, o)) for t, o in zip(targets, outputs)])
    acc, res = np.mean(accs), np.mean(EDs)

    if converter is not None:
        # Calculate acc + ed on morphological conversions
        for s,t,o in zip(sources, targets, outputs):
            src_morph, trg_morph, pred_morph = converter.phon_elements2morph_elements_generic(s, t, o)
            # morph_sources.append(src_morph)
            morph_targets.append(trg_morph)
            morph_outputs.append(pred_morph)

        morph_accs, morph_EDs = zip(*[(t==o, editDistance(t, o)) for t,o in zip(morph_targets, morph_outputs)])
        morph_acc, morph_res = np.mean(morph_accs), np.mean(morph_EDs)
        if output_file:
            write_predictions(output_file, morph_targets, morph_outputs, morph_accs, morph_EDs, sources=sources, phon_accs=accs, phon_eds=EDs, phon_targets=targets, phon_preds=outputs)
        returned = res, acc, morph_res, morph_acc
    else:
        if output_file:
            targets = [''.join(t) for t in targets] # convert to readable
            outputs = [''.join(o) for o in outputs] # convert to readable
            write_predictions(output_file, targets, outputs, accs, EDs, sources=sources)
        returned = res, acc
    return returned


def write_predictions(path, targets, preds, morph_accs, morph_eds, sources=None, phon_accs=None, phon_eds=None, phon_targets=None, phon_preds=None):
    assert bool(phon_accs)==bool(phon_eds), "Either both or none of phon_accs & phon_eds should be supplied!"
    printF(f"Predictions are being written to {path}.")

    with open(path, "w", encoding='utf8') as f:
        f.write(f"Predictions file: generated on {get_time_now_str(allow_colon=True)}.\n")
        if sources is None:
            it = zip(targets, preds, morph_accs, morph_eds)
            if bool(phon_accs) and bool(phon_eds):
                for (t, p, m_acc, m_ed), (p_t, p_p, p_acc, p_ed) in zip(it, zip(phon_targets, phon_preds, phon_accs, phon_eds)):
                    f.write(f"Target: {t} ; Phon-Target: {p_t} ; Pred: {p} ; Phon-Pred: {p_p} ; Morph-Exact: {'Yes' if m_acc else 'No'} ; Phon-Exact: {'Yes' if p_acc else 'No'} ; Morph-ED = {m_ed} ; Phon-ED = {p_ed}\n")
            else:
                for (t, p, m_acc, m_ed) in it:
                    f.write(f"Target: {t} ; Pred: {p} ; Morph-Exact: {'Yes' if m_acc else 'No'} ; Morph-ED = {m_ed}\n")
        else:
            it = zip(sources, targets, preds, morph_accs, morph_eds)
            if bool(phon_accs) and bool(phon_eds):
                for (s, t, p, m_acc, m_ed), (p_t, p_p, p_acc, p_ed) in zip(it, zip(phon_targets, phon_preds, phon_accs, phon_eds)):
                    f.write(f"Source: {s} ; Target: {t} ; Phon-Target: {p_t} ; Pred: {p} ; Phon-Pred: {p_p} ; Morph-Exact: {'Yes' if m_acc else 'No'} ; Phon-Exact: {'Yes' if p_acc else 'No'} ; Morph-ED = {m_ed} ; Phon-ED = {p_ed}\n")
            else:
                for (s, t, p, m_acc, m_ed) in it:
                    f.write(f"Source: {s} ; Target: {t} ; Pred: {p} ; Morph-Exact: {'Yes' if m_acc else 'No'} ; Morph-ED = {m_ed}\n")

def get_time_now_str(allow_colon:bool):
    from datetime import datetime
    s = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return s if allow_colon else s.replace(':', '')

def save_checkpoint(model, optimizer, filename="my_checkpoint.pth.tar", file_to_delete=""): # modify with https://github.com/pytorch/examples/blob/537f6971872b839b36983ff40dafe688276fe6c3/imagenet/main.py#L237
    if file_to_delete!="":
        from os import remove
        remove(file_to_delete) # delete the last checkpoint (only 1 such file exists).
    checkpoint = {"state_dict": model.state_dict(), "optimizer": optimizer.state_dict(),}
    printF(f"=> Saving checkpoint called {filename}")
    torch.save(checkpoint, filename)

def load_checkpoint(checkpoint, model, optimizer, verbose=True):
    if verbose: printF("=> Loading checkpoint")
    model.load_state_dict(checkpoint["state_dict"])
    optimizer.load_state_dict(checkpoint["optimizer"])

def editDistance(str1, str2):
    """Simple Levenshtein implementation"""
    table = np.zeros([len(str2) + 1, len(str1) + 1])
    for i in range(1, len(str2) + 1):
        table[i][0] = table[i - 1][0] + 1
    for j in range(1, len(str1) + 1):
        table[0][j] = table[0][j - 1] + 1
    for i in range(1, len(str2) + 1):
        for j in range(1, len(str1) + 1):
            if str1[j - 1] == str2[i - 1]:
                dg = 0
            else:
                dg = 1
            table[i][j] = min(table[i - 1][j] + 1, table[i][j - 1] + 1, table[i - 1][j - 1] + dg)
    return int(table[len(str2)][len(str1)])

def showAttention(input_sentence, output_words, attentions, fig_name="Attention Weights.png"):
    # Set up figure with colorbar
    fig = plt.figure(figsize=(20,20))
    ax = fig.add_subplot(111)
    cax = ax.matshow(attentions.numpy(), cmap='bone')
    fig.colorbar(cax)

    # Set up axes
    ax.set_xticklabels([''] + input_sentence + ['<eos>'])#, rotation=90)
    ax.set_yticklabels([''] + output_words)

    # Show label at every tick
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    # plt.show()
    plt.savefig(fig_name)


def write_dataset(p, dataset, test_mode=False):
    """
    Takes the dataset and writes it to the given path.
    :param p: target path
    :param dataset: an iterable object of (lemma, form, feat) triplets
    :param test_mode: if true, the forms are not written (covered), as in the Inflection task
    :return:
    """
    with open(p, mode='w', encoding='utf8') as f:
        for sample in dataset:
            lemma, form, feat = sample
            if test_mode:
                f.write(f"{lemma}\t{feat}\n")
            else:
                f.write(f"{lemma}\t{form}\t{feat}\n")