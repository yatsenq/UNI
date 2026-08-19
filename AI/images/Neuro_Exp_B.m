% Neuro_Exp_B.m
% Експеримент Б: вплив кількості нейронів QV1 (шар 1) на час навчання
% Варіант 20 (парний) → змінюємо шар 1
% Метод Монте-Карло: m=7 запусків

clear; clc; close all;

%% s1 --- Зчитати P і T ---
p_Read_Vector_1;

%% --- Параметри Монте-Карло ---
m = 7;              % кількість випробувань
gamma = 0.95;       % надійність
t_gamma = 2.45;     % аргумент Лапласа при gamma=0.95 (для m=7 з таблиць)
delta1 = 0.1;       % задана верхня межа похибки

% Варіант 20 — парний → змінюємо кількість нейронів у шарі 1 (QV1)
% Базова структура з методички/прикладу: [16 12]
qv1_values = [8, 16, 24];   % -50%, база 0%, +50%
qv2 = 12;                   % другий шар незмінний
labels = {'QV1=8 (-50%)', 'QV1=16 (база)', 'QV1=24 (+50%)'};

fprintf('\n');
fprintf('=====================================================\n');
fprintf('ЕКСПЕРИМЕНТ Б: Монте-Карло (Варіант 20, парний)\n');
fprintf('Зміна кількості нейронів у шарі 1, m=%d, gamma=%.2f\n', m, gamma);
fprintf('=====================================================\n\n');

allResults = struct();

%% --- Цикл по трьом структурам мережі ---
for qi = 1:3
    QV1 = qv1_values(qi);
    
    fprintf('--- %s (шар 2 = %d) ---\n', labels{qi}, qv2);
    
    t_k = zeros(1, m);  % часи навчання
    
    for k = 1:m
        % Створення каскадної мережі
        net_exp = newcf(P, T, [QV1 qv2], {'logsig', 'tansig'});
        
        % Вимкнути розбивку на вибірки (бо мало даних)
        net_exp.divideFcn = '';
        
        % Налаштування навчання
        net_exp.trainFcn = 'trainlm';
        net_exp.performFcn = 'mse';
        net_exp.trainParam.epochs = 1500;
        net_exp.trainParam.goal   = 1e-3;   % фіксовано за умовою п.6
        net_exp.trainParam.time   = 120;
        net_exp.trainParam.showWindow = false;  % не показувати вікно навчання
        
        % Переініціалізація ваг
        net_exp = init(net_exp);
        
        % Навчання та вимір часу
        tic;
        [net_exp, tr] = train(net_exp, P, T);
        t_k(k) = toc;
        
        fprintf('  Запуск %d/%d: час = %.4f сек, епох = %d, MSE = %.5e\n', ...
            k, m, t_k(k), tr.num_epochs, tr.best_perf);
    end
    
    %% --- Статистична обробка (Додаток А) ---
    % A.1 Середнє значення (математичне сподівання)
    tc = mean(t_k);
    
    % A.2 Середнє квадратичне відхилення (несміщене)
    sigma = sqrt(sum((t_k - tc).^2) / m);
    
    % Виправлене середнє квадратичне відхилення
    s = sqrt(m / (m - 1)) * sigma;
    
    % A.3 Верхня межа похибки визначення часу
    delta = t_gamma * s / sqrt(m);
    
    % Формула 3.6: мінімальна кількість випробувань
    m1 = ceil((t_gamma * s / delta1)^2);
    
    % Збереження
    allResults(qi).Label   = labels{qi};
    allResults(qi).QV1     = QV1;
    allResults(qi).t_k     = t_k;
    allResults(qi).tc      = tc;
    allResults(qi).sigma   = sigma;
    allResults(qi).s       = s;
    allResults(qi).delta   = delta;
    allResults(qi).m1      = m1;
    
    fprintf('  >> tc = %.4f с | sigma = %.4f | delta = %.4f | m1 = %d\n\n', ...
        tc, sigma, delta, m1);
end

%% --- Вивід зведеної таблиці ---
fprintf('\n');
fprintf('================================================================================\n');
fprintf('ЗВЕДЕНА ТАБЛИЦЯ (Додаток А)\n');
fprintf('================================================================================\n');
fprintf('%-18s | %-12s | %-10s | %-10s | %-10s | %-4s\n', ...
    'Структура', 't_k (сек)', 'tc (с)', 'sigma', 'delta', 'm1');
fprintf('--------------------------------------------------------------------------------\n');

for qi = 1:3
    r = allResults(qi);
    tStr = sprintf('%.2f ', r.t_k);
    fprintf('%-18s | %-12s | %-10.4f | %-10.4f | %-10.4f | %-4d\n', ...
        r.Label, tStr, r.tc, r.sigma, r.delta, r.m1);
end
fprintf('================================================================================\n');

%% --- Діаграма середнього часу ---
figure('Name', 'Exp B: Time vs QV1', 'Position', [300 300 600 400]);
bar([allResults(1).tc, allResults(2).tc, allResults(3).tc], ...
    'FaceColor', [0.3 0.6 0.9]);
set(gca, 'XTickLabel', {allResults(1).Label, allResults(2).Label, allResults(3).Label});
ylabel('Середній час навчання tc, с');
xlabel('Кількість нейронів у шарі 1 (QV1)');
title('Залежність часу навчання від QV1 (Варіант 20, MSE=1e-3)');
grid on;

% Додамо значення над стовпчиками
hold on;
for qi = 1:3
    text(qi, allResults(qi).tc + 0.05*max([allResults.tc]), ...
        sprintf('%.3f', allResults(qi).tc), ...
        'HorizontalAlignment', 'center', 'FontWeight', 'bold');
end
hold off;

fprintf('\nЕксперимент Б завершено. Збережи графік та таблицю для звіту.\n');