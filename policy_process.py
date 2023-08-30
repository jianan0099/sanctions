import numpy as np
import copy
import utils


class Policy:
    def __init__(self, regions, activities, Z):
        self.regions = regions
        self.activities = activities
        self.num_regs = len(regions)
        self.num_comms = len(activities)
        self.Z = Z
        self.firm_output_to_each_country_Z = utils.row_sum_n_col(self.Z, self.num_comms)
        self.firm_output_to_each_country_Z_frac = \
            self.firm_output_to_each_country_Z / np.sum(self.firm_output_to_each_country_Z, axis=1)[:, None]
        self.reg_comm_pair_input_from_each_reg = \
            utils.get_reg_sec_pair_from_each_reg(self.firm_output_to_each_country_Z,
                                                 self.num_regs, self.num_comms).transpose()
        self.reg_comm_pair_input_from_each_country_Z_frac = \
            self.reg_comm_pair_input_from_each_reg / np.sum(self.reg_comm_pair_input_from_each_reg, axis=1)[:, None]

    def importance_evaluation(self, reg_impose, reg_affected, sector_affected, trade_direction, compare_info_='part'):
        reg_impose_index = self.regions.index(reg_impose)
        reg_affected_index = self.regions.index(reg_affected)
        sector_affected_index = self.activities.index(sector_affected)
        firm_affected_index = utils.get_firm_index(reg_affected_index, sector_affected_index, self.num_comms)

        if trade_direction == 'imp':
            p1 = utils.row_sum_n_col(self.Z, self.num_comms)[firm_affected_index, reg_impose_index]

            if compare_info_ == 'all':
                p1_reverse = \
                    self.importance_evaluation(reg_affected, reg_impose, sector_affected, trade_direction='exp',
                                               compare_info_='part')

        if trade_direction == 'exp':
            p1 = self.reg_comm_pair_input_from_each_country_Z_frac[firm_affected_index, reg_impose_index]
            if compare_info_ == 'all':
                p1_reverse = \
                    self.importance_evaluation(reg_affected, reg_impose, sector_affected, trade_direction='imp',
                                               compare_info_='part')
        if compare_info_ == 'all':
            return p1 - p1_reverse
        else:
            return p1

    def get_policy_results(self, policy_scenario, **kwargs):
        import_tariffs_impact, export_control_info, firm_only, policy_duration = \
            [[], [], []], [[], [], []], True, kwargs['policy_duration']
        if policy_scenario == 'normal':
            pass

        elif policy_scenario == 'base':
            for pair_num in range(len(kwargs['reg_impose_imp'])):
                import_tariffs_impact[0].append(self.regions.index(kwargs['reg_impose_imp'][pair_num]))
                import_tariffs_impact[1].append(
                    utils.get_firm_index(self.regions.index(kwargs['reg_affected_imp'][pair_num]),
                                         self.activities.index(kwargs['sec_affected_imp'][pair_num]), self.num_comms))
                import_tariffs_impact[2].append(kwargs['reduction_imp'][pair_num])

            for pair_num in range(len(kwargs['reg_impose_exp'])):
                export_control_info[0].append(self.regions.index(kwargs['reg_affected_exp'][pair_num]))
                export_control_info[1].append(
                    utils.get_firm_index(self.regions.index(kwargs['reg_impose_exp'][pair_num]),
                                         self.activities.index(kwargs['sec_affected_exp'][pair_num]), self.num_comms))
                export_control_info[2].append(kwargs['reduction_exp'][pair_num])
                import_tariffs_impact[0].append(self.regions.index(kwargs['reg_affected_exp'][pair_num]))
                import_tariffs_impact[1].append(
                    utils.get_firm_index(self.regions.index(kwargs['reg_impose_exp'][pair_num]),
                                         self.activities.index(kwargs['sec_affected_exp'][pair_num]), self.num_comms))
                import_tariffs_impact[2].append(kwargs['reduction_exp'][pair_num])
            firm_only = kwargs['firm_only']
            policy_duration = kwargs['policy_duration']

        elif policy_scenario == 'fight_back_alone':
            kwargs_new = copy.deepcopy(kwargs)
            for (reg_impose_imp, sec_affected_imp, reg_affected_imp, reduction_imp) in zip(kwargs['reg_impose_imp'],
                                                                                           kwargs['sec_affected_imp'],
                                                                                           kwargs['reg_affected_imp'],
                                                                                           kwargs['reduction_imp']):
                kwargs_new['reg_impose_imp'].append(reg_affected_imp)
                kwargs_new['reg_affected_imp'].append(reg_impose_imp)
                kwargs_new['sec_affected_imp'].append(
                    self.get_best_fight_sector(reg_affected_imp, reg_impose_imp, 'imp',
                                               compare_info_=kwargs['compare_info_']))
                kwargs_new['reduction_imp'].append(reduction_imp)
            import_tariffs_impact, export_control_info, firm_only, policy_duration = \
                self.get_policy_results('base', **kwargs_new)

        elif policy_scenario == 'fight_back_bloc_each':
            kwargs_new = copy.deepcopy(kwargs)
            for (reg_impose_imp, sec_affected_imp, reg_affected_imp, bloc, reduction_imp) in \
                    zip(kwargs['reg_impose_imp'],
                        kwargs['sec_affected_imp'],
                        kwargs['reg_affected_imp'],
                        kwargs['bloc'],
                        kwargs['reduction_imp']):
                for reg_affected in [reg_affected_imp] + bloc:
                    kwargs_new['reg_impose_imp'].append(reg_affected)
                    kwargs_new['reg_affected_imp'].append(reg_impose_imp)
                    kwargs_new['sec_affected_imp'].append(
                        self.get_best_fight_sector(reg_affected, reg_impose_imp, 'imp',
                                                   compare_info_=kwargs['compare_info_']))
                    kwargs_new['reduction_imp'].append(reduction_imp)
            for (reg_impose_exp, sec_affected_exp, reg_affected_exp, bloc, reduction_exp) in \
                    zip(kwargs['reg_impose_exp'],
                        kwargs['sec_affected_exp'],
                        kwargs['reg_affected_exp'],
                        kwargs['bloc'],
                        kwargs['reduction_exp']):
                for reg_affected in [reg_affected_exp] + bloc:
                    kwargs_new['reg_impose_exp'].append(reg_affected)
                    kwargs_new['reg_affected_exp'].append(reg_impose_exp)
                    kwargs_new['sec_affected_exp'].append(
                        self.get_best_fight_sector(reg_affected, reg_impose_exp, 'exp',
                                                   compare_info_=kwargs['compare_info_']))
                    kwargs_new['reduction_exp'].append(reduction_exp)
            import_tariffs_impact, export_control_info, firm_only, policy_duration = \
                self.get_policy_results('base', **kwargs_new)

        elif policy_scenario == 'fight_back_bloc':
            kwargs_new = copy.deepcopy(kwargs)
            for (reg_impose_imp, sec_affected_imp, reg_affected_imp, bloc, reduction_imp) in \
                    zip(kwargs['reg_impose_imp'],
                        kwargs['sec_affected_imp'],
                        kwargs['reg_affected_imp'],
                        kwargs['bloc'],
                        kwargs['reduction_imp']):
                for reg_affected in [reg_affected_imp] + bloc:
                    kwargs_new['reg_impose_imp'].append(reg_affected)
                    kwargs_new['reg_affected_imp'].append(reg_impose_imp)
                    kwargs_new['sec_affected_imp'].append(
                        self.get_best_fight_sector(reg_affected, reg_impose_imp, 'imp',
                                                   compare_info_=kwargs['compare_info_']))
                    kwargs_new['reduction_imp'].append(reduction_imp)
            import_tariffs_impact, export_control_info, firm_only, policy_duration = \
                self.get_policy_results('base', **kwargs_new)

        elif policy_scenario == 'fight_back_bloc_sender_re':
            kwargs_new = copy.deepcopy(kwargs)
            for (reg_impose_imp, sec_affected_imp, reg_affected_imp, bloc, reduction_imp) in \
                    zip(kwargs['reg_impose_imp'],
                        kwargs['sec_affected_imp'],
                        kwargs['reg_affected_imp'],
                        kwargs['bloc'],
                        kwargs['reduction_imp']):
                for reg_affected in [reg_affected_imp] + bloc:
                    kwargs_new['reg_impose_imp'].append(reg_affected)
                    kwargs_new['reg_affected_imp'].append(reg_impose_imp)
                    kwargs_new['sec_affected_imp'].append(
                        self.get_best_fight_sector(reg_affected, reg_impose_imp, 'imp',
                                                   compare_info_=kwargs['compare_info_']))
                    kwargs_new['reduction_imp'].append(reduction_imp)
                    if reg_affected != reg_affected_imp:
                        kwargs_new['reg_impose_imp'].append(reg_impose_imp)
                        kwargs_new['reg_affected_imp'].append(reg_affected)
                        kwargs_new['sec_affected_imp'].append(
                            self.get_best_fight_sector(reg_impose_imp, reg_affected, 'imp',
                                                       compare_info_=kwargs['compare_info_']))
                        kwargs_new['reduction_imp'].append(reduction_imp)
                    else:
                        kwargs_new['reg_impose_imp'].append(reg_impose_imp)
                        kwargs_new['reg_affected_imp'].append(reg_affected)
                        for sec_ in self.get_best_fight_sectors(reg_impose_imp, reg_affected, 'imp',
                                                   compare_info_=kwargs['compare_info_']):
                            if sec_ != sec_affected_imp:
                                kwargs_new['sec_affected_imp'].append(sec_)
                                break
                        kwargs_new['reduction_imp'].append(reduction_imp)
            import_tariffs_impact, export_control_info, firm_only, policy_duration = \
                self.get_policy_results('base', **kwargs_new)
        return import_tariffs_impact, export_control_info, firm_only, policy_duration

    def get_best_fight_sector(self, reg_impose, reg_affected, trade_direction, compare_info_='part'):
        reg_impose_importance = []
        for sector_affected in self.activities:
            reg_impose_importance.append(self.importance_evaluation(reg_impose, reg_affected, sector_affected,
                                                                    trade_direction,
                                                                    compare_info_=compare_info_))
        return self.activities[np.argsort(np.array(reg_impose_importance))[-1]]

    def get_best_fight_sectors(self, reg_impose, reg_affected, trade_direction, compare_info_='part'):
        reg_impose_importance = []
        for sector_affected in self.activities:
            reg_impose_importance.append(self.importance_evaluation(reg_impose, reg_affected, sector_affected,
                                                                    trade_direction,
                                                                    compare_info_=compare_info_))
        return [self.activities[index] for index in np.argsort(np.array(reg_impose_importance))[::-1]]

    def get_fight_back_sector_bi_trade_direction(self, reg_impose, reg_affected, compare_info_='part'):
        reg_affected_index = self.regions.index(reg_affected)
        reg_impose_index = self.regions.index(reg_impose)
        IMP_superiority = []
        EXP_superiority = []

        for comm_index in range(self.num_comms):
            IMP_reg_affected_importance = \
                self.firm_output_to_each_country_Z_frac[self.num_comms * reg_impose_index + comm_index][
                    reg_affected_index]
            IMP_reg_impose_importance = \
                self.reg_comm_pair_input_from_each_country_Z_frac[self.num_comms * reg_affected_index +
                                                                  comm_index][reg_impose_index]
            EXP_reg_affected_importance = \
                self.reg_comm_pair_input_from_each_country_Z_frac[self.num_comms * reg_impose_index +
                                                                  comm_index][reg_affected_index]
            EXP_reg_impose_importance = \
                self.firm_output_to_each_country_Z_frac[self.num_comms * reg_affected_index +
                                                        comm_index][reg_impose_index]
            if compare_info_ == 'part':
                IMP_superiority.append(IMP_reg_affected_importance)
                EXP_superiority.append(EXP_reg_affected_importance)
            if compare_info_ == 'all':
                IMP_superiority.append(IMP_reg_affected_importance - IMP_reg_impose_importance)
                EXP_superiority.append(EXP_reg_affected_importance - EXP_reg_impose_importance)
        if max(IMP_superiority) > max(EXP_superiority):
            return 'imp', self.activities[np.argsort(IMP_superiority)[-1]]
        else:
            return 'exp', self.activities[np.argsort(EXP_superiority)[-1]]

    def get_firm_imp_importance_for_reg(self, reg_impose):
        reg_impose_index = self.regions.index(reg_impose)
        imp_importance_for_reg_impose = \
            self.firm_output_to_each_country_Z_frac[utils.get_reg_index_range(reg_impose_index,
                                                                              self.num_comms)].copy()
        imp_importance_for_reg_impose[:, reg_impose_index] = -np.inf
        imp_importance_rank_sec_reg_pair = np.argsort(imp_importance_for_reg_impose.flatten())[self.num_comms:][::-1]
        imp_importance_rank_sec_reg_pair_results = []
        for index in imp_importance_rank_sec_reg_pair:
            sec, reg = index // self.num_regs, index % self.num_regs
            imp_importance_rank_sec_reg_pair_results.append([self.regions[reg], self.activities[sec],
                                                             imp_importance_for_reg_impose[sec][reg]])
        return imp_importance_rank_sec_reg_pair_results

    def get_bloc(self, imp_importance_rank_sec_reg_pair_results, bloc_formation_strategy, reg_affected, num_item_bloc,
                 reg_impose, **kwargs):
        fight_back_alone_sec = self.get_best_fight_sector(reg_affected, reg_impose, 'imp')
        fight_back_alone_importance = self.importance_evaluation(reg_affected, reg_impose, fight_back_alone_sec, 'imp')

        reg_selection_result = [reg_affected]
        sec_selection_result = [fight_back_alone_sec]
        importance_results = [fight_back_alone_importance, ]

        if bloc_formation_strategy == 'one_sec_each_reg':
            ignore_country_list = [reg_affected]
            if reg_impose in ['chn', 'hkg', 'mac', 'twn']:
                ignore_country_list.extend(['chn', 'hkg', 'mac', 'twn'])
            for info in imp_importance_rank_sec_reg_pair_results:
                if info[0] not in ignore_country_list and info[0] not in reg_selection_result:
                    reg_selection_result.append(info[0])
                    sec_selection_result.append(info[1])
                    importance_results.append(info[2])
                if len(reg_selection_result) == num_item_bloc+1:
                    break

        if bloc_formation_strategy == 'more_than_one_sec_each_reg':
            ignore_country_list = []
            if reg_impose in ['chn', 'hkg', 'mac', 'twn']:
                ignore_country_list.extend(['chn', 'hkg', 'mac', 'twn'])
            for info in imp_importance_rank_sec_reg_pair_results:
                if info[0] not in ignore_country_list:
                    reg_selection_result.append(info[0])
                    sec_selection_result.append(info[1])
                    importance_results.append(info[2])
                    if len(reg_selection_result) == num_item_bloc+1:
                        break

        if bloc_formation_strategy == '1sec_with_bloc':
            for info in imp_importance_rank_sec_reg_pair_results:
                if info[0] in kwargs['bloc'] and info[0] not in reg_selection_result:
                    reg_selection_result.append(info[0])
                    sec_selection_result.append(info[1])
                    importance_results.append(info[2])
                if len(reg_selection_result) == num_item_bloc+1:
                    break

        if bloc_formation_strategy == 'secs_with_bloc':
            for info in imp_importance_rank_sec_reg_pair_results:
                if info[0] in kwargs['bloc'] or (info[0] == reg_affected and info[1] != fight_back_alone_sec):
                    reg_selection_result.append(info[0])
                    sec_selection_result.append(info[1])
                    importance_results.append(info[2])
                if len(reg_selection_result) == num_item_bloc+1:
                    break

        return reg_selection_result, sec_selection_result, importance_results
