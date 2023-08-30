% fig 4

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
texts = char(99:118);
% -------------------------------------

reg_impose_all = {'chn','deu','chn','usa'};
reg_target_all = {'usa','fra','idn','sgp'};
fig_source_index = [1,2,5,6];
ylim_sub_axis = [3, 5, 15, 6];
bloc_form_rule = '';
policy_duration = '52';
q = '5';
strategy_name = {'Base', 'Individual', 'Collective'};


figure('Position', [70,116,736,680]);
for i=1:length(reg_impose_all)
    sender = string(reg_impose_all(i));
    target = string(reg_target_all(i));
    [sender_loss, target_loss, eff_sanction, bloc_info, sender_loss_decouple, target_loss_decouple] = ...
     get_eff_info(sender,target,bloc_form_rule, policy_duration,q);
    
 disp(bloc_info)
    
    simulation_length = length(sender_loss(:,1));
    
    if i<=2
        fig_y_start = 0.78;
    else
        fig_y_start = 0.76;
    end

    %sender
    figs=fig_source_index(i);
    row_num = ceil(figs/2);
    col_num = figs - 2 * (row_num-1);
    subplot(4,2,figs,'Position',  ...
        [0.1 + (col_num-1) * 0.47, ...
         fig_y_start - (row_num-1) * 0.23,...
         0.42,0.165])
    h_all = [];
    for loss_index=1:3
        h = plot(sender_loss(:,loss_index)*100,...
            'LineStyle', char(line_shape(loss_index)),...
            'LineWidth', line_width,...
            'color', colors(loss_index,:));
        hold on
        h_all = [h_all, h];
    end
     xline(52,'--', 'LineWidth', line_width, 'Color', ...
            [135/255,135/255,135/255], 'HandleVisibility','off');
    text(-0.08, 1.2, texts(figs), 'Units', 'Normalized','FontSize',font_size,'FontWeight','bold');
    text(0.51, 0.1, strcat(num2str(round(sender_loss_decouple*100,2)), '%'), 'Units', 'Normalized','FontSize',font_size);
    xlim([0 simulation_length])
    xticks(0:20:simulation_length)
    title(strcat('Sender: ', upper(sender), '-', 'Target: ', upper(target)),...
         'Units', 'Normalized',...
        'Position', [0.5,1.070758928571428,0]);
    if i==1 || i==3
        ylabel({'Sender''s GDP', 'change (%)'},'Units', 'Normalized', 'Position', [-0.12,0.5,0]);
    end
    set(gca,'FontSize',font_size)
    
    subAX = axes('position',[0.38 + (col_num-1) * 0.47, 0.82 - (row_num-1) * 0.24, 0.12,0.1]);
    b = bar(eff_sanction, 'BarWidth', 0.7, 'FaceColor', 'flat');
    for strategy_index=1:3
        b.CData(strategy_index, :) = colors(strategy_index, :);
        if strategy_index>1
            if strategy_index==2
                temp_val = 0.5;
            else
                temp_val = 0;
            end

            text(strategy_index-temp_val, eff_sanction(strategy_index)+ylim_sub_axis(i)*0.15,...
                strcat(num2str(round((1-eff_sanction(strategy_index)/eff_sanction(1))*100,0)), ...
                '%'),'FontSize',font_size-1);
        end
          
    end
    if i==1
        ylim([0, 3]);
        yticks([0 1 2 3]);
    end
    
    if i==2
        ylim([0, 5]);
        yticks([0 2.5 5]);
    end
    
    if i==3
        ylim([0, 15]);
        yticks([0 5 10 15]);
    end
    
    if i==4
        ylim([0, 6]);
        yticks([0 2 4 6]);
    end
    ylabel('\eta (%)','FontWeight','bold');
    box off
    set(gca,'FontSize',font_size-2,'xtick',[])
    disp(eff_sanction)

    
    %target
    figs = fig_source_index(i)+2;
    row_num = ceil(figs/2);
    col_num = figs - 2 * (row_num-1);
        subplot(4,2,figs,'Position',  ...
        [0.1 + (col_num-1) * 0.47, ...
         fig_y_start - (row_num-1) * 0.23,...
         0.42,0.165])
    h_all = [];
    for loss_index=1:3
        h = plot(target_loss(:,loss_index)*100,...
            'LineStyle', char(line_shape(loss_index)),...
            'LineWidth', line_width,...
            'color', colors(loss_index,:));
        hold on
        h_all = [h_all, h];
    end
     xline(52,'--', 'LineWidth', line_width, 'Color', ...
            [135/255,135/255,135/255], 'HandleVisibility','off');
    text(-0.08, 1.2, texts(figs), 'Units', 'Normalized','FontSize',font_size,'FontWeight','bold');
    text(0.51, 0.1, strcat(num2str(round(target_loss_decouple*100,2)), '%'), 'Units', 'Normalized','FontSize',font_size);
    xlim([0 simulation_length])
    xticks(0:20:simulation_length)
    legend(h_all, strategy_name, 'box', 'off','Units', 'Normalized',...
          'Position',[0.3 + (col_num-1) * 0.47, 0.58 - (row_num-2) * 0.23, 0.23, 0.0735]);
    set(gca,'FontSize',font_size)
    if i>length(reg_impose_all)-2
        xlabel('t [week]')
    end
    
    if i==1 || i==3
        ylabel({'Target''s GDP', 'change (%)'},'Units', 'Normalized', 'Position', [-0.12,0.5,0]);
    end
    
    
end
saveas(gcf,strcat('figs/eff_base.eps'),'epsc')