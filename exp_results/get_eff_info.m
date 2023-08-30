function [sender_loss, target_loss, eff_sanction, bloc_info,sender_loss_decouple, target_loss_decouple] = get_eff_info(reg_impose,reg_target,...
    bloc_form_rule, policy_duration, q)
loss_path = strcat('results/cr_eff_full_',reg_impose, '_', reg_target, bloc_form_rule, '_imp_', policy_duration, '.xlsx');
loss_INFO = readtable(loss_path, 'ReadVariableNames', true);
decouple_INFO = readtable(loss_path, 'Sheet','decoupling_va_change_by_country', 'ReadVariableNames',true);
eff_cal_path = strcat('results/cr_eff_full_cal_q',q,'_',reg_impose, '_', reg_target, bloc_form_rule, '_imp_', policy_duration, '.xlsx');
eff_sanction_INFO = readtable(eff_cal_path,'Sheet','eff_sanction',  'ReadVariableNames', true);
sender_loss_decouple = decouple_INFO{1,reg_impose};
target_loss_decouple = decouple_INFO{1,reg_target};
%% loss for sender
sender_loss_base_header = string(strcat(reg_impose, '_', reg_impose, '_', reg_target, '_base'));
sender_loss_base = loss_INFO.(sender_loss_base_header);

sender_loss_alone_header = string(strcat(reg_impose, '_', reg_impose, '_', reg_target, '_alone_no'));
sender_loss_alone = loss_INFO.(sender_loss_alone_header);

sender_loss_bloc_header = string(strcat(reg_impose, '_', reg_impose, '_', reg_target, '_bloc_no'));
sender_loss_bloc = loss_INFO.(sender_loss_bloc_header);

sender_loss = [sender_loss_base, sender_loss_alone, sender_loss_bloc];
%% loss for target
target_loss_base_header = string(strcat(reg_target, '_', reg_impose, '_', reg_target, '_base'));
target_loss_base = loss_INFO.(target_loss_base_header);

target_loss_alone_header = string(strcat(reg_target, '_', reg_impose, '_', reg_target, '_alone_no'));
target_loss_alone = loss_INFO.(target_loss_alone_header);

target_loss_bloc_header = string(strcat(reg_target, '_', reg_impose, '_', reg_target, '_bloc_no'));
target_loss_bloc = loss_INFO.(target_loss_bloc_header);
target_loss = [target_loss_base, target_loss_alone, target_loss_bloc];

eff_sanc_base = string(strcat(reg_impose, '_', reg_target, '_base'));
eff_sanc_alone = string(strcat(reg_impose, '_', reg_target, '_alone_no'));
eff_sanc_bloc = string(strcat(reg_impose, '_', reg_target, '_bloc_no'));
eff_sanction = [eff_sanction_INFO.(eff_sanc_base), ...
    eff_sanction_INFO.(eff_sanc_alone),...
    eff_sanction_INFO.(eff_sanc_bloc)]*100;

bloc_info = readtable(eff_cal_path,'Sheet','bloc_regs', 'ReadVariableNames', false);
end


