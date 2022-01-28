from os.path import join, isdir, isfile
from os import mkdir, listdir, getcwd
from test_single_model import test_single_model
from argparse import ArgumentParser

original_main_logs_folder, test_main_logs_folder = join("Results", "Logs"), join("Results", "Logs", "Tests")
analogy_types, seeds = ['None', 'src1_cross1'], [42, 21, 7]

groups_indices = list(range(1,8))
lang_pos_groups = dict(zip(groups_indices, [['kat_V', 'kat_N', 'fin_ADJ'], ['swc_V', 'swc_ADJ', 'fin_V'], ['sqi_V', 'hun_V'], ['bul_V', 'bul_ADJ'], ['lav_V', 'lav_N'], ['tur_V', 'tur_ADJ'], ['fin_N']]))

def main(analogy_type, seed, device_idx):
    """
    The plan:
    1. For each original log file of the subfolders (there's only one for each configuration), calculate the model's file name.
        This includes adding "Model_Checkpoint_", ".pth.tar" etc). Then, apply test_single_model on this model.
    2. Divide the work to the various GPUs/servers.
    3. Apply extract_results..py with the new Excel path.
    """
    analogy_seed_folder = f"{analogy_type}_{seed}"
    for i in groups_indices: # 7 groups
        original_logs_folder = join(original_main_logs_folder, analogy_seed_folder, f"Group {i}")
        test_logs_folder = join(test_main_logs_folder, analogy_seed_folder, f"Group {i}")
        models_folder = join("Results", "Checkpoints", analogy_seed_folder, f"Group {i}")
        if not isdir(test_logs_folder): mkdir(test_logs_folder)

        log_files = [f for f in listdir(original_logs_folder) if isfile(f)] # can be 6/12/18 files.
        for f in log_files:
            # Replacing from:    Logs_2022-01-15 003659_bul_ADJ_form_f_p_src1_cross1_42_0_attn.txt
            # to: Model_Checkpoint_46_2022-01-15 003659_bul_ADJ_form_f_p_src1_cross1_42_0_attn.pth.tar
            pattern = f.replace("Logs_","").replace(".txt","")
            model_file = [f for f in listdir(models_folder) if pattern in f][0]
            test_single_model(model_file, device_idx, test_logs_folder, models_folder)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('analogy_type', type=str, choices=['src1_cross1', 'None'], help='The analogies type to be applied')
    parser.add_argument('SEED', type=int, help='Initial seed for all random operations')
    parser.add_argument('device_idx', type=str, help='GPU index', nargs='?', default='0')
    args = parser.parse_args()
    analogy_type, seed, device_idx = args.analogy_type, args.SEED, args.device_idx
    main(analogy_type, seed, device_idx)