% p_Read_Vector_1.m
% Зчитування зображень навчальної вибірки та формування матриць P і T
% Варіант 20: символи τ, x, Z, X

% Відкрити файл з іменами файлів та номерами класів
fid_files = fopen('Neuro_Train/File_Name_tx1.txt', 'r');
files = textscan(fid_files, '%d %s');
fclose(fid_files);

num_images = length(files{1});  % кількість зображень (20)
num_classes = 4;                % кількість класів (τ, x, Z, X)

P = zeros(256, num_images);     % матриця вхідних векторів (256 = 16x16)
T = zeros(num_classes, num_images); % матриця цільових векторів

for i = 1:num_images
    % Зчитати зображення з папки Neuro_Train
    img = imread(fullfile('Neuro_Train', [files{2}{i}, '.bmp']));
    
    % Перетворити у відтінки сірого якщо потрібно
    if size(img, 3) == 3
        img = rgb2gray(img);
    end
    
    % Нормалізувати та записати у стовпець матриці P
    P(:, i) = im2double(img(:));
    
    % Заповнити цільовий вектор (one-hot encoding)
    T(files{1}(i), i) = 1;
end

fprintf('Матриці P (%dx%d) та T (%dx%d) сформовано успішно.\n', ...
    size(P,1), size(P,2), size(T,1), size(T,2));
