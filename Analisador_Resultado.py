import csv
import time
import tracemalloc

# Arquivos de entrada
respostas_csv = r"C:\Users\User\Documents\Computação Grafica\Processamento do gabarito\resposta.csv"
gabarito_csv = r"C:\Users\User\Downloads\gabarito.csv"

def limpar_nome_colunas(colunas):
    """Remove BOM e espaços em branco extras dos nomes de colunas."""
    return [col.strip().replace('\ufeff', '') for col in colunas]

def checar_colunas(arquivo, esperado):
    with open(arquivo, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        colunas_brutas = next(reader)
        colunas = limpar_nome_colunas(colunas_brutas)
        for col in esperado:
            if col not in colunas:
                print(f"⚠️ Atenção: coluna '{col}' não encontrada em {arquivo}. Colunas disponíveis: {colunas}")
                return False
    return True

# Verificar colunas dos arquivos
colunas_necessarias = ['id_prova', 'questao', 'resposta']
if not checar_colunas(respostas_csv, colunas_necessarias) or not checar_colunas(gabarito_csv, colunas_necessarias):
    print("Corrija os nomes das colunas nos arquivos CSV e tente novamente.")
    exit(1)

# --- Iniciar medições ---
tracemalloc.start()
inicio = time.time()

# --- Carregar respostas detectadas ---
respostas_detectadas = {}
with open(respostas_csv, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    reader.fieldnames = limpar_nome_colunas(reader.fieldnames)
    for row in reader:
        try:
            chave = (int(row['id_prova']), int(row['questao']))
            respostas_detectadas[chave] = row['resposta'].strip().upper()
        except KeyError as e:
            print(f"Erro: coluna ausente {e} na linha: {row}")
            continue

# --- Carregar gabarito oficial ---
gabarito_oficial = {}
with open(gabarito_csv, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    reader.fieldnames = limpar_nome_colunas(reader.fieldnames)
    for row in reader:
        try:
            chave = (int(row['id_prova']), int(row['questao']))
            gabarito_oficial[chave] = row['resposta'].strip().upper()
        except KeyError as e:
            print(f"Erro: coluna ausente {e} na linha: {row}")
            continue

# --- Comparar respostas ---
total = 0
acertos = 0
comparacoes_detalhadas = []

for chave, resposta_certa in gabarito_oficial.items():
    resposta_detectada = respostas_detectadas.get(chave)
    if resposta_detectada is None or resposta_detectada == '?':
        continue  # Ignorar não respondidas

    total += 1
    correta = resposta_certa == resposta_detectada
    if correta:
        acertos += 1

    comparacoes_detalhadas.append({
        'id_prova': chave[0],
        'questao': chave[1],
        'resposta_certa': resposta_certa,
        'resposta_detectada': resposta_detectada,
        'correta': '✓' if correta else '✘'
    })

# --- Métricas finais ---
fim = time.time()
mem_atual, mem_pico = tracemalloc.get_traced_memory()
tracemalloc.stop()

acuracia = (acertos / total) * 100 if total > 0 else 0.0

# --- Exibir resultados ---
print("\n📊 RESULTADOS DA COMPARAÇÃO")
print(f"Total de comparações válidas: {total}")
print(f"Total de acertos: {acertos}")
print(f"Acurácia: {acuracia:.2f}%")
print(f"⏱️ Tempo de execução: {fim - inicio:.2f} segundos")
print(f"📈 Pico de uso de memória: {mem_pico / 1024:.2f} KB")

# --- Salvar log detalhado ---
with open("log_comparacao.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=['id_prova', 'questao', 'resposta_certa', 'resposta_detectada', 'correta'], delimiter=';')
    writer.writeheader()
    writer.writerows(comparacoes_detalhadas)
