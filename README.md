#### **TÓPICOS IMPORTANTES SOBRE O CÓDIGO**

### **Arquivos que devem ser apagados:**

    - [X]exportar_dados.py

    - [X]dados_exportados.txt

    - [X]populate_database.py

### **Quando for rodar a aplicação faz:**

1. Criar o ambiente isolado:
``` python

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2. Rodar a aplicação:
``` python
python3 -m interface.main
```

3. Desativar o ambiente isolado:
``` python
deactivate
```
### **Precisa ser implementado:**

## 1. [] A logica para que a IA consiga atualizar os tipos de ocorrencias e elas aparecerem nas abas de ocorrencia 
**_AJUDA DO CHAT:_**
{Ah, agora entendi perfeitamente! O que você quer é que a aplicação não use mais um `tipo` fixo como `"Automático"`, mas sim que **o tipo da ocorrência seja definido dinamicamente pela IA** e que essa informação apareça na aba “Ocorrências”.

Vamos analisar o fluxo:

---

### 1️⃣ Onde isso precisa mudar

No seu `main.py` você tem:

```python
# Valores padrão iniciais (podem ser alterados conforme login no futuro)
tipo = "Automático"
gravidade = "leve"
origem = "Rede"
usuario_id = 1  # ID do usuário padrão (ex: operador logado)
```

E depois:

```python
criar_ocorrencia(
    tipo=tipo,
    descricao=f"Falha detectada no arquivo {nome_arquivo}",
    gravidade=gravidade,
    origem=origem,
    data=data_ocorrencia_arquivo.split(" ")[0],
    hora=data_ocorrencia_arquivo.split(" ")[1],
    duracao=tempo_video,
    usuario_id=usuario_id
)
```

Atualmente, **`tipo` nunca muda**, mesmo que sua IA detecte o tipo real do arquivo.

---

### 2️⃣ Como modificar

Você precisa que a função que identifica a ocorrência pela IA **retorne o tipo correto**. Por exemplo:

```python
def identificar_tipo_ia(arquivo_path):
    # Aqui você coloca a lógica da IA
    # Exemplo fictício:
    if arquivo_path.endswith(".mp4"):
        return "vídeo"
    elif arquivo_path.endswith(".jpg"):
        return "logo"
    else:
        return "automação"  # default
```

Então, no fluxo de upload, você substitui:

```python
tipo = identificar_tipo_ia(filepath)
```

Agora o `tipo` refletirá o que a IA detectou.

---

### 3️⃣ Garantir que apareça na aba “Ocorrências”

1. No `criar_ocorrencia()` você salva o `tipo` correto no banco.
2. Na função `listar_ocorrencias()` você já retorna o `tipo`.
3. No `main.py` a tabela é preenchida usando `ocorrencias_data`, que agora terá o tipo correto.

Se tudo estiver correto, **a tabela exibirá o tipo detectado pela IA imediatamente**.

---

Se quiser, posso te enviar **uma versão pronta do fluxo de upload + detecção IA** no `main.py`, já integrando o tipo dinâmico, duração e preenchimento da aba de ocorrências.

Quer que eu faça isso?*}

## 2. []Lógica para gerar o relatório
**_AJUDA DO CHAT:_**
{Perfeito! Vamos criar uma função completa que gera relatórios automaticamente a partir das ocorrências existentes no banco de dados. Ela vai:

1. Receber um **período** (data inicial e final) e o **ID do usuário** que está gerando o relatório.
2. Contar todas as ocorrências nesse período, separando por gravidade.
3. Inserir automaticamente um registro na tabela `relatorios`.
4. Retornar os valores para poder exibir na interface.

Segue o código que você pode adicionar no seu `db_functions.py`:

```python
from datetime import datetime

def gerar_relatorio(data_inicio: str, data_fim: str, usuario_id: int):
    """
    Gera um relatório automático com base nas ocorrências existentes
    entre data_inicio e data_fim.
    
    Args:
        data_inicio (str): Data inicial no formato 'YYYY-MM-DD'
        data_fim (str): Data final no formato 'YYYY-MM-DD'
        usuario_id (int): ID do usuário que gera o relatório
    
    Returns:
        dict: Totais calculados {'total_falhas', 'total_gravissimas', 'total_leves'}
    """
    conn = connect()
    cursor = conn.cursor()
    
    # Conta todas as ocorrências no período
    cursor.execute("""
        SELECT gravidade, COUNT(*)
        FROM ocorrencias
        WHERE data BETWEEN ? AND ?
        GROUP BY gravidade
    """, (data_inicio, data_fim))
    
    resultados = cursor.fetchall()
    
    # Inicializa contadores
    total_falhas = 0
    total_gravissimas = 0
    total_leves = 0
    
    # Processa os resultados
    for gravidade, count in resultados:
        total_falhas += count
        if gravidade == 'gravíssima':
            total_gravissimas += count
        elif gravidade == 'leve':
            total_leves += count
    
    # Cria o relatório no banco
    periodo_str = f"{data_inicio} a {data_fim}"
    cursor.execute("""
        INSERT INTO relatorios (periodo, total_falhas, total_gravissimas, total_leves, gerado_por)
        VALUES (?, ?, ?, ?, ?)
    """, (periodo_str, total_falhas, total_gravissimas, total_leves, usuario_id))
    
    conn.commit()
    conn.close()
    
    return {
        'total_falhas': total_falhas,
        'total_gravissimas': total_gravissimas,
        'total_leves': total_leves,
        'periodo': periodo_str
    }
```

---

### ✅ Como usar no `main.py`:

```python
from database.db_functions import gerar_relatorio

# Exemplo de geração para a semana atual
relatorio = gerar_relatorio("2025-11-01", "2025-11-04", usuario_id=1)
print(f"Relatório gerado: {relatorio}")
```

Isso já permite:

* Gerar relatórios automáticos sem precisar passar manualmente os totais.
* Integrar direto com a aba “Relatórios” da sua aplicação.

---

Se quiser, posso também escrever **uma função no `main.py` que atualiza a aba “Relatórios” automaticamente**, listando todos os relatórios já gerados e permitindo gerar novos com um botão “Gerar Relatório”.

Quer que eu faça isso?
}


