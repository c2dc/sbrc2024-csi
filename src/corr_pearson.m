% Listar todos os arquivos CSV
arquivos = dir('*.csv'); %filtrar pelos nomes de arquivos que deseja processar

% Estrutura para armazenar os dados complexos e os nomes dos arquivos
dadosArquivosTodos = struct;

% Loop através de cada arquivo CSV
for i = 1:length(arquivos)
    % Ler o arquivo CSV atual
    data = readtable(arquivos(i).name);

    % Pegar coluna data
    csiCol = data.data;

    % Inicializando arrays para armazenar os números complexos e amplitude para este arquivo
    complexData = zeros(height(data), 51);
    amplitudeData = zeros(height(data), 51);
    
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
        end
    end

    % Armazenar os dados complexos, amplitude e o nome do arquivo na estrutura
    dadosArquivosTodos(i).nomeArquivo = arquivos(i).name;
    dadosArquivosTodos(i).dados = complexData;
    dadosArquivosTodos(i).amplitude = amplitudeData;    
end

% Preparação dos dados
% Selecionar os dados de amplitude
amplitudeCaptura1 = dadosArquivosTodos(2).amplitude; % Substituir pelo índice correto
amplitudeCaptura2 = dadosArquivosTodos(1).amplitude; % Substituir pelo índice correto

%Correlação de Pearson

% amplitudeData é a matriz de amplitude
FlatCap1 = amplitudeCaptura1(:); % Achatando a matriz de amplitude
FlatCap2 = amplitudeCaptura2(:); % Achatando a matriz de amplitude

% Igualar o tamanho dos vetores
if length(FlatCap2) > length(FlatCap1)
    FlatCap2 = FlatCap2(1:length(FlatCap1));
elseif length(FlatCap1) > length(FlatCap2)
    FlatCap1 = FlatCap1(1:length(FlatCap2));
end

% Calculando a correlação
coeficienteCorrelacao = corr(FlatCap2, FlatCap1);
disp(['Coeficiente de Correlação: ', num2str(coeficienteCorrelacao)]);

% Calculando a correlação cruzada
coeficienteCorrelacaoCruzada = xcorr(FlatCap2, FlatCap1);

% Encontrar o índice central para o lag 0
indiceCentral = ceil(length(coeficienteCorrelacaoCruzada) / 2);
correlacaoCruzadaLagZero = coeficienteCorrelacaoCruzada(indiceCentral);

% Exibindo o coeficiente de correlação cruzada para o lag 0
disp(['Coeficiente de Correlação Cruzada (Lag 0): ', num2str(correlacaoCruzadaLagZero)]);



