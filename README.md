#### **TÓPICOS IMPORTANTES SOBRE O CÓDIGO**

### **Quando for rodar a aplicação no linux faz:**

1. Criar o ambiente isolado:

```python
pip install -r requirements.txt
```

2. Criar o Banco de Dados local:

```python
python -m src.database.database_setup
```

3. Rodar a aplicação:

```python
python -m main
```

### Precisa ser implementado:

- adicionar o tipo de identificação LYP-SYNC no modelo de detecção
- adicionar o tipo de identificação AUDIO no modelo de detecção
- adicionar a paginção na tabela
- acertar o padding da logo em relação à side bar
- refinar o threshold do freeze
- Lógica para gerar o relatório
