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

- acertar o padding da logo em relação à side bar
- refinar o threshold do freeze
- ajustar o threshold do audio, silence e clipping
