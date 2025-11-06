import json
import random
import datetime as dt
import requests

# Endpoint de destino
url = "https://g5xyw5okt6.execute-api.us-east-1.amazonaws.com/hml/raw-bucket-891377383993/sensor/captura_de_dados.json"

# Corrente
tensao_padrao = 2.5
sensibilidade = 0.066
corrente_nominal = 10.0
tensao_teorica = tensao_padrao + corrente_nominal * sensibilidade

# Tensão
vmax_in = 400
variacao_minima = 300
tensao_normal_base = 350
variacao_normal = 2.0
probabilidade_pico = 0.01

# Temperatura
temperatura_nominal = 25.0
variacao_maxima_temp = 0.8

# Vibração
velocidade_nominal = 6.0
variacao_permitida = 5.0
horario_parada_inicio = 12  # início da parada (12h)
horario_parada_fim = 16     # fim da parada (16h)

# Frequência
frequencia_nominal = 60.0
variacao_maxima_freq = 1.5
frequencia_minima = 38.0
frequencia_maxima = 72.0

# Pressão
pressao_nominal = 35.0
variacao_maxima_pressao = 2.5


def simular_dados(meses, intervalo_minutos):
    agora = dt.datetime.now()
    current_time = agora - dt.timedelta(days=30 * meses)
    dados = []

    while current_time <= agora:
        record = {
            'data_captura': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'sensor_1': calcular_corrente(),
            'sensor_2': calcular_tensao(),
            'sensor_3': calcular_temperatura(),
            'sensor_4': calcular_vibracao(current_time),
            'sensor_5': calcular_pressao(),
            'sensor_6': calcular_frequencia(current_time, agora)
        }

        dados.append(record)
        current_time += dt.timedelta(minutes=intervalo_minutos)

    print(f"📊 Total de registros gerados: {len(dados)}")

    # --- Envio ao endpoint ---
    try:
        r = requests.put(
            url,
            data=json.dumps(dados),
            headers={'Content-Type': 'application/json'}
        )
        print(f"🌐 Envio concluído! Status: {r.status_code}")
        print(f"📨 Resposta do servidor: {r.text[:200]}")
    except Exception as e:
        print(f"⚠️ Erro ao enviar dados: {e}")


def calcular_corrente():
    variacao = random.uniform(-0.5, 0.5)
    tensao_saida = tensao_teorica + variacao
    return round((tensao_saida - tensao_padrao) / sensibilidade, 3)


def calcular_tensao():
    limite_normal_inferior = tensao_normal_base - variacao_normal
    limite_normal_superior = tensao_normal_base + variacao_normal

    if random.random() < probabilidade_pico:
        if random.choice([True, False]):
            variacao = random.uniform(limite_normal_superior, vmax_in)
        else:
            variacao = random.uniform(variacao_minima, limite_normal_inferior)
    else:
        variacao = random.uniform(limite_normal_inferior, limite_normal_superior)

    return round(variacao, 2)


def calcular_temperatura():
    variacao = random.uniform(-variacao_maxima_temp, variacao_maxima_temp)
    return round(temperatura_nominal + variacao, 2)


def calcular_vibracao(current_time):
    hora = current_time.hour
    # 4h de parada diária
    if horario_parada_inicio <= hora < horario_parada_fim:
        return 0.0
    variacao = random.uniform(-variacao_permitida, variacao_permitida)
    return round(velocidade_nominal + variacao, 3)


def calcular_pressao():
    variacao = random.uniform(-variacao_maxima_pressao, variacao_maxima_pressao)
    return round(pressao_nominal + variacao, 2)


def calcular_frequencia(current_time, inicio_simulacao):
    """
    A frequência oscila naturalmente, mas a cada dia muda de comportamento:
    - Dia 1: normal (58–62)
    - Dia 2: começa a cair até 38
    - Dia 3: recupera até normal
    - Dia 4: sobe até 72
    - Dia 5: normaliza novamente
    """
    
    dias_passados = (current_time - inicio_simulacao).days % 4

    if dias_passados == 1:
        # Fase de queda
        progresso = (current_time.hour + current_time.minute / 60) / 24
        valor = frequencia_nominal - (frequencia_nominal - frequencia_minima) * progresso
    elif dias_passados == 2:
        # Fase de recuperação
        progresso = (current_time.hour + current_time.minute / 60) / 24
        valor = frequencia_minima + (frequencia_nominal - frequencia_minima) * progresso
    elif dias_passados == 3:
        # Fase de pico
        progresso = (current_time.hour + current_time.minute / 60) / 24
        valor = frequencia_nominal + (frequencia_maxima - frequencia_nominal) * progresso
    else:
        # Normal
        valor = random.uniform(frequencia_nominal - variacao_maxima_freq,
                               frequencia_nominal + variacao_maxima_freq)

    # Pequena oscilação natural
    valor += random.uniform(-0.5, 0.5)
    return round(valor, 2)


# Exemplo de uso:
simular_dados(meses=1, intervalo_minutos=1)
