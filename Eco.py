import sqlite3
import re
from typing import Dict, Optional

DB_NAME = "ECO.db"

# Criar tabelas com relacionamentos

def criar_tabelas():
    """Cria as tabelas Titulares e Dependentes no banco de dados."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Tabela de Titulares
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Titulares (
            CPF TEXT PRIMARY KEY,
            Credencial TEXT UNIQUE NOT NULL,
            Nome TEXT NOT NULL,
            Sexo TEXT CHECK(Sexo IN ('M', 'F')),
            DtNascimento TEXT NOT NULL,
            Idade INTEGER,
            FaixaANS TEXT,
            EstadoCivil TEXT,
            TipoSuplementar TEXT,
            CEP TEXT,
            Bairro TEXT,
            Cidade TEXT,
            Estado TEXT,
            StatusSegurado TEXT DEFAULT 'Ativo',
            DataInicio TEXT,
            DataFim TEXT
        )
        """)
        
        # Tabela de Dependentes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Dependentes (
            CPF TEXT PRIMARY KEY,
            Credencial TEXT UNIQUE NOT NULL,
            Nome TEXT NOT NULL,
            Sexo TEXT CHECK(Sexo IN ('M', 'F')),
            DtNascimento TEXT NOT NULL,
            Idade INTEGER,
            FaixaANS TEXT,
            EstadoCivil TEXT,
            GrauParentesco TEXT NOT NULL,
            TipoSuplementar TEXT,
            CPFTitular TEXT NOT NULL,
            StatusSegurado TEXT DEFAULT 'Ativo',
            DataInicio TEXT,
            DataFim TEXT,
            FOREIGN KEY (CPFTitular) REFERENCES Titulares(CPF) ON DELETE CASCADE
        )
        """)
        
        conn.commit()
        print("Tabelas criadas com sucesso!")
    except sqlite3.Error as e:
        print(f"Erro ao criar tabelas: {e}")
    finally:
        conn.close()

# -------------------------
# Funções de validação
# -------------------------
def cpf_valido(cpf: str) -> bool:
    """Valida se um CPF tem 11 dígitos numéricos."""
    return bool(re.fullmatch(r"\d{11}", cpf))

# Operações com Titulares



def inserir_titular(dados: Dict[str, str]) -> None:
    """Insere um novo titular no banco de dados."""
    if not cpf_valido(dados['cpf']):
        print(f"CPF inválido: {dados['cpf']}")
        return
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO Titulares (
            CPF, Credencial, Nome, Sexo, DtNascimento, Idade, FaixaANS, EstadoCivil,
            TipoSuplementar, CEP, Bairro, Cidade, Estado, StatusSegurado, DataInicio, DataFim
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dados['cpf'], dados['credencial'], dados['nome'], dados['sexo'],
            dados['dt_nascimento'], dados['idade'], dados['faixa_ans'],
            dados['estado_civil'], dados['tipo_suplementar'], dados['cep'],
            dados['bairro'], dados['cidade'], dados['estado'], dados['status'],
            dados['data_inicio'], dados['data_fim']
        ))
        
        conn.commit()
        print(f"Titular '{dados['nome']}' inserido com sucesso!")
    except sqlite3.IntegrityError as e:
        print(f"Erro de integridade: {e}")
    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {e}")
    finally:
        conn.close()

# Operações com Dependentes

def inserir_dependente(dados: Dict[str, str]) -> None:
    """Insere um novo dependente no banco de dados."""
    if not cpf_valido(dados['cpf']):
        print(f"CPF inválido do dependente: {dados['cpf']}")
        return
        
    if not cpf_valido(dados['cpf_titular']):
        print(f"CPF inválido do titular: {dados['cpf_titular']}")
        return

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Verifica se titular existe
        cursor.execute("SELECT 1 FROM Titulares WHERE CPF = ?", (dados['cpf_titular'],))
        if not cursor.fetchone():
            print(f"Erro: Titular com CPF {dados['cpf_titular']} não encontrado.")
            return
        
        # Insere o dependente
        cursor.execute("""
        INSERT INTO Dependentes (
            CPF, Credencial, Nome, Sexo, DtNascimento, Idade, FaixaANS, EstadoCivil,
            GrauParentesco, TipoSuplementar, CPFTitular, StatusSegurado, DataInicio, DataFim
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dados['cpf'], dados['credencial'], dados['nome'], dados['sexo'],
            dados['dt_nascimento'], dados['idade'], dados['faixa_ans'],
            dados['estado_civil'], dados['grau_parentesco'], dados['tipo_suplementar'],
            dados['cpf_titular'], dados['status'], dados['data_inicio'], dados['data_fim']
        ))
        
        conn.commit()
        print(f"Dependente '{dados['nome']}' inserido com sucesso!")
    except sqlite3.IntegrityError as e:
        print(f"Erro de integridade: {e}")
    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {e}")
    finally:
        conn.close()

# Operações gerais
def remover_pessoa(cpf: str) -> None:
    """Remove uma pessoa (titular ou dependente) do banco de dados."""
    if not cpf_valido(cpf):
        print(f"CPF inválido: {cpf}")
        return
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Verifica se é titular
        cursor.execute("SELECT 1 FROM Titulares WHERE CPF = ?", (cpf,))
        if cursor.fetchone():
            cursor.execute("DELETE FROM Titulares WHERE CPF = ?", (cpf,))
            print(f"Titular com CPF {cpf} e seus dependentes foram removidos com sucesso!")
        else:
            # Se não for titular, tenta remover como dependente
            cursor.execute("DELETE FROM Dependentes WHERE CPF = ?", (cpf,))
            if cursor.rowcount > 0:
                print(f"Dependente com CPF {cpf} removido com sucesso!")
            else:
                print(f"Nenhuma pessoa encontrada com CPF {cpf}")
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao remover pessoa: {e}")
    finally:
        conn.close()

def listar_pessoas() -> None:
    """Lista todos os titulares e dependentes do banco de dados."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        print("\n=== Titulares ===")
        cursor.execute("""
        SELECT CPF, Nome, Sexo, Idade, Estado, StatusSegurado 
        FROM Titulares
        ORDER BY Nome
        """)
        
        for row in cursor.fetchall():
            print(f"CPF: {row[0]} | Nome: {row[1]} | Sexo: {row[2]} | Idade: {row[3]} | Estado: {row[4]} | Status: {row[5]}")
        
        print("\n=== Dependentes ===")
        cursor.execute("""
        SELECT d.CPF, d.Nome, d.Sexo, d.Idade, d.GrauParentesco, t.Nome as Titular, d.StatusSegurado 
        FROM Dependentes d
        JOIN Titulares t ON d.CPFTitular = t.CPF
        ORDER BY d.Nome
        """)
        
        for row in cursor.fetchall():
            print(f"CPF: {row[0]} | Nome: {row[1]} | Sexo: {row[2]} | Idade: {row[3]} | Parentesco: {row[4]} | Titular: {row[5]} | Status: {row[6]}")
            
    except sqlite3.Error as e:
        print(f"Erro ao listar pessoas: {e}")
    finally:
        conn.close()

# Testando as funcionalidades
if __name__ == "__main__":
    # Cria as tabelas
    criar_tabelas()

    # Dados do titular
    dados_titular = {
        'cpf': '12930888466',
        'credencial': 'CRED001',
        'nome': 'Julius Cesar',
        'sexo': 'M',
        'dt_nascimento': '2001-05-10',
        'idade': 24,
        'faixa_ans': 'Adulto',
        'estado_civil': 'Solteiro',
        'tipo_suplementar': 'Ouro',
        'cep': '12345678',
        'bairro': 'Timbi',
        'cidade': 'Camaragibe',
        'estado': 'PE',
        'status': 'Ativo',
        'data_inicio': '2025-01-01',
        'data_fim': None
    }
    
    inserir_titular(dados_titular)

    # Dados do dependente
    dados_dependente = {
        'cpf': '21223344556',
        'credencial': 'CRED002',
        'nome': 'Maria Silva',
        'sexo': 'F',
        'dt_nascimento': '2012-03-20',
        'idade': 13,
        'faixa_ans': 'Infantil',
        'estado_civil': 'Solteiro',
        'grau_parentesco': 'Prima',
        'tipo_suplementar': 'Ouro',
        'cpf_titular': '12930888466',  
        'status': 'Ativo',
        'data_inicio': '2025-01-01',
        'data_fim': None
    }
    
    # Insere o dependente
    inserir_dependente(dados_dependente)

    # Lista todas as pessoas
    listar_pessoas()

    # Remove o dependente
    remover_pessoa('21223344556')

    # Lista novamente para verificar
    listar_pessoas()

    # Remove o titular (deve remover automaticamente todos os dependentes restantes)
    remover_pessoa('12930888466')

    # Lista final
    listar_pessoas()



    