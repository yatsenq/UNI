% Neuro_Image_Recog.m
% Розпізнавання тестових зображень навченими ШНМ
% Варіант 20: порівняння для goal = 1e-2, 1e-3, 1e-4

clear; clc; close all;

%% --- Конфігурація ---
testDir = 'Neuro_Recogn';
netFiles = {'net_lm_1e-2.mat', 'net_lm_1e-3.mat', 'net_lm_1e-4.mat'};
netLabels = {'1e-2', '1e-3', '1e-4'};

classNames = {'tau', 'x', 'Z', 'X'};

% Список тестових файлів (16 шт) та очікувані класи
testFiles = {
    'tau1_S2', 'tau1_R2', 'tau1_D2', 'tau1_C2', ...
    'x1_S2',   'x1_R2',   'x1_D2',   'x1_C2',   ...
    'Z1_S2',   'Z1_R2',   'Z1_D2',   'Z1_C2',   ...
    'X1_S2',   'X1_R2',   'X1_D2',   'X1_C2'
};
trueLabels = [1 1 1 1,  2 2 2 2,  3 3 3 3,  4 4 4 4];

numTests = length(testFiles);

fprintf('Поточна папка: %s\n\n', pwd);

%% --- Цикл по 3 навченим мережам ---
for n = 1:length(netFiles)
    
    % Завантажити мережу
    if ~isfile(netFiles{n})
        error('Файл %s не знайдено! Переконайся, що навчання виконано.', netFiles{n});
    end
    load(netFiles{n}, 'net');
    fprintf('========================================\n');
    fprintf('РОЗПІЗНАВАННЯ: мережа з goal = %s\n', netLabels{n});
    fprintf('========================================\n\n');
    
    correct = 0;
    results = struct('File', {}, 'Y', {}, 'Pred', {}, 'True', {}, 'OK', {});
    
    for i = 1:numTests
        fname = fullfile(testDir, [testFiles{i} '.bmp']);
        
        % Перевірка чи існує файл
        if ~isfile(fname)
            error('Файл не знайдено: %s. Перевір шлях %s', fname, pwd);
        end
        
        % Зчитування та підготовка
        img = imread(fname);
        if size(img, 3) == 3
            img = rgb2gray(img);
        end
        x_vec = im2double(img(:));
        
        % Розпізнавання
        Y = net(x_vec);
        [~, predClass] = max(Y);
        
        isOK = (predClass == trueLabels(i));
        if isOK, correct = correct + 1; end
        
        % Збереження результату
        results(i).File  = testFiles{i};
        results(i).Y     = Y;
        results(i).Pred  = predClass;
        results(i).True  = trueLabels(i);
        results(i).OK    = isOK;
        
        % Вивід у командне вікно
        yStr = sprintf('%.3f  ', Y);
        status = 'OK';
        if ~isOK, status = 'НЕВДАЧА'; end
        
        fprintf('%-15s | Y=[%s] | Розпізнано: %-4s | Очікувалось: %-4s | %s\n', ...
            testFiles{i}, yStr, classNames{predClass}, classNames{trueLabels(i)}, status);
    end
    
    % Підсумок по мережі
    acc = correct / numTests * 100;
    fprintf('\n>>> Точність для goal=%s: %d/%d = %.1f%%\n\n', ...
        netLabels{n}, correct, numTests, acc);
    
    % --- Діаграми вихідних векторів Y (4 графіки по 4 зображення) ---
    figure('Name', sprintf('Y vectors (goal=%s)', netLabels{n}), 'Position', [100 100 1200 800]);
    for i = 1:numTests
        subplot(4, 4, i);
        bar(results(i).Y, 'FaceColor', [0.2 0.5 0.8]);
        set(gca, 'XTickLabel', classNames, 'FontSize', 8);
        title(sprintf('%s', testFiles{i}), 'FontSize', 9);
        ylim([-0.2 1.2]);
        grid on;
        
        % Підсвітка правильного класу зеленим
        hold on;
        bar(results(i).True, results(i).Y(results(i).True), 'FaceColor', [0.2 0.8 0.2]);
        hold off;
    end
    sgtitle(sprintf('Вихідні вектори Y (goal = %s)', netLabels{n}));
end

fprintf('Готово! Перевір графіки та таблицю у командному вікні.\n');