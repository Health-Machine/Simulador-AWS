import pandas as pd
from datetime import datetime
import json

# Caminho do CSV
caminho_csv = 'sensor_pressao.csv'

# Ler o CSV
df = pd.read_csv(caminho_csv)

# Converter a data para o formato desejado
df['data_captura'] = pd.to_datetime(df['data_captura'])
df['data_captura'] = df['data_captura'].dt.strftime('%d/%m/%Y %H:%M')

# Converter para lista de dicionários
dados_json = df.to_dict(orient='records')

# Salvar como JSON
with open('sensor_5.json', 'w', encoding='utf-8') as f:
    json.dump(dados_json, f, ensure_ascii=False, indent=2)

print("Arquivo JSON gerado com sucesso!")
