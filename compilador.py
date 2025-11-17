import sys
import os
import re



# dicionário de palavras reservadas 
RESERVED_WORDS = {
    'INTEGER': 'PRS01', 'REAL': 'PRS02', 'CHARACTER': 'PRS03', 'STRING': 'PRS04',
    'BOOLEAN': 'PRS05', 'VOID': 'PRS06', 'TRUE': 'PRS07', 'FALSE': 'PRS08',
    'VARTYPE': 'PRS09', 'FUNCTYPE': 'PRS10', 'PARAMTYPE': 'PRS11',
    'DECLARATIONS': 'PRS12', 'ENDDECLARATIONS': 'PRS13', 'PROGRAM': 'PRS14',
    'ENDPROGRAM': 'PRS15', 'FUNCTIONS': 'PRS16', 'ENDFUNCTIONS': 'PRS17',
    'ENDFUNCTION': 'PRS18', 'RETURN': 'PRS19', 'IF': 'PRS20', 'ELSE': 'PRS21',
    'ENDIF': 'PRS22', 'WHILE': 'PRS23', 'ENDWHILE': 'PRS24', 'BREAK': 'PRS25',
    'PRINT': 'PRS26'
}

# dicionario de simbolos reservados
RESERVED_SYMBOLS = {
    ':=': 'SRS04', '==': 'SRS17', '!=': 'SRS18', '<=': 'SRS20', '>=': 'SRS22',
    '#': 'SRS18',  
    ';': 'SRS01', ',': 'SRS02', ':': 'SRS03', '?': 'SRS05', '(': 'SRS06',
    ')': 'SRS07', '[': 'SRS08', ']': 'SRS09', '{': 'SRS10', '}': 'SRS11',
    '+': 'SRS12', '-': 'SRS13', '*': 'SRS14', '/': 'SRS15', '%': 'SRS16',
    '<': 'SRS19', '>': 'SRS21'
}


SORTED_SYMBOLS = sorted(RESERVED_SYMBOLS.keys(), key=len, reverse=True)


TRUNC_LIMIT = 32


LETRA = r'[a-zA-Z]'

DIGITO = r'[0-9]'

DIGITOS_DECIMAL = f'({DIGITO}+)'

# <variable> 
# (<letra> | _) ( <letra> | <digito> | _ )*
IDENTIFIER_PATTERN = re.compile(f'^({LETRA}|_)({LETRA}|{DIGITO}|_)*')

# <programName> e <functionName> 
# <letra> ( <letra> | <digito> )*
PROGRAM_FUNC_PATTERN = re.compile(f'^({LETRA})({LETRA}|{DIGITO})*')

# <intConst> 
INT_CONST_PATTERN = re.compile(f'^{DIGITOS_DECIMAL}')

# <realConst> 
PARTE_EXPONENCIAL = f'([Ee][+-]?{DIGITOS_DECIMAL})'
REAL_CONST_PATTERN = re.compile(fr'^{DIGITOS_DECIMAL}\.{DIGITOS_DECIMAL}({PARTE_EXPONENCIAL})?')

# isso deixa colocar coisas entre aspas menos outras aspas duplas
STRING_CONST_PATTERN = re.compile(r'^"([^"]*)"')

CHAR_CONST_PATTERN = re.compile(f"^'({LETRA})'")

class StaticChecker:
    def __init__(self, base_filename):
        #ta configurando os nomes dos arquivos para ficar como pediu nas orientações
        self.base_filename = os.path.normpath(base_filename)
        self.source_filename = f"{self.base_filename}.252"
        self.lex_filename = f"{self.base_filename}.LEX"
        self.tab_filename = f"{self.base_filename}.TAB"
        
        self.source_code = ""
        self.tokens = []  # armazena os tokens
        self.symbol_table = []  #tabela de Símbolos
        self.symbol_map = {}  
        
        self.line_number = 1
        self.pos = 0  

    def run(self):
        """ Executa o processo principal de análise. """
        print(f"Iniciando análise do arquivo: {self.source_filename}")
        
        if not self.read_source_file():
            return
         
        self.run_lexer()
        

        self.write_lex_report()
        self.write_tab_report()
        
        print(f"Análise concluída. Relatórios gerados:")
        print(f" -> {self.lex_filename}")
        print(f" -> {self.tab_filename}")

    def read_source_file(self):
        """ Lê o arquivo fonte .252. """
        try:
            
            with open(self.source_filename, 'r', encoding='utf-8') as f:
                #tratando coisas como insensibilidade da letra
                self.source_code = f.read().upper()
            return True
        except FileNotFoundError:
            print(f"Erro: Arquivo fonte '{self.source_filename}' não encontrado.")
            return False
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            return False

    def run_lexer(self):
        """ Itera sobre o código fonte e gera a lista de tokens. """
        while self.pos < len(self.source_code):
            char = self.source_code[self.pos]

            #ignorando espaços em branco
            if char in (' ', '\t', '\r'):
                self.pos += 1
                continue
            if char == '\n':
                self.line_number += 1
                self.pos += 1
                continue

            #delemitadores sendo tratados
            if char == '/' and self.pos + 1 < len(self.source_code):
                next_char = self.source_code[self.pos + 1]
                if next_char == '*':
                    self.handle_block_comment()
                    continue
                if next_char == '/':
                    self.handle_line_comment()
                    continue
            
            #trata os simbolos
            if self.handle_symbol():
                continue
                
            #trata identificadore e palavras reservadas, coisas que começam com letra ou _
            if char.isalpha() or char == '_':
                self.handle_identifier_or_keyword()
                continue
                
            #trata os numeros
            if char.isdigit():
                self.handle_number()
                continue

            # trata strings e char
            if char == '"':
                self.handle_string()
                continue
            if char == "'":
                self.handle_char()
                continue
                
            
            self.pos += 1

    # --- MÉTODOS DE TRATAMENTO DE ÁTOMOS ---
    #função para comentarios em blocos
    def handle_block_comment(self):
        """ Processa e ignora um comentário de bloco (/* ... */). """
        
        self.pos += 2
        while self.pos + 1 < len(self.source_code):
            if self.source_code[self.pos] == '*' and self.source_code[self.pos + 1] == '/':
                self.pos += 2  
                return
            if self.source_code[self.pos] == '\n':
                self.line_number += 1
            self.pos += 1
        
        self.pos = len(self.source_code)

    #função para comentarios de linha
    def handle_line_comment(self):
        """ Processa e ignora um comentário de linha (// ...). """
        
        self.pos += 2
        while self.pos < len(self.source_code):
            char = self.source_code[self.pos]
            if char == '\n':
                return
            self.pos += 1
    
        self.pos = len(self.source_code)
        
    def handle_symbol(self):
        """ Identifica o próximo símbolo reservado. """
        
        for symbol in SORTED_SYMBOLS:
            if self.source_code.startswith(symbol, self.pos):
                code = RESERVED_SYMBOLS[symbol]
                self.add_token(symbol, code, self.line_number)
                self.pos += len(symbol)
                return True
        return False

    def handle_identifier_or_keyword(self):
        """ Identifica um identificador ou palavra reservada. """
        substring = self.source_code[self.pos:]
        match = IDENTIFIER_PATTERN.match(substring)
        
        if not match:
            self.pos += 1
            return
            
        full_lexeme = match.group(0)
        self.pos += len(full_lexeme)
        
        truncated_lexeme = full_lexeme[:TRUNC_LIMIT]
        
        if truncated_lexeme in RESERVED_WORDS:
            code = RESERVED_WORDS[truncated_lexeme]
            self.add_token(truncated_lexeme, code, self.line_number)
        else:

            code = 'IDN02' 
            
            tab_index = self.add_to_symbol_table(truncated_lexeme, code, full_lexeme)
            self.add_token(truncated_lexeme, code, self.line_number, tab_index)

    def handle_number(self):
        """ Identifica um intConst (IDN04) ou realConst (IDN05). """
        substring = self.source_code[self.pos:]
        

        match_real = REAL_CONST_PATTERN.match(substring)
        if match_real:
            full_lexeme = match_real.group(0)
            self.pos += len(full_lexeme)
            truncated_lexeme = full_lexeme[:TRUNC_LIMIT]
            
            code = 'IDN05'  
            tab_index = self.add_to_symbol_table(truncated_lexeme, code, full_lexeme)
            self.add_token(truncated_lexeme, code, self.line_number, tab_index)
            return

        match_int = INT_CONST_PATTERN.match(substring)
        if match_int:
            full_lexeme = match_int.group(0)
            self.pos += len(full_lexeme)
            truncated_lexeme = full_lexeme[:TRUNC_LIMIT]

            code = 'IDN04'  # intConst
            tab_index = self.add_to_symbol_table(truncated_lexeme, code, full_lexeme)
            self.add_token(truncated_lexeme, code, self.line_number, tab_index)
            return
            
        if substring[0].isdigit():
             self.pos += 1 

    def handle_string(self):
        """ Identifica uma stringConst (IDN06). """
        substring = self.source_code[self.pos:]
        match = STRING_CONST_PATTERN.match(substring)
        
        if match:
            full_lexeme = match.group(0)
            self.pos += len(full_lexeme)
            
            if len(full_lexeme) > TRUNC_LIMIT:
                truncated_lexeme = full_lexeme[:TRUNC_LIMIT - 1] + '"'
            else:
                truncated_lexeme = full_lexeme
            
            code = 'IDN06'  
            tab_index = self.add_to_symbol_table(truncated_lexeme, code, full_lexeme)
            self.add_token(truncated_lexeme, code, self.line_number, tab_index)
        else:
           
            self.pos += 1
                
    def handle_char(self):
        """ Identifica uma charConst (IDN07). """
        substring = self.source_code[self.pos:]
        match = CHAR_CONST_PATTERN.match(substring)
        
        if match:
            full_lexeme = match.group(0)
            self.pos += len(full_lexeme)
            
            
            code = 'IDN07'  # charConst
            tab_index = self.add_to_symbol_table(full_lexeme, code, full_lexeme)
            self.add_token(full_lexeme, code, self.line_number, tab_index)
        else:
            
            self.pos += 1

    # --- MÉTODOS DE RELATÓRIO E TABELA DE SÍMBOLOS ---

    def add_token(self, lexeme, code, line, tab_index=None):
        """ Adiciona um token à lista de tokens encontrados. """
        self.tokens.append({
            'lexeme': lexeme,
            'code': code,
            'line': line,
            'tab_index': tab_index  
        })

    def add_to_symbol_table(self, truncated_lexeme, code, full_lexeme):
        """ 
        Adiciona um identificador à tabela de símbolos.
        Se já existe, apenas atualiza a linha.
        Retorna o índice 1-based da entrada.
        """
       
        if truncated_lexeme in self.symbol_map:
            idx_0 = self.symbol_map[truncated_lexeme] 
            
           
            entry = self.symbol_table[idx_0]
            if (self.line_number not in entry['lines']) and (len(entry['lines']) < 5):
                entry['lines'].append(self.line_number)
            
           
            if len(full_lexeme) > entry['qtd_antes_trunc']:
                entry['qtd_antes_trunc'] = len(full_lexeme)
                
            return idx_0 + 1 

        # É um novo símbolo
        new_entry = {
            'code': code,
            'lexeme': truncated_lexeme,
            'qtd_antes_trunc': len(full_lexeme),
            'qtd_depois_trunc': len(truncated_lexeme),
            'tipo': '',  
            'lines': [self.line_number] 
        }
        
        self.symbol_table.append(new_entry)
        new_index_0 = len(self.symbol_table) - 1
        self.symbol_map[truncated_lexeme] = new_index_0
        return new_index_0 + 1

    def write_lex_report(self):
        """ Escreve o arquivo .LEX com base no exemplo[cite: 85]. """
        
        header = [
            "Código da Equipe: 99 (PREENCHER)",
            "Componentes:",
            "Guilherme Rodrigues; seu.email@aluno.senai.br; (71)9XXXX-XXXX (PREENCHER)",
            f"RELATÓRIO DA ANÁLISE LÉXICA. Texto fonte analisado: {self.source_filename}" 
        ]
        
        with open(self.lex_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(header))
            f.write('\n' + '-'*80 + '\n\n')
            
            for token in self.tokens:
                
                idx_str = str(token['tab_index']) if token['tab_index'] else ""
                
               
                f.write(f"Lexeme: {token['lexeme']},\n")
                f.write(f"Código: {token['code']}, ÍndiceTabSimb: {idx_str},\n")
                f.write(f"Linha: {token['line']}.\n\n")

    def write_tab_report(self):
        """ Escreve o arquivo .TAB com base no exemplo. """
        
        header = [
            "Código da Equipe: 99 (PREENCHER)",
            "Componentes:",
            "Guilherme Rodrigues; seu.email@aluno.senai.br; (71)9XXXX-XXXX (PREENCHER)",
            f"RELATÓRIO DA TABELA DE SÍMBOLOS. Texto fonte analisado: {self.source_filename}" 
        ]
        
        with open(self.tab_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(header))
            f.write('\n' + '-'*80 + '\n\n')

            for i, entry in enumerate(self.symbol_table):
                
                line_str = ", ".join(map(str, entry['lines']))
                
                f.write(f"Entrada: {i+1}, Codigo: {entry['code']}, Lexeme: {entry['lexeme']},\n")
                f.write(f"QtdCharAntesTrunc: {entry['qtd_antes_trunc']}, QtdCharDepoisTrunc: {entry['qtd_depois_trunc']},\n")
                f.write(f"TipoSimb: {entry['tipo']}, Linhas: ({line_str}).\n\n")


# =============================================================================
# EXECUÇÃO PRINCIPAL
# =============================================================================
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python compilador.py <nome_base_arquivo>")
        print("Exemplo: python compilador.py MeuTeste")
        sys.exit(1)
        
    base_name = sys.argv[1]
    
    if base_name.upper().endswith(".252"):
        base_name = base_name[:-4]
        
    absolute_base_name = os.path.abspath(base_name)
    
    checker = StaticChecker(absolute_base_name)
    checker.run()
