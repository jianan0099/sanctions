import numpy as np
import utils


def RAS_matrix_balancing(A, u, v):
    X = A.copy()
    for i in range(500):
        R = u / np.sum(X, axis=1)
        X = X * R[:, None]
        S = v / np.sum(X, axis=0)
        X = X * S[None, :]
    return X


def MRIOT_adjust(Z_, VA_, F_, num_comm_):
    Y_without_VA = np.sum(Z_, axis=0)
    VA_by_country = utils.row_sum_n_col(VA_, num_comm_).flatten()
    U = Y_without_VA + VA_
    V = np.concatenate((Y_without_VA, VA_by_country))
    Z_F_MRIOT = np.concatenate((Z_, F_), axis=1)

    Z_F_MRIOT_adjusted = RAS_matrix_balancing(Z_F_MRIOT, U, V)
    return Z_F_MRIOT_adjusted


def arr_change_stop(arr_init, arr_new, thre=1e-8):
    thre_current = np.max(np.abs(arr_new-arr_init))
    return thre_current < thre


def get_P_change_based_on_c_change(pi, c_change, tau_change_current, theta_version1, theta_version2, num_comms_):
    c_tau = c_change[:, None] * tau_change_current
    P_change = pi * np.power(c_tau, theta_version1)
    P_change = utils.col_sum_each_n_row(P_change, num_comms_)
    P_change = np.power(P_change, theta_version2)
    return P_change


def get_c_change_based_on_P_change(P_change, gamma):
    return np.prod(np.power(P_change, gamma), axis=0)


def get_pi_change(c_change, tau_change, P_change, theta_version1, num_regs_):
    return np.power(c_change[:, None] * tau_change / np.tile(P_change, (num_regs_, 1)), theta_version1)


def get_MRIOT_sample(num_regs_, num_comms_):
    num_items_ = num_regs_ * num_comms_
    Z_init = np.random.randint(1, 4, (num_items_, num_items_))
    VA_init = np.random.randint(1, 4, num_items_)
    F_init = np.random.randint(1, 4, (num_items_, num_regs_))
    MRIOT = MRIOT_adjust(Z_init, VA_init, F_init, num_comms_)
    Z_final_, F_final_ = MRIOT[:, :num_items_], MRIOT[:, num_items_:]
    X_final_ = np.sum(Z_final_, axis=0) + VA_init
    VA_final_ = VA_init.copy()
    return Z_final_, F_final_, VA_final_, X_final_


def get_theta_r_version(theta_r_, num_regs_, num_items_):
    theta_r_version1 = np.tile(-theta_r_, num_regs_)[:, None]
    theta_r_version2_Z = np.tile(-1 / theta_r_[:, None], (1, num_items_))
    theta_r_version2_F = np.tile(-1 / theta_r_[:, None], (1, num_regs_))
    return theta_r_version1, theta_r_version2_Z, theta_r_version2_F


def trade_share_equilibrium(pi_firm_, pi_household_, gamma_intermediate_,
                            tau_Z_trade_cost_change_, tau_F_trade_cost_change_,
                            theta_r_, num_regs_, num_comms_,
                            iters=100, thre=1e-5):
    num_items_ = num_regs_ * num_comms_
    theta_r1, theta_r2_Z, theta_r2_F = get_theta_r_version(theta_r_, num_regs_, num_items_)
    c_production_cost_change = np.ones(num_items_)
    for i in range(iters):
        P_Z_change_current = get_P_change_based_on_c_change(pi_firm_, c_production_cost_change,
                                                            tau_Z_trade_cost_change_, theta_r1,
                                                            theta_r2_Z, num_comms_)
        c_change_new = get_c_change_based_on_P_change(P_Z_change_current, gamma_intermediate_)
        if arr_change_stop(c_production_cost_change, c_change_new, thre):
            c_production_cost_change = c_change_new
            break
        c_production_cost_change = c_change_new
    P_Z_change_final = get_P_change_based_on_c_change(pi_firm_, c_production_cost_change,
                                                      tau_Z_trade_cost_change_, theta_r1,
                                                      theta_r2_Z, num_comms_)
    P_F_change_final = get_P_change_based_on_c_change(pi_household_, c_production_cost_change,
                                                      tau_F_trade_cost_change_, theta_r1,
                                                      theta_r2_F, num_comms_)
    pi_firm_change = get_pi_change(c_production_cost_change, tau_Z_trade_cost_change_, P_Z_change_final,
                                   theta_r1, num_regs_)
    pi_household_change = get_pi_change(c_production_cost_change, tau_F_trade_cost_change_, P_F_change_final,
                                        theta_r1, num_regs_)
    return pi_firm_change, pi_household_change


def get_new_MRIOT_based_on_new_cost_share(X_, VA_, num_regs_, num_comms_, gamma_intermediate_, alpha_,
                                          pi_firm_, pi_household_, iters=100, thre=1e-5):
    X_ad = X_.copy()
    VA_ad = VA_.copy()
    for i in range(iters):
        VA_by_country_ad = utils.cal_VA_by_country(VA_ad, num_comms_)
        Z_ad = utils.recover_Z_by_new_cost_share(X_ad, gamma_intermediate_, pi_firm_, num_regs_)
        F_ad = utils.recover_F_by_new_cost_share(VA_by_country_ad, alpha_, pi_household_,
                                                 num_regs_)
        X_ad, VA_ad1 = utils.get_X_VA_by_Z_F(Z_ad, F_ad)
        if arr_change_stop(VA_ad1, VA_ad, thre) and \
                np.max(np.abs(utils.cal_VA_by_country(VA_ad1, num_comms_))-np.sum(F_ad, axis=0)) < thre:
            VA_ad = VA_ad1
            break
        VA_ad = VA_ad1
    return X_ad, Z_ad, F_ad, VA_ad



