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
freq_normal_min = 55.0
freq_normal_max = 65.0
frequencia_minima = 38.0
frequencia_maxima = 72.0
osc_normal_amp = 5.0        # amplitude da oscilação em modo normal (~±5 -> 55-65)
osc_phase_amp = 1.5         # amplitude durante as fases de degradação/elevação (mais sutil)
recovery_hours = 6   

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
    # dias inteiros passados desde o início da simulação
    total_days = (current_time - inicio_simulacao).days
    phase = total_days % 4  # 0..3
    # fração do dia atual (0..1)
    seconds_into_day = (current_time - current_time.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    frac_day = seconds_into_day / 86400.0

    if phase == 0:
        # modo normal: baseline nominal com oscilação natural maior
        baseline = frequencia_nominal
        osc = random.uniform(-osc_normal_amp, osc_normal_amp)
        valor = baseline + osc

    elif phase == 1:
        # queda gradual ao longo do dia: baseline linear de 60 -> 38
        baseline = frequencia_nominal + (frequencia_minima - frequencia_nominal) * frac_day
        # oscilações sutis enquanto cai
        osc = random.uniform(-osc_phase_amp, osc_phase_amp)
        valor = baseline + osc
        # garantir que não suba acima do início da fase
        # (isso evita "pulos" bruscos)
        max_allowed = frequencia_nominal - 0.1  # pequeno buffer
        if valor > max_allowed:
            valor = max_allowed

    elif phase == 2:
        # recuperação rápida: primeiros recovery_hours do dia -> sobe linearmente de 38 -> 60
        hour_of_day = seconds_into_day / 3600.0
        if hour_of_day <= recovery_hours:
            progresso = hour_of_day / recovery_hours  # 0..1 ao longo da recuperação rápida
            baseline = frequencia_minima + (frequencia_nominal - frequencia_minima) * progresso
            osc = random.uniform(-osc_phase_amp, osc_phase_amp)
            valor = baseline + osc
        else:
            # depois da recuperação, fica normal (osc normal)
            baseline = frequencia_nominal
            osc = random.uniform(-osc_normal_amp, osc_normal_amp)
            valor = baseline + osc

    else:  # phase == 3
        # subida gradual ao longo do dia: baseline linear de 60 -> 72
        baseline = frequencia_nominal + (frequencia_maxima - frequencia_nominal) * frac_day
        # oscilações sutis enquanto sobe
        osc = random.uniform(-osc_phase_amp, osc_phase_amp)
        valor = baseline + osc
        # garantir que não caia abaixo do início da fase
        min_allowed = frequencia_nominal + 0.1
        if valor < min_allowed:
            valor = min_allowed

    # segurança: limitar para não sair de limites plausíveis
    valor = max( round(valor, 2), 28.0 )   # piso de segurança
    valor = min( valor, 78.0 )             # teto de segurança

    return valor


# Exemplo de uso:
simular_dados(meses=1, intervalo_minutos=1)
