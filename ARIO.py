import utils
import numpy as np
from policy_process import Policy


class ARIOModel:
    def __init__(self, Z, F, VA, X, regions, activities, num_time_steps_in_inv_init=4):
        self.Z = Z
        self.F = F
        self.VA = VA
        self.X = X
        self.regions = regions
        self.activities = activities
        self.num_regs = len(regions)
        self.num_comms = len(activities)
        self.num_items = self.num_regs * self.num_comms
        self.num_time_steps_in_inv_init = num_time_steps_in_inv_init
        self.pi_firm_base, self.pi_household_base, self.alpha_base, self.gamma_intermediate_base, self.gamma_va_base = \
            utils.get_important_paras(self.Z, self.F, self.VA, self.X,
                                      self.num_regs, self.num_comms)
        self.sum_input_product = utils.col_sum_each_n_row(Z, self.num_comms)
        self.A_Cobb_Douglas = self.X / (np.prod(np.power(self.sum_input_product, self.gamma_intermediate_base), axis=0)
                                        * np.power(self.VA, self.gamma_va_base))
        self.policy_model = Policy(regions, activities, Z)

    def define_labour_input(self):
        return self.VA.copy()

    def production_func(self, labour, inv):
        return np.minimum(np.min(inv / self.gamma_intermediate_base, axis=0), labour / self.gamma_va_base)

    def input_amount_cal(self, product_to_firms, product_to_households):
        product_to_ = np.sum(product_to_firms, axis=1) + np.sum(product_to_households, axis=1)
        return self.gamma_intermediate_base * product_to_[None, :], self.gamma_va_base * product_to_

    def target_inv_define(self, x):
        using_init_index = x < 1e-8
        x[using_init_index] = self.X[using_init_index].copy()
        return self.gamma_intermediate_base * x[None, :] * (self.num_time_steps_in_inv_init + 1)

    def adjust_order_weight(self, x_relative, info_type_):
        if info_type_ == 'Z':
            return utils.source_prefer(self.Z * x_relative[:, None], self.num_regs, self.num_comms)
        if info_type_ == 'F':
            return utils.source_prefer(self.F * x_relative[:, None], self.num_regs, self.num_comms)

    def general_weight_adjust(self, INFO, policy_impact, type_):
        for i in range(len(policy_impact[0])):
            region_imposing_policy = policy_impact[0][i]
            firms_affected = policy_impact[1][i]
            relative_change_in_INFO = policy_impact[2][i]
            if type_ == 'to_firm':
                INFO[firms_affected,
                     utils.get_reg_index_range(region_imposing_policy, self.num_comms)] *= relative_change_in_INFO
            elif type_ == 'to_reg':
                INFO[firms_affected, region_imposing_policy] *= relative_change_in_INFO

    def adjust_order_weight_firm_specific(self, x_relative, type_, t, t_stop):
        if type_ == 'to_firm':
            if t > t_stop:
                return utils.source_prefer(self.Z * x_relative[:, None], self.num_regs, self.num_comms)
            else:
                return utils.source_prefer(self.Z_after_import_control * x_relative[:, None], self.num_regs,
                                           self.num_comms)
        if type_ == 'to_reg':
            if t > t_stop:
                return utils.source_prefer(self.F * x_relative[:, None], self.num_regs, self.num_comms)
            else:
                return utils.source_prefer(self.F_after_import_control * x_relative[:, None], self.num_regs,
                                           self.num_comms)

    def cal_household_demand_for_each_product(self, value_added_input):
        value_added_by_country = utils.cal_VA_by_country(value_added_input, self.num_comms)
        return self.alpha_base * value_added_by_country[None, :]

    def order_placing_prefer(self, x_, t, t_stop):
        x_relative = x_ / self.X
        adjust_product_input_fraction_for_F = \
            self.adjust_order_weight_firm_specific(x_relative, 'to_firm', t, t_stop)
        adjust_product_input_fraction_for_H = \
            self.adjust_order_weight_firm_specific(x_relative, 'to_reg', t, t_stop)
        return adjust_product_input_fraction_for_F, adjust_product_input_fraction_for_H

    def order_distribution(self, orderF, orderH, export_control_info, firm_only):
        if not firm_only:
            self.general_weight_adjust(orderH, export_control_info, 'to_reg')
        self.general_weight_adjust(orderF, export_control_info, 'to_firm')
        total_order_t = np.sum(orderF, axis=1) + np.sum(orderH, axis=1)
        total_order_t_reshape = total_order_t[:, None]
        if sum(total_order_t != 0) == len(total_order_t):
            orderF_distribution_fraction = np.divide(orderF, total_order_t_reshape)
            orderH_distribution_fraction = np.divide(orderH, total_order_t_reshape)
        else:
            orderF_distribution_fraction = utils.division_define(orderF, total_order_t_reshape, 0)
            orderH_distribution_fraction = utils.division_define(orderH, total_order_t_reshape, 0)
        return total_order_t, orderF_distribution_fraction, orderH_distribution_fraction

    def IO_trans(self, T, policy_scenario, **policy_kwargs):
        self.Z_after_import_control, self.F_after_import_control = self.Z.copy(), self.F.copy()
        Inv_t = self.num_time_steps_in_inv_init * self.sum_input_product
        product_to_firms = np.array(self.Z)
        orderF_t = np.array(self.Z)
        orderH_t = np.array(self.F)
        import_tariffs_impact_base, export_control_info_base, firm_only_base, policy_duration = \
            self.policy_model.get_policy_results(policy_scenario, **policy_kwargs)
        self.general_weight_adjust(self.Z_after_import_control, import_tariffs_impact_base, 'to_firm')
        if not firm_only_base:
            self.general_weight_adjust(self.F_after_import_control, import_tariffs_impact_base, 'to_reg')
        export_control_info_t, firm_only_t = export_control_info_base.copy(), firm_only_base
        results_dict = {'va_actual': []}

        for t in range(T):
            if t > policy_duration:
                export_control_info_t, firm_only_t = [[], [], []], True
            total_order_t, orderF_distribution_fraction_t, orderH_distribution_fraction_t = \
                self.order_distribution(orderF_t, orderH_t, export_control_info_t, firm_only_t)

            temporal_received_products_F = utils.col_sum_each_n_row(product_to_firms, self.num_comms)
            labour_input_t = self.define_labour_input()
            Inv_t = Inv_t + temporal_received_products_F
            x_max_t = self.production_func(labour_input_t, Inv_t)
            x_actual_t = np.minimum(x_max_t, total_order_t)
            x_actual_t_reshape = x_actual_t[:, None]
            product_to_firms = orderF_distribution_fraction_t * x_actual_t_reshape
            product_to_households = orderH_distribution_fraction_t * x_actual_t_reshape
            used_inv, used_labour = self.input_amount_cal(product_to_firms, product_to_households)
            Inv_t = Inv_t - used_inv
            Inv_t[Inv_t < 0] = 0
            results_dict['va_actual'].append(used_labour)
            Target_Inv_t = self.target_inv_define(x_max_t)
            DemF_product_t = Target_Inv_t - Inv_t
            DemF_product_t[DemF_product_t < 0] = 0
            DemH_product_t = utils.col_sum_each_n_row(self.F, self.num_comms)
            adjust_product_input_fraction_for_F, adjust_product_input_fraction_for_H = \
                self.order_placing_prefer(x_max_t, t, policy_duration)
            orderF_t = DemF_product_t[None, :, :] * np.reshape(adjust_product_input_fraction_for_F,
                                                               (self.num_regs, self.num_comms, self.num_items))
            orderF_t = np.reshape(orderF_t, (self.num_items, self.num_items))
            orderH_t = DemH_product_t[None, :, :] * np.reshape(adjust_product_input_fraction_for_H,
                                                               (self.num_regs, self.num_comms, self.num_regs))
            orderH_t = np.reshape(orderH_t, (self.num_items, self.num_regs))
        return results_dict

