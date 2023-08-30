%fig 2

% ------- figure setting --------------
font_size = 14;
line_width = 2;
markers = {'.', 'x', 'o','+', '.'};
MarkerSizes = [18, 14, 9, 12, 12];
colors_sender = [251/255, 128/255, 114/255;
                 252/255, 153/255, 142/255;
                 253/255, 179/255, 170/255;
                 253/255, 204/255, 199/255;
                 254/255, 230/255, 227/255];
             
colors_target = [128/255, 177/255, 211/255;
                 153/255, 193/255, 220/255;
                 179/255, 208/255, 229/255;
                 204/255, 224/255, 237/255;
                 230/255, 239/255, 246/255];
texts = char(97:118);
% -------------------------------------

% ----- read table -----------
share_threshold = '0.05';
path = strcat('results/sec_selection_example.xlsx');
scenarios = readtable(path,'Sheet','scenarios', 'ReadVariableNames', true);
results = readtable(path,'Sheet','results','ReadRowNames', true, 'ReadVariableNames', true);
sender_target_pair = table2cell(readtable(path,'Sheet','c_pair', 'ReadVariableNames', false));
sender_loss = readtable(path,'Sheet','sender_loss', 'ReadVariableNames', true);
target_loss = readtable(path,'Sheet','target_loss', 'ReadVariableNames', true);
share_info = readtable(path,'Sheet',strcat('share_summary_', share_threshold),...
    'ReadVariableNames', true);
% -------------------------------------


%% scenario info
all_senders = {};
all_targets = {};
all_comms = {};
sender_rank = [];
target_rank = [];
comm_share = [];

for c_pair_index=1:length(sender_target_pair)
    sender_target = char(sender_target_pair(c_pair_index));
    sender = sender_target(1:3);
    target = sender_target(5:7);
    all_senders{end+1} = sender;
    all_targets{end+1} = target;
    
    comms = {};
    comm_share_temp = [];
    sender_rank_temp = 0;
    target_rank_temp = 0;
    scenarios_size = size(scenarios); 
    rows = scenarios_size(1); 
    for row = 1:rows 
        if strcmp(string(table2cell(scenarios(row,'sender'))), sender) && ...
                strcmp(string(table2cell(scenarios(row,'target'))), target)
            comm = string(table2cell(scenarios(row,'comm')));
            comms{end+1} = comm;
            comm_share_temp = [comm_share_temp, table2cell(scenarios(row,'share'))];
            sender_rank_temp = table2cell(scenarios(row,'sender_rank'));
            target_rank_temp = table2cell(scenarios(row,'target_rank'));
        end
    end 
    sender_rank = [sender_rank, sender_rank_temp];
    target_rank = [target_rank, target_rank_temp];
    comm_share = [comm_share; comm_share_temp];
    all_comms{end+1} = comms;
end

%% draw
figure('Position', [32,146,1186,620])

figs = 1;
for row = 1:2
    if row==1
        loss_Info = sender_loss;
        colors = colors_sender;
    else
        loss_Info = target_loss;
        colors = colors_target;
    end
    
    
    for col=1:length(all_senders)
        sender = string(all_senders{1,col});
        target = string(all_targets{1,col});
        sender_rank_info = sender_rank{col};
        target_rank_info = target_rank{col};
        
        scenario_key_all = strcat(sender, '_', target, '_');
        subplot(3, length(all_senders), figs, ...
            'Position', ...
            [0.068 + (col-1) * 0.235, 0.71-(row-1)*0.3, 0.205, 0.22],...
            'Units','normalized');
        h_all = [];
        legend_info = {};
        legend_info_simple = {};
        for comm_i=1:length(all_comms{col})
            comm_name = all_comms{col}{comm_i};
            scenario_key = strcat(scenario_key_all, comm_name);
            
            legend_info{end+1} = strcat(upper(comm_name),' (', num2str(round(results{'eta', scenario_key}*100, 2)), '%)');
            legend_info_simple{end+1} = upper(comm_name);
            loss = loss_Info.(scenario_key) * 100;
            simulation_length = length(loss);
            
            h = plot(loss,...
                'Marker', char(markers(comm_i)), ...
                'MarkerIndices',1:10:simulation_length,...
                'MarkerSize', MarkerSizes(comm_i), ...
                'LineWidth', line_width,...
                'color', colors(comm_i,:));
            h_all = [h_all, h];
            hold on
        end
        
        legend(h_all, legend_info_simple, 'box', 'off', 'Position',[0.198 + (col-1) * 0.235, 0.722860561914673-(row-1)*0.3, 0.053119730185497, 0.130645161290322]);
        text(-0.08, 1.2, texts(figs), 'Units', 'Normalized','FontSize',font_size,'FontWeight','bold');
        set(gca,'FontSize',font_size)
        figs = figs+1;
        
        if row==1 && col==3
            ylim([-4e-3, 0])
        end
        
        if col==1
            if row==1
            ylabel({'The imposing country''s', 'GDP change (%)'}, 'Units','normalized','Position', [-0.18, 0.5,0])
            else
                ylabel({'The affected country''s', 'GDP change (%)'},'Units','normalized', 'Position', [-0.18, 0.5,0])
            end
        end
        
        if row==2
            xlabel('t [week]')
            xlim([0 simulation_length])
            xticks(0:20:simulation_length)
        end
        if row==1
            title(strcat(upper(sender),'(', num2str(sender_rank_info), ')-', ...
                upper(target), '(', num2str(target_rank_info), ')'),'Units','normalized',...
                'Position',...
                [0.500000794075843,1.094688642985666,0]);
        end
        
        xline(52,'--', 'LineWidth', line_width, 'Color', ...
            [135/255,135/255,135/255], 'HandleVisibility','off');
        
    end
    
end

row=3;
for col = 1:4
    sender = string(all_senders{1,col});
    target = string(all_targets{1,col});
    scenario_key_all = strcat(sender, '_', target, '_');

    subplot(3, length(all_senders), figs, ...
        'Position', ...
        [0.068 + (col-1) * 0.235, 0.71-(row-1)*0.3, 0.17, 0.2],...
        'Units','normalized');
    

    eta_info = [];
    share_info = [];
    comm_name_info = [];
    for comm_i=1:length(all_comms{col})
        comm_name = all_comms{col}{comm_i};
        comm_name_info = [comm_name_info, upper(comm_name)];
        scenario_key = strcat(scenario_key_all, comm_name);
        eta_info = [eta_info, results{'eta', scenario_key}*100];
        share_comm_i = comm_share{col,comm_i}*100;
        share_info = [share_info, share_comm_i];
    end

    yyaxis left
    H1 = bar((1:length(all_comms{col}))-0.2, share_info, 0.4);
    set(H1,'FaceColor',colors_sender(1,:))
    if col==1
    ylabel('Trade-to-GDP ratio (%)')
    end
    yyaxis right
    H2 = bar((1:length(all_comms{col}))+0.2, eta_info, 0.4);
    set(H2,'FaceColor',colors_target(1,:)) 
    if col==4
    ylabel({'Effectiveness of', 'restrictions (%)'})
    end
    set(gca, 'XTick', 1:length(all_comms{col}))
    set(gca,'xticklabel',comm_name_info)
    set(gca,'FontSize',font_size)
    xtickangle(90)
    text(-0.08, 1.2, texts(figs), 'Units', 'Normalized','FontSize',font_size,'FontWeight','bold');
    figs=figs+1;
end

saveas(gcf,strcat('figs/eco_info.eps'),'epsc')



