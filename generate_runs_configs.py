from itertools import product

def write_to_file(f, s):
    f.write(s)

def generate_run_name(lang, *pos, analogy='None', seed=42):
    return f"{lang}-{'_'.join(pos)}-{analogy}-{seed}.sh"
# python main.py kat V form f p src2 42 0 --ATTN

def generate_lang_pos_group_run(file_name, lang, pos, seed=42, device_idx=0, analogy='None'):
    # write_to_file( open(file_name, "a+", encoding='utf8'), "# Note: the commands in this file must be at the same level as the other files!\n" )

    write_to_file( open(file_name, "a+", encoding='utf8'), f"\npython main.py {lang} {pos} form g g {analogy} {seed} {device_idx}\n" )
    write_to_file( open(file_name, "a+", encoding='utf8'), f"python main.py {lang} {pos} form f f {analogy} {seed} {device_idx}\n" )
    write_to_file( open(file_name, "a+", encoding='utf8'), f"python main.py {lang} {pos} form f p {analogy} {seed} {device_idx} --ATTN\n" )
    write_to_file( open(file_name, "a+", encoding='utf8'), f"python main.py {lang} {pos} lemma g g {analogy} {seed} {device_idx}\n" )
    write_to_file( open(file_name, "a+", encoding='utf8'), f"python main.py {lang} {pos} lemma f f {analogy} {seed} {device_idx}\n" )
    write_to_file( open(file_name, "a+", encoding='utf8'), f"python main.py {lang} {pos} lemma f p {analogy} {seed} {device_idx} --ATTN\n" )

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
#     write_to_file(open(generated_file, "a+", encoding='utf8'), f"python main_network.py {lang} {pos} {tm} {I} {O} {analog} {seed} {device_idx} {attn}\n")
#
# write_to_file(open(generated_file, "a+", encoding='utf8'), f"""date\n'
# date +"%FORMAT
# var=$(date)
# var=`date`
# echo "$var" """)
# endregion manual_configs

if __name__ == '__main__':
    from os.path import join
    # Group 1
    file_name1 = join("runs_scripts", 'kat-V_N-and-fin-ADJ-src1_cross1-42.sh')
    generate_lang_pos_group_run(file_name1, 'kat', 'V', 42, 1)
    generate_lang_pos_group_run(file_name1, 'kat', 'N', 42, 1)
    generate_lang_pos_group_run(file_name1, 'fin', 'ADJ', 42, 1)

    # Group 2
    file_name2 = join("runs_scripts", 'swc-V_ADJ-and-fin-V-src1_cross1-42.sh')
    generate_lang_pos_group_run(file_name2, 'swc', 'V', 42, 2)
    generate_lang_pos_group_run(file_name2, 'swc', 'ADJ', 42, 2)
    generate_lang_pos_group_run(file_name2, 'fin', 'V', 42, 2)

    # Group 3
    file_name3 = join("runs_scripts", 'sqi-V-and-hun-V-src1_cross1-42.sh')
    generate_lang_pos_group_run(file_name3, 'sqi', 'V', 42, 3)
    generate_lang_pos_group_run(file_name3, 'hun', 'V', 42, 3)

    # # Group 4
    # file_name4 = join("runs_scripts", 'bul-V_ADJ-src1_cross1-42.sh')
    # generate_lang_pos_group_run(file_name4, 'bul', 'V', 42, 0, 'src1_cross1')
    # generate_lang_pos_group_run(file_name4, 'bul', 'ADJ', 42, 0, 'src1_cross1')
    # 
    # # Group 5
    # file_name5 = join("runs_scripts", 'lav-V_N-src1_cross1-42.sh')
    # generate_lang_pos_group_run(file_name5, 'lav', 'V', 42, 1, 'src1_cross1')
    # generate_lang_pos_group_run(file_name5, 'lav', 'N', 42, 1, 'src1_cross1')
    # 
    # # Group 6
    # file_name6 = join("runs_scripts", 'tur-V_ADJ-src1_cross1-42.sh')
    # generate_lang_pos_group_run(file_name6, 'tur', 'V', 42, 2, 'src1_cross1')
    # generate_lang_pos_group_run(file_name6, 'tur', 'ADJ', 42, 2, 'src1_cross1')
    # 
    # # Group 7
    # file_name7 = join("runs_scripts", 'fin-N-src1_cross1-42.sh')
    # generate_lang_pos_group_run(file_name7, 'fin', 'N', 42, 3, 'src1_cross1')
