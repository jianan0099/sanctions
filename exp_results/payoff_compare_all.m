% fig 5
% ------- figure setting --------------
font_size = 14;
line_width = 2.2;
markers = {'x', 'o', '+'};
markersizes = [12, 10, 10];
line_shape = {'-.', '--', ':'};
color_base = [251/255, 128/255, 114/255];
color_alone = [128/255, 177/255, 211/255];
color_bloc = [253,180,98]/255;
colors = [color_base; color_alone; color_bloc];
texts = char(97:118);
% -------------------------------------

reg_impose_all = {'chn','deu','chn','usa'};
reg_target_all = {'usa','fra','idn','sgp'};
bloc_form_rule = '';
policy_duration = '52';
q = '5';
strategy_name = {'Base', 'Individual', 'Collective'};


figure('Position', [71,160,944,548]);
figs=1;
for i=1:length(reg_impose_all)
    sender = string(reg_impose_all(i));
    target = string(reg_target_all(i));
    [bloc_regs, not_join_in_base_payoff, not_join_in_alone_payoff,...
    join_in_payoff] = get_payoff_info(sender,target, bloc_form_rule, policy_duration, q);
    
    for j=1:length(bloc_regs)
        row_num = ceil(figs/4);
        col_num = figs - 4 * (row_num-1);
        
        subplot(length(reg_impose_all), length(bloc_regs),figs,...
            'Units', 'Normalized',...
            'Position', [0.07 + (col_num-1) * 0.23, 0.77 - (row_num-1) * 0.22, 0.2,0.15])
        
        pay_off_collection = [not_join_in_base_payoff(j), not_join_in_alone_payoff(j), join_in_payoff(j)];
        b=bar(pay_off_collection, 'BarWidth', 0.7, 'FaceColor', 'flat');
        ylim([min(pay_off_collection) - (max(pay_off_collection)-min(pay_off_collection))*2.5e-1,...
            max(pay_off_collection) + (max(pay_off_collection)-min(pay_off_collection))*2.5e-1]);
        
        for strategy_index=1:3
            b.CData(strategy_index, :) = colors(strategy_index, :);
            
            text(strategy_index-0.5, pay_off_collection(strategy_index) + (max(pay_off_collection)-min(pay_off_collection))*1.2e-1,...
                strcat(num2str(pay_off_collection(strategy_index))),'FontSize',font_size-1);
        end
        
        if row_num==1 && col_num==1
            ylabel('\textbf{Expected payoff [$\pi^T(\mathcal{G})$]}', 'Interpreter',"latex",...
                'Units', 'Normalized',...
                'Position', [-0.15,-1.45136068631625,0]);
        end
        
        if col_num==1
            title(upper(bloc_regs(j)), 'Color', color_alone);
        else
             title(upper(bloc_regs(j)), 'Color', color_bloc);
        end
        
        if row_num==4
            xticklabels(strategy_name);
            xtickangle(45)
        else
             set(gca,'Xtick',[])
        end
        text(-0.08, 1.2, texts(figs), 'Units', 'Normalized','FontSize',font_size,'FontWeight','bold');
        
        set(gca,'FontSize',font_size,'Ytick',[])
    
        figs = figs + 1;
    end

end
saveas(gcf,strcat('figs/payoff_compare.eps'),'epsc')