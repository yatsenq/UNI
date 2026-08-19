% Neuro_Image_Train.m
% Навчання ШНМ для 3 значень MSE (1e-2, 1e-3, 1e-4)
% Варіант 20: каскадна мережа newcf, logsig+tansig, trainlm

clear; clc; close all;

%% s1 --- Read Vector ---
p_Read_Vector_1;

%% s2-s5 --- Налаштування мережі (базова структура) ---
goals = [1e-2, 1e-3, 1e-4];
results = table('Size', [3 4], ...
    'VariableTypes', {'double','double','double','string'}, ...
    'VariableNames', {'Goal', 'Epochs', 'Time_sec', 'FileName'});

for g = 1:length(goals)
    goalVal = goals(g);
    
    % Створити каскадну мережу (парний варіант → newcf)
    net = newcf(P, T, [16 12], {'logsig', 'tansig'});
    
    % Вимкнути розбивку на підвибірки (бо всього 20 зразків)
    net.divideFcn = '';
    
    % Алгоритм та параметри
    net.trainFcn = 'trainlm';
    net.performFcn = 'mse';
    net.trainParam.epochs = 1500;
    net.trainParam.goal   = goalVal;
    net.trainParam.time   = 120;
    
    fprintf('\n=== Навчання %d/3: goal = %.0e ===\n', g, goalVal);
    
    % Переініціалізація ваг перед кожним запуском
    net = init(net);
    
    % Навчання
    tic;
    [net, tr] = train(net, P, T);
    t_train = toc;
    
    % Збереження
    saveName = sprintf('net_lm_%.0e.mat', goalVal);
    save(saveName, 'net', 'tr', 't_train');
    
    % Запис результатів
    results.Goal(g)     = goalVal;
    results.Epochs(g)   = tr.num_epochs;
    results.Time_sec(g) = t_train;
    results.FileName(g) = saveName;
    
    fprintf('Епох: %d | Час: %.3f сек | MSE: %.5e\n', ...
        tr.num_epochs, t_train, tr.best_perf);
end

disp(' ');
disp('=== ЗВЕДЕНА ТАБЛИЦЯ ===');
disp(results);
fprintf('Готово! Створено файли: net_lm_1e-2.mat, net_lm_1e-3.mat, net_lm_1e-4.mat\n');