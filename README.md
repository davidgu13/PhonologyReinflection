# PhonologyReinflection

This project studies the use of Phonology for the task of Morphological Reinflection, by David Guriel from the Computer Science dept. at Bar-Ilan university, Israel.

### Providing g2p & p2g Methods
Provide a list of the alphabet and their corresponding phonemes. Provide also methods for manual conversions if needed (see the code examples; the code supports digraphs and trigraphs as well). You could also provide a data-cleaning method. Group the 4 functions as a list `${lang}_components`, and add it to the dictionary `langs_properties`.


### Training a Model on an Existing Dataset:
1. Add the file to the folder `.data/RawData`.
2. Provide g2p & p2g methods for the language, as described above.
3. Run `generate_reinflection_datasets.py ${lang_name} ${# samples}`. This results in folders in .data/Reinflection for each POS found for the language, and also train, dev & test reinflection datasets (in 0.8-0.1-0.1 ratio) -- 3 in form-split and (if possible) 3 in lemma-split.
4. The model works with TSV format. for that, run the script `reinflection2TSV.py ${lang_name} ${POS} ${training_mode}`.
5. Now you can run the model! Configure the hyper-parameters if needed and run `main.py` with the required parameters.

The algorithm trains and prints updates to the Console and evaluates the performance on dev set on every epoch. If the output format is features or phonemes, 2 evaluations will be made. Finally, the best model is selected (acc. to the dev-accuracy) and, it is applied on the test set.

The script produces output files in each of the folders `./Results/{Logs, EvaluationGraphs, Checkpoints, Predictions}` (logs file, Accuracy & ED curves, .tar file and predictions on the test set).
All the above files' names include the run's parameters + time stamp, for identification.

### Testing a Model:
Run `test_single_model.py` with the model's parameters. The script loads and applies it on the dev and test sets, and then prints the results to the Console, writes them to a "Test-Logs" file in `./Results/Logs`, and writes the predictions in `./Results/Predictions`.

