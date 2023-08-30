function [bloc_regs, not_join_in_base_payoff, not_join_in_alone_payoff,...
    join_in_payoff] = get_payoff_info(reg_impose,reg_target,bloc_form_rule, policy_duration, q)

eff_cal_path = strcat('results/cr_eff_full_cal_q',q,'_',reg_impose, '_', reg_target, bloc_form_rule, '_imp_', policy_duration, '.xlsx');

payoff_bloc_base_INFO = readtable(eff_cal_path,'Sheet','payoff_bloc_base',  'ReadVariableNames', true,'ReadRowNames', true);
payoff_bloc_alone_INFO = readtable(eff_cal_path,'Sheet','payoff_bloc_alone_no',  'ReadVariableNames', true,'ReadRowNames', true);
bloc_regs = table2cell(readtable(eff_cal_path,'Sheet','bloc_regs',  'ReadVariableNames', false,'ReadRowNames', false));

join_in_payoff = [];
not_join_in_base_payoff = [];
not_join_in_alone_payoff = [];
for i=1:length(bloc_regs)
    bloc_reg = char(bloc_regs(i));
    join_in_payoff = [join_in_payoff, payoff_bloc_base_INFO{'join_payoff',bloc_reg}];
    not_join_in_base_payoff = [not_join_in_base_payoff, payoff_bloc_base_INFO{'not_join_payoff',bloc_reg}];
    not_join_in_alone_payoff = [not_join_in_alone_payoff, payoff_bloc_alone_INFO{'not_join_payoff',bloc_reg}];
end

end

