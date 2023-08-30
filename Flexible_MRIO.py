# for generating new IO table after decoupling
import pickle
import numpy as np
import utils
import new_equilibrium_cal as NE
import pandas as pd
from itertools import combinations
import os


class IOEquilibrium:
    def __init__(self):
        with open('MRIOT_from_GTAP/adjusted_MRIOT_df.pkl', 'rb') as f:
            annual_MRIOT = pickle.load(f).to_numpy()
        with open('MRIOT_from_GTAP/regions_list.pkl', 'rb') as f:
            regions = pickle.load(f)
        with open('MRIOT_from_GTAP/activities_list.pkl', 'rb') as f:
            activities = pickle.load(f)
        trade_ela_df = pd.read_excel('code_mapping/trade_ela.xlsx')

        self.num_regs, self.num_comms = len(regions), len(activities)
        self.regions = regions
        self.activities = activities
        self.num_items = self.num_regs * self.num_comms
        self.annual_Z = annual_MRIOT[:self.num_items, :self.num_items]
        self.annual_F = annual_MRIOT[:self.num_items, self.num_items:]
        self.annual_VA = annual_MRIOT[-1, :self.num_items]
        self.annual_X = np.sum(annual_MRIOT, axis=1)[:-1]
        self.theta_r = np.zeros(self.num_comms)
        for _, row in trade_ela_df.iterrows():
            self.theta_r[activities.index(row['code'])] = row['trade_ela']
        self.pi_firm_base, self.pi_household_base, self.alpha_base, self.gamma_intermediate_base, self.gamma_va_base = \
            utils.get_important_paras(self.annual_Z, self.annual_F, self.annual_VA, self.annual_X,
                                      self.num_regs, self.num_comms)

    def get_new_equilibrium_by_changing_trade_cost(self, decoupling_scenario,
                                                   pi_iters=1000, pi_thre=1e-7, mriot_iters=1000, mriot_thre=1e-7,
                                                   **kwargs):

        tau_Z_trade_cost_change, tau_F_trade_cost_change = \
            self.get_decoupling_scenario_paras(decoupling_scenario, **kwargs)
        pi_firm_change, pi_household_change = \
            NE.trade_share_equilibrium(self.pi_firm_base, self.pi_household_base, self.gamma_intermediate_base,
                                       tau_Z_trade_cost_change, tau_F_trade_cost_change,
                                       self.theta_r, self.num_regs, self.num_comms,
                                       iters=pi_iters, thre=pi_thre)
        annual_X_ad, annual_Z_ad, annual_F_ad, annual_VA_ad = \
            NE.get_new_MRIOT_based_on_new_cost_share(self.annual_X, self.annual_VA, self.num_regs, self.num_comms,
                                                     self.gamma_intermediate_base, self.alpha_base,
                                                     pi_firm_change * self.pi_firm_base,
                                                     pi_household_change * self.pi_household_base,
                                                     iters=mriot_iters, thre=mriot_thre)
        return annual_X_ad, annual_Z_ad, annual_F_ad, annual_VA_ad

    def get_reg_index_range(self, reg_index):
        return range(self.num_comms * reg_index, self.num_comms * (reg_index + 1))

    def get_decoupling_scenario_paras(self, decoupling_scenario, **kwargs):
        tau_F_trade_cost_change = np.ones((self.num_items, self.num_regs))
        if decoupling_scenario == 'country_list':
            tau_Z_trade_cost_change = np.ones((self.num_items, self.num_items))
            for country_pair in combinations(kwargs['c_list'], 2):
                reg_index_range_list0 = self.get_reg_index_range(self.regions.index(country_pair[0]))
                reg_index_range_list1 = self.get_reg_index_range(self.regions.index(country_pair[1]))
                for i in reg_index_range_list0:
                    for j in reg_index_range_list1:
                        tau_Z_trade_cost_change[i, j] = np.inf
                        tau_Z_trade_cost_change[j, i] = np.inf
                if kwargs['change_F']:
                    tau_F_trade_cost_change[reg_index_range_list0, self.regions.index(country_pair[1])] = np.inf
                    tau_F_trade_cost_change[reg_index_range_list1, self.regions.index(country_pair[0])] = np.inf
            return tau_Z_trade_cost_change, tau_F_trade_cost_change
        if decoupling_scenario == 'US-CHN':
            tau_Z_trade_cost_change = np.ones((self.num_items, self.num_items))
            reg_index_range_US = self.get_reg_index_range(self.regions.index('usa'))
            reg_index_range_CHN = self.get_reg_index_range(self.regions.index('chn'))
            for i in reg_index_range_CHN:
                for j in reg_index_range_US:
                    tau_Z_trade_cost_change[i, j] = np.inf
                    tau_Z_trade_cost_change[j, i] = np.inf
            return tau_Z_trade_cost_change, tau_F_trade_cost_change

    def get_needed_IO(self, decoupling_scenario, days_in_each_time_step, **kwargs):
        if decoupling_scenario == 'base':
            annual_X1, annual_Z1, annual_F1, annual_VA1 = self.annual_X, self.annual_Z, self.annual_F, self.annual_VA
        elif decoupling_scenario == 'country_list':
            path_key = 'MRIOT_from_GTAP/Decoupling/'
            for i, c in enumerate(kwargs['c_list']):
                path_key += c
                if i < len(kwargs['c_list'])-1:
                    path_key += '_'
                else:
                    path_key += '_' + str(days_in_each_time_step)

            if os.path.exists(path_key):
                with open(path_key + '/' + 'annual_X.pkl', 'rb') as f:
                    annual_X1 = pickle.load(f)
                with open(path_key + '/' + 'annual_Z.pkl', 'rb') as f:
                    annual_Z1 = pickle.load(f)
                with open(path_key + '/' + 'annual_F.pkl', 'rb') as f:
                    annual_F1 = pickle.load(f)
                with open(path_key + '/' + 'annual_VA.pkl', 'rb') as f:
                    annual_VA1 = pickle.load(f)
            else:
                os.mkdir(path_key)
                annual_X1, annual_Z1, annual_F1, annual_VA1 = \
                    self.get_new_equilibrium_by_changing_trade_cost(decoupling_scenario, c_list=kwargs['c_list'],
                                                                    change_F=kwargs['change_F'])
                with open(path_key + '/' + 'annual_X.pkl', 'wb') as f:
                    pickle.dump(annual_X1, f)
                with open(path_key + '/' + 'annual_Z.pkl', 'wb') as f:
                    pickle.dump(annual_Z1, f)
                with open(path_key + '/' + 'annual_F.pkl', 'wb') as f:
                    pickle.dump(annual_F1, f)
                with open(path_key + '/' + 'annual_VA.pkl', 'wb') as f:
                    pickle.dump(annual_VA1, f)
        return annual_X1 / days_in_each_time_step, annual_Z1 / days_in_each_time_step, \
               annual_F1 / days_in_each_time_step, annual_VA1 / days_in_each_time_step


