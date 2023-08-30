import numpy as np


def row_sum_n_col(array_, n_col):
    if len(np.shape(array_)) == 1:
        return np.sum(np.reshape(array_, (int(len(array_) / n_col), n_col)), axis=1)
    return np.sum(np.reshape(array_, (-1, int(np.shape(array_)[1] / n_col), n_col)), axis=2)


def col_sum_each_n_row(array_, n_row):
    return np.sum(np.reshape(array_, (-1, n_row, int(np.shape(array_)[1]))), axis=0)


def recover_Z_by_new_cost_share(X, gamma_intermediate, pi_firm, num_regs_):
    return pi_firm * np.tile(gamma_intermediate, (num_regs_, 1)) * X[None, :]


def recover_F_by_new_cost_share(VA_by_country, alpha, pi_household, num_regs_):
    return pi_household * np.tile(alpha, (num_regs_, 1)) * VA_by_country[None, :]


def get_X_VA_by_Z_F(Z, F):
    X = np.sum(Z, axis=1) + np.sum(F, axis=1)
    VA = X - np.sum(Z, axis=0)
    return X, VA


def cal_VA_by_country(VA_, num_comms_):
    return row_sum_n_col(VA_, num_comms_)


def get_reg_sec_pair_from_each_reg(INFO, num_regs_, num_comms_):
    return np.concatenate([np.reshape(INFO[:, col], (num_regs_, num_comms_)) for col in range(len(INFO[0]))], axis=1)


def source_prefer(INFO, num_regs_, num_comms_):
    INFO_sum_by_product_type = col_sum_each_n_row(INFO, num_comms_)
    pi_source_prefer = np.reshape(INFO, (num_regs_, num_comms_, len(INFO[0]))) / INFO_sum_by_product_type[None, :, :]
    pi_source_prefer = np.reshape(pi_source_prefer, (num_regs_ * num_comms_, len(INFO[0])))
    return pi_source_prefer


def get_important_paras(Z_final_, F_final_, VA_final_, X_final_, num_regs_, num_comms_):
    Z_sum_by_product_type = col_sum_each_n_row(Z_final_, num_comms_)
    F_sum_by_product_type = col_sum_each_n_row(F_final_, num_comms_)
    pi_source_prefer_firm = source_prefer(Z_final_, num_regs_, num_comms_)
    pi_source_prefer_household = source_prefer(F_final_, num_regs_, num_comms_)
    gamma_intermediate_share = Z_sum_by_product_type / X_final_[None, :]
    gamma_va_share = VA_final_ / X_final_
    VA_by_country = cal_VA_by_country(VA_final_, num_comms_)
    alpha_house_consumption_prefer = F_sum_by_product_type / VA_by_country[None, :]
    return pi_source_prefer_firm, pi_source_prefer_household, alpha_house_consumption_prefer, \
           gamma_intermediate_share, gamma_va_share

def get_multiple_reg_info_row_pick(INFO, reg_index_list, num_comms_):
    return np.concatenate([INFO[get_reg_index_range(reg_index, num_comms_)] for reg_index in reg_index_list], axis=0)


def get_firm_index(reg_index_, comm_index_, num_comms_):
    return reg_index_ * num_comms_ + comm_index_


def get_reg_index_range(reg_index_, num_comms_):
    return range(num_comms_ * reg_index_, num_comms_ * (reg_index_ + 1))


def get_domestic_supply(Z_, num_comms_, num_regs_):
    num_items_ = num_comms_ * num_regs_
    domestic_supply = np.zeros((num_comms_, num_items_))
    for reg_index in range(num_regs_):
        reg_range = get_reg_index_range(reg_index, num_comms_)
        for comm_index in range(num_comms_):
            firm_index = reg_index * num_comms_ + comm_index
            domestic_supply[:, firm_index] = Z_[reg_range, firm_index]
    return domestic_supply


def get_trade_between_two_countries(trade_info, regions, reg1, reg2):
    return trade_info[regions.index(reg1) * 65:(regions.index(reg1) + 1) * 65][:,
           regions.index(reg2) * 65:(regions.index(reg2) + 1) * 65]


def get_total_trade_between_countries(trade_info, regions):
    total_trade = np.zeros((len(regions), len(regions)))
    for reg1_index in range(len(regions)):
        for reg2_index in range(len(regions)):
            total_trade[reg1_index][reg2_index] = np.sum(get_trade_between_two_countries(trade_info, regions,
                                                                                         regions[reg1_index],
                                                                                         regions[reg2_index]))
    return total_trade


def get_final_trade_between_two_countries(final_trade_info, regions, reg1, reg2):
    return final_trade_info[regions.index(reg1) * 65:(regions.index(reg1) + 1) * 65][regions.index(reg2)]


def division_define(arr_x, arr_y, default_value):
    return np.divide(arr_x, arr_y, out=np.ones_like(arr_x) * float(default_value), where=arr_y != 0)
