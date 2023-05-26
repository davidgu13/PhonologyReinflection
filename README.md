# ReinflectionPhonologyLSTM

Repo for the LSTM model we used in the paper [**Morphological Inflection with Phonological Features**](https://github.com/OnlpLab/InflectionWithPhonology). Based on the model by [Silfverberg & Hulden](https://github.com/mpsilfve/pcfp-data).

## Running Instructions
See the dependencies at `requirements.txt`.

### Using the Phonology Component
If you wish to experiment with a new language, provide a list of the alphabet and their corresponding phonemes. Optionally, you can add methods for manual conversions (digraphs and trigraphs are supported). Also, you could provide a method for data normalizing.

### Training
For a new language, you need to first generate datasets (otherwise, skip to stage 4):
1. Add an inflections file (in UniMorph format) to the folder `.data/RawData`.
2. Provide g2p & p2g methods for the language, as described above.
3. Run `generate_reinflection_datasets.py ${lang_name} ${# samples}` to generate folders in .data/Reinflection for each POS found for the inflections file, and also train, dev & test reinflection datasets (in 0.8-0.1-0.1 ratio) -- 3 in form-split, and, if possible, 3 in lemma-split.
4. The model works with TSV-format files. For that, run the script `reinflection2TSV.py ${lang_name} ${POS} ${training_mode}`.
5. Now you can run the model! Configure the hyper-parameters if needed and run `main.py` with the required parameters.

The algorithm trains and prints updates to the Console and evaluates the performance on dev set on every epoch. If the output format is features or phonemes, 2 evaluations will be made. Finally, the best model is selected (according to the dev-accuracy), it is applied on the test set.

The script produces output files in each of the folders `./Results/{Logs, EvaluationGraphs, Checkpoints, Predictions}` (logs file, Accuracy & ED curves, .tar file and predictions on the test set).
All the above files' names include the run's parameters + time stamp, for identification.

### Testing the Model
Run `test_single_model.py` with the model's parameters. The script loads and applies it on the dev and test sets, and then prints the results to the Console, writes them to a "Test-Logs" file in `./Results/Logs`, and writes the predictions in `./Results/Predictions`.

