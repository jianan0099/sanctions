import utils
from ARIO import ARIOModel
from Flexible_MRIO import IOEquilibrium
import numpy as np
import effectiveness_cal_utils as eff_cal_utils
from collections import *
import pandas as pd
# figs 2 & 3


decoupling_scenario = 'base'
days_in_each_time_step = 7
simulation_length = 52 * 2
qs = 5
ls = 0.01 * 5
lt = 0.01 * 5
alpha_s = alpha_t = 0
impose_affected_tuple = [('usa', 'chn'),
                         ('chn', 'lao'),
                         ('lao', 'chn'),
                         ('vnm', 'lao')]


IO_eqi = IOEquilibrium()
X, Z, F, VA = IO_eqi.get_needed_IO(decoupling_scenario, days_in_each_time_step)
eco_model = ARIOModel(Z, F, VA, X, IO_eqi.regions, IO_eqi.activities)
imp_importance_all = utils.row_sum_n_col(Z, IO_eqi.num_comms) / \
                     np.repeat(utils.cal_VA_by_country(VA, IO_eqi.num_comms), IO_eqi.num_comms)[:, None]
va_c = utils.cal_VA_by_country(eco_model.VA, 65)
country_size_ranking = [eco_model.regions[index] for index in np.argsort(va_c)[::-1]]
impose_change_all = {}
affected_change_all = {}
scenarios = defaultdict(list)
results = defaultdict(dict)

for impose_c, affected_c in impose_affected_tuple:
    impose_index, affected_index = eco_model.regions.index(impose_c), eco_model.regions.index(affected_c)
    imp_aff = imp_importance_all[affected_index * 65:(affected_index + 1) * 65][:, impose_index]
    comm_index_list = np.argsort(imp_aff)[::-1][:5]
    for comm_index in comm_index_list:
        scenario_key = impose_c + '_' + affected_c + '_' + eco_model.activities[comm_index]
        impose_change, affected_change = eff_cal_utils.plot_base_two_regs(reg_impose=impose_c,
                                                                      reg_affected=affected_c,
                                                                      sec_affected=eco_model.activities[comm_index],
                                                                      trade_dir='imp',
                                                                      firm_only=True,
                                                                      policy_duration=52,
                                                                      eco_model=eco_model,
                                                                      simulation_length=simulation_length)
        r_sender, r_target = \
            eff_cal_utils.yearly_gdp_reduction(impose_change, 52), \
            eff_cal_utils.yearly_gdp_reduction(affected_change, 52)
        eff_sanction = eff_cal_utils.eff_sanctions_without_sanctions(r_sender, r_target, alpha_s, alpha_t, qs, ls, lt)

        scenarios['sender'].append(impose_c)
        scenarios['sender_rank'].append(country_size_ranking.index(impose_c) + 1)
        scenarios['target'].append(affected_c)
        scenarios['target_rank'].append(country_size_ranking.index(affected_c) + 1)
        scenarios['comm'].append(eco_model.activities[comm_index])
        scenarios['share'].append(imp_aff[comm_index])

        results[scenario_key]['r_sender'] = r_sender
        results[scenario_key]['r_target'] = r_target
        results[scenario_key]['eta'] = eff_sanction
        impose_change_all[scenario_key] = impose_change
        affected_change_all[scenario_key] = affected_change


save_path = 'exp_results/results/sec_selection_example.xlsx'

df = pd.DataFrame(scenarios)
df.to_excel(save_path, sheet_name='scenarios', index=False)

df = pd.DataFrame(results)
with pd.ExcelWriter(save_path, engine="openpyxl", mode='a') as writer:
    df.to_excel(writer, sheet_name='results')

df = pd.DataFrame([sender + '_' + target for sender, target in impose_affected_tuple])
with pd.ExcelWriter(save_path, engine="openpyxl", mode='a') as writer:
    df.to_excel(writer, sheet_name='c_pair', index=False, header=None)

df = pd.DataFrame(impose_change_all)
with pd.ExcelWriter(save_path, engine="openpyxl", mode='a') as writer:
    df.to_excel(writer, sheet_name='sender_loss', index=False)

df = pd.DataFrame(affected_change_all)
with pd.ExcelWriter(save_path, engine="openpyxl", mode='a') as writer:
    df.to_excel(writer, sheet_name='target_loss', index=False)

largest_share_value = []
num_regs, num_comms = len(eco_model.regions), len(eco_model.activities)
for reg_index in range(num_regs):
    largest_share_sector_index = \
        np.argsort(imp_importance_all[reg_index * num_comms:(reg_index + 1) * num_comms, :],
                   axis=0)[::-1][0]
    largest_share_value.append(imp_importance_all[
                                   reg_index * num_comms + largest_share_sector_index,
                                   range(num_regs)])
largest_share_value = np.array(largest_share_value)
threshold = 0.05
capability = np.sum(largest_share_value >= threshold, axis=0)/len(largest_share_value)
vulnerability = np.sum(largest_share_value >= threshold, axis=1)/len(largest_share_value)
share_summary = {}
share_summary['regs'] = eco_model.regions
share_summary['va'] = va_c
share_summary['capability'] = capability
share_summary['vulnerability'] = vulnerability
df = pd.DataFrame(share_summary)
with pd.ExcelWriter(save_path, engine="openpyxl", mode='a') as writer:
    df.to_excel(writer, sheet_name='share_summary_' + str(threshold), index=False)

