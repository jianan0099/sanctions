from ARIO import ARIOModel
from Flexible_MRIO import IOEquilibrium
import pandas as pd
import effectiveness_cal_utils as eff_cal_utils
import os
# figs 4 & 5


decoupling_scenario = 'base'
days_in_each_time_step = 7
simulation_length = 52 * 2
policy_duration = 52
firm_only = True
num_bloc = 3
bloc_type = 'bloc_no'
bloc_form_rule = ''
alpha_S = 1-2.4*0.01
alpha_T_list = [1-2.4*0.01] * (num_bloc + 1)
q_S = 5
q_T_list = [5] * (num_bloc + 1)
l_S = 5 * 0.01
l_T_list = [5 * 0.01] * (num_bloc + 1)
p_c_T_list = [1] * (num_bloc + 1)

IO_eqi = IOEquilibrium()
X, Z, F, VA = IO_eqi.get_needed_IO(decoupling_scenario, days_in_each_time_step)
eco_model = ARIOModel(Z, F, VA, X, IO_eqi.regions, IO_eqi.activities)
largest_value, largest_info = eff_cal_utils.get_largest_share_info()
policy_key_simplified = {'base': 'base',
                         'fight_back_alone': 'alone_no',
                         'fight_back_bloc': bloc_type}

for reg_impose, reg_target in [('chn', 'usa'), ('deu', 'fra'), ('chn', 'idn'), ('usa', 'sgp')]:
    if bloc_form_rule == '':
        bloc = [reg_target] + eff_cal_utils.get_basic_bloc(reg_impose, reg_target, largest_value, num_bloc,
                                                           IO_eqi.regions)
    elif bloc_form_rule == 'low':
        bloc = [reg_target] + eff_cal_utils.get_bloc_general(reg_impose, reg_target, largest_value, num_bloc,
                                                             IO_eqi.regions, bloc_form_rule)
    save_path = 'exp_results/results/cr_eff_full_' + reg_impose + '_' + reg_target + bloc_form_rule \
                + '_imp' + '_' + \
                str(policy_duration) + '.xlsx'
    save_path_cal = 'exp_results/results/cr_eff_full_cal_q' + str(q_S) + '_' + reg_impose + '_' + reg_target + \
                    bloc_form_rule + '_imp' + '_' + \
                    str(policy_duration) + '.xlsx'
    if not os.path.exists(save_path):
        eff_cal_utils.eff_cal_without_decouple(eco_model, reg_impose, reg_target, bloc,
                                               policy_duration, firm_only, simulation_length, policy_key_simplified,
                                               save_path)
    X_decoupling_without_F, Z_decoupling_without_F, F_decoupling_without_F, VA_decoupling_without_F = \
        IO_eqi.get_needed_IO(decoupling_scenario='country_list', days_in_each_time_step=days_in_each_time_step,
                             c_list=[reg_impose, reg_target], change_F=False)
    _, decoupling_va_change_by_country = eff_cal_utils.value_added_evaluation(IO_eqi.annual_VA / days_in_each_time_step,
                                                                          [VA_decoupling_without_F],
                                                                          IO_eqi.num_comms, 'sum_by_country')
    df = pd.DataFrame({IO_eqi.regions[i]: decoupling_va_change_by_country[i] for i in range(len(decoupling_va_change_by_country))},
                      index=[0])
    with pd.ExcelWriter(save_path, engine="openpyxl", mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name='decoupling_va_change_by_country', index=False)

    r_sender_collect, r_target_collect = eff_cal_utils.eff_cal_summary(reg_impose, bloc, policy_duration,
                                                                       list(policy_key_simplified.values()),
                                                                       bloc_type, alpha_S, alpha_T_list, q_S, q_T_list,
                                                                       l_S, l_T_list, p_c_T_list,
                                                                       largest_value, IO_eqi.regions, save_path,
                                                                       save_path_cal)
