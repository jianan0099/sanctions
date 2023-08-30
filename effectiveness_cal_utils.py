import pandas as pd
import numpy as np
from ARIO import ARIOModel
from collections import *
import utils


def yearly_gdp_reduction(weekly_reduction_time_series: np.array,
                         policy_duration_week: int,
                         num_weeks_in_year=52):
    return 1 - (policy_duration_week +
                np.sum(weekly_reduction_time_series[:policy_duration_week])) / num_weeks_in_year


def yearly_gdp_reduction_from_pd(cr_eff_full, country_name, sender_name, target_name, policy,
                                 policy_duration_week: int):
    coercion_scenario = sender_name + '_' + target_name + '_' + policy
    return yearly_gdp_reduction(
        cr_eff_full[country_name + '_' + coercion_scenario].to_numpy(),
        policy_duration_week)


def yearly_gdp_reduction_from_pd_sender_target_tuple(cr_eff_full, sender_name, target_name, policy,
                                                     policy_duration_week: int):
    coercion_scenario = sender_name + '_' + target_name + '_' + policy
    return yearly_gdp_reduction(
        cr_eff_full[sender_name + '_' + coercion_scenario].to_numpy(),
        policy_duration_week), yearly_gdp_reduction(
        cr_eff_full[target_name + '_' + coercion_scenario].to_numpy(),
        policy_duration_week)


def eff_sanctions_without_sanctions(r_s, r_t, alpha_s, alpha_t, q_s, l_s, l_t):
    if r_s >= 1 - alpha_s:
        return 0
    else:
        if r_t >= 1 - alpha_t:
            return (l_s - min(l_s, (q_s - 1) * r_s)) / l_s
        else:
            return (l_s - min(l_s, (q_s - 1) * r_s)) / l_s * min(l_t, r_t) / l_t


def expected_payoff_target_without_sanctions_divided_by_pi(r_s, r_t, alpha_s, alpha_t, q_s, l_s, l_t):
    if r_s >= 1 - alpha_s:
        return 1
    else:
        AS = l_s - min(l_s, (q_s - 1) * r_s)
        AT = l_t - min(l_t, r_t)
        if r_t >= 1 - alpha_t:
            return (l_s - AS * l_t / 2) / l_s
        else:
            return (l_s * l_t - AS*(AT*r_t + (l_t-AT)**2/2)) / (l_s * l_t)


def eff_sanctions_with_sanctions(r_s, r_t, r_s_R, r_t_R, alpha_s, alpha_t, q_s, q_t, l_s, l_t):
    eff_without = eff_sanctions_without_sanctions(r_s, r_t, alpha_s, alpha_t, q_s, l_s, l_t)
    if r_t_R >= 1 - alpha_t:
        return eff_without
    else:
        if r_s_R >= 1 - alpha_s:
            if r_t_R < q_t / (q_t - 1) * r_t:
                return 0
            else:
                return eff_without
        else:
            if r_t_R < q_t / (q_t - 1) * r_t:
                return (l_s - min(l_s, q_s * r_s_R - r_s)) / l_s * min(l_t, (q_t-1)/q_t * r_t_R) / l_t
            else:
                return eff_without


def expected_payoff_target_with_sanctions_divided_by_pi(r_s, r_t, r_s_R, r_t_R, alpha_s, alpha_t, q_s, q_t, l_s, l_t):
    expected_payoff_without = expected_payoff_target_without_sanctions_divided_by_pi(
        r_s, r_t, alpha_s, alpha_t, q_s, l_s, l_t)

    if r_t_R >= 1 - alpha_t:
        return expected_payoff_without
    else:
        ASR = l_s - min(l_s, q_s * r_s_R - r_s)
        ATR = l_t - min(l_t, (q_t - 1) / q_t * r_t_R)
        if r_s_R >= 1 - alpha_s:
            if r_t_R >= q_t / (q_t - 1) * r_t:
                return expected_payoff_without
            else:
                return 1
        else:
            if r_t_R >= q_t / (q_t - 1) * r_t:
                return expected_payoff_without
            else:
                return (l_s * l_t - ASR * (r_t_R*ATR*(1-1/q_t) + (l_t - ATR)**2/2) ) / (l_s * l_t)

def payoff_elements_cal(sender_name, target_name, bloc_regs_list,
                        policy, expected_payoff_as_target_collect, bloc_payoff, p_c):
    actual_bloc = bloc_regs_list.copy()
    actual_bloc.remove(target_name)
    scenario_key = sender_name + '_' + target_name + '_' + policy
    self_targeted_payoff = expected_payoff_as_target_collect[scenario_key]
    not_target_payoff = sum([1 - bloc_payoff[sender_name + '_' + target + '_' + policy][target_name]
                             for target in actual_bloc])
    payoff = p_c * self_targeted_payoff + not_target_payoff
    return self_targeted_payoff, not_target_payoff, payoff


def pay_off_gain_cal(sender_name, bloc_regs_list, policy_list,
                     bloc_type,
                     expected_payoff_as_target_collect,
                     bloc_payoff,
                     p_c_T_list):
    payoff_info = defaultdict(dict)
    for i, bloc_reg in enumerate(bloc_regs_list):
        self_targeted_payoff_bloc, not_target_payoff_bloc, payoff_bloc = \
            payoff_elements_cal(sender_name, bloc_reg, bloc_regs_list,
                                bloc_type, expected_payoff_as_target_collect, bloc_payoff, p_c_T_list[i])

        for policy_ in policy_list:
            if policy_ != bloc_type:
                self_targeted_payoff_no_bloc, not_target_payoff_no_bloc, payoff_no_bloc = \
                    payoff_elements_cal(sender_name, bloc_reg, bloc_regs_list,
                                        policy_, expected_payoff_as_target_collect, bloc_payoff, p_c_T_list[i])

                payoff_info[policy_][bloc_reg] = {'join_as_target_payoff': self_targeted_payoff_bloc,
                                                  'join_as_bloc_payoff': not_target_payoff_bloc,
                                                  'join_payoff': payoff_bloc,

                                                  'not_join_as_target_payoff': self_targeted_payoff_no_bloc,
                                                  'not_join_as_bloc_payoff': not_target_payoff_no_bloc,
                                                  'not_join_payoff': payoff_no_bloc,

                                                  'pay_off_gain': payoff_bloc - payoff_no_bloc}
    return payoff_info


def policy_info_cal(cr_eff_full, sender_name, target_name, policy, policy_duration_in_week_num,
                    alpha_S, alpha_T, q_S, q_T, l_S, l_T,
                    if_with_retaliation, bloc_regs_list,
                    **kwargs):
    r_sender, r_target = \
        yearly_gdp_reduction_from_pd_sender_target_tuple(cr_eff_full, sender_name, target_name, policy,
                                                         policy_duration_in_week_num)
    bloc_loss = {}
    for c_in_bloc in bloc_regs_list:
        if c_in_bloc != target_name:
            bloc_loss[c_in_bloc] = yearly_gdp_reduction_from_pd(cr_eff_full, c_in_bloc, sender_name,
                                                                target_name,
                                                                policy, policy_duration_in_week_num)
    if if_with_retaliation:
        eff_sanctions = \
            eff_sanctions_with_sanctions(kwargs['r_sender_base'],
                                         kwargs['r_target_base'],
                                         r_sender, r_target,
                                         alpha_S, alpha_T,
                                         q_S, q_T, l_S, l_T)
        expected_payoff_as_target = \
            expected_payoff_target_with_sanctions_divided_by_pi(kwargs['r_sender_base'],
                                                                kwargs['r_target_base'],
                                                                r_sender, r_target,
                                                                alpha_S, alpha_T,
                                                                q_S, q_T,
                                                                l_S, l_T)
    else:
        eff_sanctions = eff_sanctions_without_sanctions(r_sender, r_target, alpha_S, alpha_T,
                                                        q_S, l_S, l_T)

        expected_payoff_as_target = \
            expected_payoff_target_without_sanctions_divided_by_pi(r_sender, r_target,
                                                                   alpha_S, alpha_T,
                                                                   q_S, l_S, l_T)
    return r_sender, r_target, bloc_loss, eff_sanctions, expected_payoff_as_target


def get_largest_share_info():
    save_path = 'MRIOT_from_GTAP/share_info_all.xlsx'
    largest_value = pd.read_excel(save_path, sheet_name='share_value').to_numpy()[:, 1:]
    largest_info = pd.read_excel(save_path, sheet_name='share_info').to_numpy()[:, 1:]
    return largest_value, largest_info


def get_basic_bloc(reg_impose: str, reg_target: str, largest_value: np.array, num_bloc: int, regions: list):
    bloc_result = []
    important_partners_index = np.argsort(largest_value[regions.index(reg_impose)])[::-1]
    for index in important_partners_index:
        if regions[index] != reg_impose and regions[index] != reg_target:
            if reg_impose in ['chn', 'hkg', 'mac', 'twn'] and regions[index] in ['chn', 'hkg', 'mac', 'twn']:
                continue
            else:
                bloc_result.append(regions[index])
        if len(bloc_result) == num_bloc:
            break
    return bloc_result


def get_bloc_general(reg_impose: str, reg_target: str, largest_value: np.array, num_bloc: int, regions: list,
                     bloc_form_rule: str):
    bloc_result = []
    if bloc_form_rule == 'low':
        important_partners_index = np.argsort(largest_value[regions.index(reg_impose)])
        for index in important_partners_index:
            if regions[index] != reg_impose and regions[index] != reg_target:
                if reg_impose in ['chn', 'hkg', 'mac', 'twn'] and regions[index] in ['chn', 'hkg', 'mac', 'twn']:
                    continue
                else:
                    bloc_result.append(regions[index])
            if len(bloc_result) == num_bloc:
                break
    return bloc_result


def eff_cal_without_decouple(eco_model: ARIOModel, reg_impose, reg_target,
                             bloc, policy_duration, firm_only, simulation_length, policy_key_simplified,
                             save_path, days_in_each_time_step=7):
    secs_affected = [eco_model.policy_model.get_best_fight_sector(reg_impose, reg_affected, 'imp') for reg_affected in
                     bloc]
    results = {}
    for (reg_affected, sec_affected) in zip(bloc, secs_affected):
        scenario_key = reg_impose + '_' + reg_affected
        policy = {'reg_impose_imp': [reg_impose],
                  'reg_affected_imp': [reg_affected],
                  'sec_affected_imp': [sec_affected],
                  'reduction_imp': [0],

                  'reg_impose_exp': [],
                  'reg_affected_exp': [],
                  'sec_affected_exp': [],
                  'reduction_exp': [],

                  'firm_only': firm_only,
                  'policy_duration': policy_duration,
                  'compare_info_': 'part',

                  'bloc': [list(set(bloc) - {reg_affected})]}
        for policy_key in ['base', 'fight_back_alone', 'fight_back_bloc']:
            simu_results = value_added_evaluation(
                eco_model.VA,
                eco_model.IO_trans(simulation_length, policy_key, **policy)['va_actual'],
                eco_model.num_comms, 'time_series_by_country')[1]
            for reg in [reg_impose] + bloc:
                results[reg + '_' + scenario_key + '_' + policy_key_simplified[policy_key]] = \
                    simu_results[:, eco_model.regions.index(reg)].tolist()

    df = pd.DataFrame(results)
    df.to_excel(save_path, index=False)

def value_added_evaluation(VA_Equilibrium, va_time_series, num_comms, cal):
    if cal == 'sum_by_country':
        va_by_country_actual = utils.row_sum_n_col(np.sum(np.array(va_time_series), axis=0), num_comms)
        va_by_country_equilibrium = utils.row_sum_n_col(VA_Equilibrium * len(va_time_series), num_comms)
        va_change_by_country = va_by_country_actual - va_by_country_equilibrium
        return va_change_by_country, va_change_by_country / va_by_country_equilibrium

    if cal == 'time_series_by_country':
        va_by_country_actual = utils.row_sum_n_col(np.array(va_time_series), num_comms)
        va_by_country_equilibrium = utils.row_sum_n_col(VA_Equilibrium, num_comms)
        va_change_by_country = va_by_country_actual - va_by_country_equilibrium[None, :]
        return va_change_by_country, va_change_by_country / va_by_country_equilibrium[None, :]

def plot_base_two_regs(reg_impose, reg_affected, sec_affected, trade_dir, firm_only, policy_duration,
                       eco_model: ARIOModel, simulation_length):
    policy = {'reg_impose_imp': [],
              'reg_affected_imp': [],
              'sec_affected_imp': [],
              'reduction_imp': [],

              'reg_impose_exp': [],
              'reg_affected_exp': [],
              'sec_affected_exp': [],
              'reduction_exp': [],

              'firm_only': firm_only,
              'policy_duration': policy_duration}

    if trade_dir == 'imp':
        policy['reg_impose_imp'].append(reg_impose)
        policy['reg_affected_imp'].append(reg_affected)
        policy['sec_affected_imp'].append(sec_affected)
        policy['reduction_imp'].append(0)
        eco_model.policy_model.importance_evaluation(reg_impose=reg_impose,
                                                                       reg_affected=reg_affected,
                                                                       sector_affected=sec_affected,
                                                                       trade_direction='imp', compare_info_='part')
        eco_model.policy_model.importance_evaluation(reg_impose=reg_impose,
                                                                      reg_affected=reg_affected,
                                                                      sector_affected=sec_affected,
                                                                      trade_direction='imp', compare_info_='all')
    if trade_dir == 'exp':
        policy['reg_impose_exp'].append(reg_impose)
        policy['reg_affected_exp'].append(reg_affected)
        policy['sec_affected_exp'].append(sec_affected)
        policy['reduction_exp'].append(0)
        eco_model.policy_model.importance_evaluation(reg_impose=reg_impose,
                                                                       reg_affected=reg_affected,
                                                                       sector_affected=sec_affected,
                                                                       trade_direction='exp', compare_info_='part')
        eco_model.policy_model.importance_evaluation(reg_impose=reg_impose,
                                                                      reg_affected=reg_affected,
                                                                      sector_affected=sec_affected,
                                                                      trade_direction='exp', compare_info_='all')

    base_results = eco_model.IO_trans(simulation_length, 'base', **policy)
    _, base = \
        value_added_evaluation(eco_model.VA, base_results['va_actual'], eco_model.num_comms, 'time_series_by_country')
    return base[:, eco_model.regions.index(reg_impose)], base[:, eco_model.regions.index(reg_affected)]

def eff_cal_summary(sender_name, bloc_regs_list, policy_duration_in_week_num, policy_list,
                    bloc_type, alpha_S, alpha_T_list, q_S, q_T_list, l_S, l_T_list, p_c_T_list, largest_share, regions,
                    save_path_raw, save_path):
    cr_eff_full = pd.read_excel(save_path_raw)

    r_sender_collect = defaultdict()
    r_target_collect = defaultdict()
    bloc_payoff = defaultdict()
    eff_sanction_collect = defaultdict()
    expected_payoff_as_target_collect = defaultdict()
    largest_share_sender = {}
    largest_share_target = {}

    for bloc_target_i, bloc_target_name in enumerate(bloc_regs_list):
        largest_share_sender[bloc_target_name] = largest_share[regions.index(bloc_target_name),
                                                               regions.index(sender_name)]
        largest_share_target[bloc_target_name] = largest_share[regions.index(sender_name),
                                                               regions.index(bloc_target_name)]
        for policy in policy_list:
            scenario_key = sender_name + '_' + bloc_target_name + '_' + policy
            if policy == 'base':
                r_sender, r_target, bloc_loss, eff_sanctions, expected_payoff_as_target = \
                    policy_info_cal(cr_eff_full, sender_name, bloc_target_name, policy,
                                    policy_duration_in_week_num,
                                    alpha_S, alpha_T_list[bloc_target_i], q_S, q_T_list[bloc_target_i], l_S,
                                    l_T_list[bloc_target_i],
                                    False, bloc_regs_list)
            else:
                r_sender, r_target, bloc_loss, eff_sanctions, expected_payoff_as_target = \
                    policy_info_cal(cr_eff_full, sender_name, bloc_target_name, policy,
                                    policy_duration_in_week_num,
                                    alpha_S, alpha_T_list[bloc_target_i], q_S, q_T_list[bloc_target_i], l_S,
                                    l_T_list[bloc_target_i],
                                    True, bloc_regs_list,
                                    r_sender_base=r_sender_collect[
                                        sender_name + '_' + bloc_target_name + '_base'],
                                    r_target_base=r_target_collect[
                                        sender_name + '_' + bloc_target_name + '_base'])
            r_sender_collect[scenario_key] = r_sender
            r_target_collect[scenario_key] = r_target
            bloc_payoff[scenario_key] = bloc_loss
            eff_sanction_collect[scenario_key] = eff_sanctions
            expected_payoff_as_target_collect[scenario_key] = expected_payoff_as_target

    payoff_info = pay_off_gain_cal(sender_name, bloc_regs_list, policy_list,
                                   bloc_type,
                                   expected_payoff_as_target_collect,
                                   bloc_payoff,
                                   p_c_T_list)

    df = pd.DataFrame(eff_sanction_collect, index=[0])
    df.to_excel(save_path, sheet_name='eff_sanction', index=False)
    for alone_policy in payoff_info:
        df = pd.DataFrame(payoff_info[alone_policy])
        with pd.ExcelWriter(save_path, engine="openpyxl", mode='a') as writer:
            df.to_excel(writer, sheet_name='payoff_bloc_' + alone_policy)

    eff_retaliation_collect = {}
    for bloc_target_name in bloc_regs_list:
        base_eff = eff_sanction_collect[sender_name + '_' + bloc_target_name + '_base']
        alone_eff = eff_sanction_collect[sender_name + '_' + bloc_target_name + '_alone_no']
        bloc_eff = eff_sanction_collect[sender_name + '_' + bloc_target_name + '_' + bloc_type]
        if base_eff == 0:
            eff_retaliation_collect[sender_name + '_' + bloc_target_name + '_alone_no'] = str('sender not impose')
            eff_retaliation_collect[sender_name + '_' + bloc_target_name + '_' + bloc_type] = str('sender not impose')
        else:
            eff_retaliation_collect[sender_name + '_' + bloc_target_name + '_alone_no'] = \
                min(1, max(0, 1 - alone_eff / base_eff))
            eff_retaliation_collect[sender_name + '_' + bloc_target_name + '_' + bloc_type] = \
                min(1, max(0, 1 - bloc_eff / base_eff))

    df = pd.DataFrame(eff_retaliation_collect, index=[0])
    with pd.ExcelWriter(save_path, engine="openpyxl", mode='a') as writer:
        df.to_excel(writer, sheet_name='eff_retaliation', index=False)

    df = pd.DataFrame(bloc_regs_list)
    with pd.ExcelWriter(save_path, engine="openpyxl", mode='a') as writer:
        df.to_excel(writer, sheet_name='bloc_regs', index=False, header=None)

    df = pd.DataFrame(largest_share_sender, index=[0])
    with pd.ExcelWriter(save_path, engine="openpyxl", mode='a') as writer:
        df.to_excel(writer, sheet_name='largest_share_sender', index=False)

    df = pd.DataFrame(largest_share_target, index=[0])
    with pd.ExcelWriter(save_path, engine="openpyxl", mode='a') as writer:
        df.to_excel(writer, sheet_name='largest_share_target', index=False)

    return r_sender_collect, r_target_collect