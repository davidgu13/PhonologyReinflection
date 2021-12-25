from itertools import product


def write_to_file(f, s):
    f.write(s)

# region possible values
langs = ['kat', 'tur', 'fin', 'bul', 'hun', 'lav', 'swc', 'sqi']
POSs = ['V','N','ADJ']
tms = ['form', 'lemma']
Input_types = ['f', 'p', 'g']
Output_types = ['f', 'p', 'g']
analogies = ['None', 'src2', 'src1_cross1', 'src1_cross2']
seeds = [7, 21, 42]
atten_modes = ['--ATTN', '']
# endregion possible values
# Note: the running file must be at the same level as the other files!
# actual chosen subset of values:
POSs, Input_types, Output_types, atten_modes, seeds = ['V'], ['f'], ['p'], ['--ATTN'], [7]
generated_file = "runs_scripts/run_configs2.sh"
write_to_file(open(generated_file, "a+", encoding='utf8'), "# Note: the commands in this file must be at the same level as the other files!\n")
for lang, pos, tm, I, O, analog, seed, attn in product(langs, POSs, tms, Input_types, Output_types, analogies, seeds, atten_modes):
    limiting_condition = (tm=='lemma' and analog=='src2') or (attn and I in {'g', 'p'})
    if limiting_condition: continue
    write_to_file(open(generated_file, "a+", encoding='utf8'), f"python main_network.py {lang} {pos} {tm} {I} {O} {analog} {seed} 0 {attn}\n")
write_to_file(open(generated_file, "a+", encoding='utf8'), 'date\n')
write_to_file(open(generated_file, "a+", encoding='utf8'), 'date +"%FORMAT"\n')
write_to_file(open(generated_file, "a+", encoding='utf8'), 'var=$(date)\n')
write_to_file(open(generated_file, "a+", encoding='utf8'), 'var=`date`\n')
write_to_file(open(generated_file, "a+", encoding='utf8'), 'echo "$var"\n')

# date
# date +"%FORMAT"
# var=$(date)
# var=`date`
# echo "$var"