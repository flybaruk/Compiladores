# Projeto de Compiladores - Analisador Léxico

Este repositório contém a implementação da primeira etapa de um compilador (Analisador Léxico / Static Checker) para a linguagem especificada na disciplina de **Compiladores**, ministrada pelo **Professor Osvaldo Requião Melo**.

O projeto foi desenvolvido em **Python 3.10** e realiza a leitura de arquivos fonte com extensão `.252`, gerando relatórios de tokens e tabela de símbolos.

## Funcionalidades

O analisador realiza as seguintes tarefas:
1.  **Filtro de Primeiro Nível:** Remoção de espaços em branco, tabulações, quebras de linha e comentários (tanto de linha `//` quanto de bloco `/* ... */`).
2.  **Tokenização:** Reconhecimento de palavras reservadas, símbolos especiais, identificadores e constantes (inteiras, reais, char e string).
3.  **Tabela de Símbolos:** Gerenciamento de identificadores e constantes, com controle de escopo básico e registro de linhas de ocorrência.
4.  **Geração de Relatórios:**
    * Arquivo `.LEX`: Relatório contendo a sequência de tokens identificados.
    * Arquivo `.TAB`: Relatório do estado final da Tabela de Símbolos.

## Pré-requisitos

* Python 3.10 ou superior instalado.
* Não é necessário instalar bibliotecas externas (o projeto utiliza apenas bibliotecas padrão: `sys`, `os`, `re`).

## Como Rodar

1.  **Prepare o arquivo fonte:**
    Crie um arquivo com a extensão `.252` contendo o código que deseja analisar (por exemplo, `MeuTeste.252`) no mesmo diretório do script.

2.  **Execute o script via terminal:**
    Abra o terminal na pasta do projeto e execute o comando abaixo, passando o nome do arquivo (com ou sem a extensão):

    ```bash exemplo 1:
    python compilador.py MeuTeste
    ```

    *Ou:*

    ```bash exemplo 2:
    python compilador.py MeuTeste.252
    ```

3.  **Verifique os resultados:**
    Após a execução, o script gerará dois arquivos no mesmo diretório:
    * `MeuTeste.LEX`
    * `MeuTeste.TAB`

## Estrutura dos Arquivos Gerados

### Arquivo .LEX (Relatório de Tokens)
Lista todos os lexemas encontrados, seus códigos (ex: `PRS01`, `IDN02`), índice na tabela de símbolos (se aplicável) e a linha onde foram encontrados.

### Arquivo .TAB (Tabela de Símbolos)
Detalha os identificadores e constantes armazenados, incluindo:
* Lexema original e truncado (limite de 35 caracteres).
* Tipo do símbolo.
* Lista das primeiras 5 linhas onde o símbolo apareceu.

## Autores

* Arthur Ribeiro
* Bernado Resende
* Guilherme Rodrigues
* José Henrique
* Disciplina: Compiladores
* Professor: Osvaldo Requião Melo
