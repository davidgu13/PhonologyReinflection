from itertools import product

def write_to_file(f, s):
    f.write(s)

def generate_run_name(lang, *pos, analogy='None', seed=42):
    return f"{lang}-{'_'.join(pos)}-{analogy}-{seed}.sh"
# python main.py kat V form f p src2 42 0 --ATTN

def generate_lang_pos_group_run(file_name, lang, pos, seed=42, analogy='None'):
    # write_to_file( open(file_name, "a+", encoding='utf8'), "# Note: the commands in this file must be at the same level as the other files!\n" )

    write_to_file( open(file_name, "a+", encoding='utf8'), f"\npython main.py {lang} {pos} form g g {analogy} {seed} 0\n" )
    write_to_file( open(file_name, "a+", encoding='utf8'), f"python main.py {lang} {pos} form f f {analogy} {seed} 0\n" )
    write_to_file( open(file_name, "a+", encoding='utf8'), f"python main.py {lang} {pos} form f p {analogy} {seed} 0 --ATTN\n" )
    write_to_file( open(file_name, "a+", encoding='utf8'), f"python main.py {lang} {pos} lemma g g {analogy} {seed} 0\n" )
    write_to_file( open(file_name, "a+", encoding='utf8'), f"python main.py {lang} {pos} lemma f f {analogy} {seed} 0\n" )
    write_to_file( open(file_name, "a+", encoding='utf8'), f"python main.py {lang} {pos} lemma f p {analogy} {seed} 0 --ATTN\n" )

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

# region manual_configs
# the subset of values actually chosen:
# POSs, Input_types, Output_types, atten_modes, seeds = ['V'], ['f'], ['p'], ['--ATTN'], [7]
# generated_file = "runs_scripts/run_configs2.sh"
# write_to_file(open(generated_file, "a+", encoding='utf8'), "# Note: the commands in this file must be at the same level as the other files!\n")
# for lang, pos, tm, I, O, analog, seed, attn in product(langs, POSs, tms, Input_types, Output_types, analogies, seeds, atten_modes):
#     limiting_condition = (tm=='lemma' and analog=='src2') or (attn and I in {'g', 'p'})
#     if limiting_condition: continue
#     write_to_file(open(generated_file, "a+", encoding='utf8'), f"python main_network.py {lang} {pos} {tm} {I} {O} {analog} {seed} 0 {attn}\n")
#
# write_to_file(open(generated_file, "a+", encoding='utf8'), f"""date\n'
# date +"%FORMAT
# var=$(date)
# var=`date`
# echo "$var" """)
# endregion manual_configs

if __name__ == '__main__':
    from os.path import join
    # Group #1
    # file_name = join("runs_scripts", 'kat-V_N-and-fin-ADJ-None-42.sh')
    # generate_lang_pos_group_run(file_name, 'kat', 'V')
    # generate_lang_pos_group_run(file_name, 'kat', 'N')
    # generate_lang_pos_group_run(file_name, 'fin', 'ADJ')

    # Group #2
    file_name = join("runs_scripts", 'swc-V_ADJ-and-fin-V-None-42.sh')
    generate_lang_pos_group_run(file_name, 'swc', 'V')
    generate_lang_pos_group_run(file_name, 'swc', 'ADJ')
    generate_lang_pos_group_run(file_name, 'fin', 'V')
