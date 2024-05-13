% Listar arquivos
arquivos = dir(silencio.csv'); %captura de silencio
arquivos(2) = dir(evento.csv'); % captura de evento de interesse

% Inicializando uma estrutura para armazenar os dados complexos e os nomes dos arquivos
dadosArquivosTodos = struct;

% Loop através de cada arquivo CSV
for i = 1:length(arquivos)
    % Ler o arquivo CSV atual
    data = readtable(arquivos(i).name);

    % Pegar a última coluna (supondo que é a coluna 'data')
    csiCol = data.data;

    % Inicializando arrays para armazenar os números complexos, amplitude e fase para este arquivo
    complexData = zeros(height(data), 51);
    amplitudeData = zeros(height(data), 51);
    %faseData = zeros(height(data), 51);

    % Loop através de cada linha da tabela
    for j = 1:height(data)
        % Extrair e converter os valores CSI
        csiRaw = csiCol{j};

        % Converter a string para um vetor numérico, se necessário
        if iscell(csiRaw) || ischar(csiRaw)
            csiRaw = str2num(csiRaw);
        end

        % Remover os primeiros 2 números (primeira portadora)
        csiRaw = csiRaw(3:end);

        % Converter em números complexos (51 pares)
        for k = 1:51
            numComplexo = complex(csiRaw(k * 2 - 1), csiRaw(k * 2));
            complexData(j, k) = numComplexo;
            amplitudeData(j, k) = abs(numComplexo);
            %faseData(j, k) = angle(numComplexo);
        end
    end

    % Armazenar os dados complexos, amplitude, fase e o nome do arquivo na estrutura
    dadosArquivosTodos(i).nomeArquivo = arquivos(i).name;
    dadosArquivosTodos(i).dados = complexData;
    dadosArquivosTodos(i).amplitude = amplitudeData;
    %dadosArquivosTodos(i).fase = faseData;
end

% Preparação dos dados
% Selecionar os dados de amplitude dos arquivos de silêncio e conexão
amplitudeSilencio = dadosArquivosTodos(1).amplitude; % Substitua pelo índice correto
amplitudeConexao = dadosArquivosTodos(2).amplitude; % Substitua pelo índice correto

% Combinar os dados em um único conjunto
dadosCombinados = [amplitudeSilencio; amplitudeConexao];

% Aplicar o algoritmo LOF
K = 110; % Número de vizinhos para o LOF
modeloLOF = lof(dadosCombinados, 'NumNeighbors', K);

% Identificar anomalias usando o modelo LOF
[isanom, scores] = isanomaly(modeloLOF, dadosCombinados);

% Separar os scores para a parte de conexão
scoresConexao = scores(size(amplitudeSilencio, 1) + 1:end);

% Calcular média e desvio padrão dos scores de conexão
mediaScores = mean(scoresConexao);
desvioPadrao = (3*std(scoresConexao));

% Definir um limiar manual para identificar outliers
limiar = (mediaScores + desvioPadrao); % Ajuste este valor conforme necessário
outliersConexao = scoresConexao > limiar;

% Inicializar um vetor para marcar outliers finais
outliersFinais = outliersConexao;

% Calcular a quantidade de outliers finais
quantidadeOutliersFinais = sum(outliersFinais);
disp(['Quantidade de outliers finais: ', num2str(quantidadeOutliersFinais)]);

% Plotar os scores de anomalia
figure;
p1 = plot(scoresConexao); % Score de Anomalia

% Plotar média e desvio padrão
pMedia = yline(mediaScores, '--', 'Color', 'b', 'LineWidth', 1.5);
pDesvioPositivo = yline(mediaScores + desvioPadrao, '--', 'Color', 'r', 'LineWidth', 1.5);

% Texto para média e desvio padrão
text(10, mediaScores * 1.05, ['Média: ' num2str(mediaScores, '%.2f')], 'Color', 'black', 'FontSize', 10, 'FontWeight', 'bold');
text(10, (mediaScores + desvioPadrao) * 1.05, ['Desvio Padrão: ' num2str(desvioPadrao, '%.2f')], 'Color', 'black', 'FontSize', 10, 'FontWeight', 'bold');

hold on;

% Verificar se existem outliers finais identificados
if any(outliersFinais)
    pOutliersFinais = plot(find(outliersFinais), scoresConexao(outliersFinais), 'ro'); % Outliers finais
    % Adicionar texto com a quantidade de outliers finais
    text(10, limiar * 1.5, ['Outliers finais: ' num2str(quantidadeOutliersFinais)], 'Color', 'black', 'FontSize', 10, 'FontWeight', 'bold');
    legend([p1, pOutliersFinais, pMedia, pDesvioPositivo], ...
           {'Score de Anomalia', 'Outlier de Conexão Final', 'Média', 'Desvio Padrão +'});
else
    legend([p1, pMedia, pDesvioPositivo], ...
           {'Score de Anomalia', 'Média', 'Desvio Padrão +'});
    disp('Nenhum outlier de conexão final identificado com o limiar atual.');
end

title('LOF Scores Amplitude - Tentativa de Conexão');
xlabel('Amostra');
ylabel('Score de Anomalia');