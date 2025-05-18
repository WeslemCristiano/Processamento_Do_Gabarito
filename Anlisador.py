import cv2
import numpy as np
import os

# --- Parâmetros ---
imagem_path = r"C:\Users\User\Downloads\img_anonimizado\01049301.jpg"
gabarito_path = r"C:\Users\User\Downloads\img_anonimizado\gabarito.txt"
NUM_COLUNAS = 3
QUESTOES_POR_COLUNA = 20
OPCOES = 5
THRESHOLD_MARCACAO = 30
ALTURA_INICIAL = 70
largura, altura = 600, 800
modo_debug = True

# Carregar gabarito 
with open(gabarito_path, "r", encoding="utf-8") as f:
    gabarito_correto = [resposta.strip().lower() for resposta in f.read().splitlines()]
if len(gabarito_correto) != 60:
    raise ValueError("O gabarito deve conter exatamente 60 respostas.")

# Carregar imagem
img = cv2.imread(imagem_path)
if img is None:
    raise FileNotFoundError(f"Imagem não encontrada: {imagem_path}")

# Detectar triângulos (marcadores)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blur, 50, 150)
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

triangles = []
for cnt in contours:
    approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
    if len(approx) == 3 and cv2.contourArea(cnt) > 150:
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            triangles.append((cx, cy))

# Filtrar triângulos pela área útil 
altura_img = img.shape[0]
triangles = [p for p in triangles if p[1] > altura_img * 0.25]  

if len(triangles) < 4:
    raise ValueError(f"Apenas {len(triangles)} triângulos encontrados. Esperado: 4.")

# Visualizar triângulos detectados (debug)
img_debug = img.copy()
for cx, cy in triangles:
    cv2.circle(img_debug, (cx, cy), 10, (0, 0, 255), -1)
cv2.imwrite("triangulos_detectados.png", img_debug)

# Ordenar corretamente os pontos dos triângulos
def ordenar_pontos_triangulos(pontos):
    pontos = np.array(pontos, dtype="float32")
    soma = pontos.sum(axis=1)
    diff = np.diff(pontos, axis=1).flatten()

    ordenados = np.zeros((4, 2), dtype="float32")
    ordenados[0] = pontos[np.argmin(soma)]      # Topo esquerdo
    ordenados[1] = pontos[np.argmin(diff)]      # Topo direito
    ordenados[2] = pontos[np.argmax(soma)]      # Baixo direito
    ordenados[3] = pontos[np.argmax(diff)]      # Baixo esquerdo
    return ordenados

pts_src = ordenar_pontos_triangulos(triangles)
pts_dst = np.array([[0, 0], [largura, 0], [largura, altura], [0, altura]], dtype=np.float32)

# Corrigir perspectiva
matrix = cv2.getPerspectiveTransform(pts_src, pts_dst)
warped = cv2.warpPerspective(img, matrix, (largura, altura))

# Aplicar máscara branca fora do cartão
mask_cartao = np.zeros((altura, largura), dtype=np.uint8)
cv2.fillConvexPoly(mask_cartao, pts_dst.astype(np.int32), 255)
warped_masked = warped.copy()
warped_masked[mask_cartao == 0] = 255  # Preenche fora com branco

# Separar colunas 
col_width = largura // NUM_COLUNAS
columns = [warped_masked[:, i * col_width:(i + 1) * col_width] for i in range(NUM_COLUNAS)]
columns = [col[ALTURA_INICIAL:-85, :] for col in columns]

# Debugar as 3 colunas
if modo_debug:
    os.makedirs("debug_colunas", exist_ok=True)
    for i, col in enumerate(columns):
        cv2.imwrite(f"debug_colunas/coluna_{i + 1}.png", col)

# Detecção das caixas
def detectar_caixas_por_contorno(linha_binaria):
    contornos, _ = cv2.findContours(linha_binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    caixas_detectadas = []
    for cnt in contornos:
        x, y, w, h = cv2.boundingRect(cnt)
        aspecto = w / h if h != 0 else 0
        area = cv2.contourArea(cnt)
        if 8 < w < 50 and 8 < h < 50 and 0.6 < aspecto < 1.4 and area > 30:
            caixas_detectadas.append((x, y, w, h))
    return sorted(caixas_detectadas, key=lambda c: c[0])

# Analisar linha de questão
def analisar_linha(linha_binaria, linha_colorida, numero_questao):
    caixas = detectar_caixas_por_contorno(linha_binaria)
    resultados = {}
    letras = ['A', 'B', 'C', 'D', 'E']

    for i, (x, y, w, h) in enumerate(caixas[:5]):
        regiao = linha_binaria[y:y + h, x:x + w]
        brancos = np.count_nonzero(regiao == 255)
        letra = letras[i]
        resultados[letra] = brancos

        if modo_debug:
            cv2.rectangle(linha_colorida, (x, y), (x + w, y + h), (0, 255, 0), 1)
            cv2.putText(linha_colorida, letra, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    if modo_debug:
        os.makedirs("debug_linhas", exist_ok=True)
        cv2.imwrite(f"debug_linhas/q{numero_questao:02d}.png", linha_colorida)

    if not resultados:
        return '?', resultados

    marcada = max(resultados.items(), key=lambda x: x[1])
    return (marcada[0], resultados) if marcada[1] >= THRESHOLD_MARCACAO else ('?', resultados)

# Processar todas as questões 
respostas = []
relatorio = []
corretas = 0
numero_questao = 1

for col_idx, col in enumerate(columns):
    question_height = col.shape[0] // QUESTOES_POR_COLUNA
    for i in range(QUESTOES_POR_COLUNA):
        y1 = i * question_height
        y2 = (i + 1) * question_height
        linha = col[y1:y2, :]
        linha_gray = cv2.cvtColor(linha, cv2.COLOR_BGR2GRAY)
        _, linha_bin = cv2.threshold(linha_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        marcada, marcacoes = analisar_linha(linha_bin, linha.copy(), numero_questao)
        correta = gabarito_correto[numero_questao - 1].upper()
        acertou = marcada == correta
        simbolo = "✓" if acertou else "✘"

        if acertou:
            corretas += 1

        respostas.append(f"{numero_questao}-{marcada}")
        relatorio.append(f"{numero_questao:02d}. Marcada: {marcada} | Correta: {correta} {simbolo}")
        print(f"Questão {numero_questao:02d}: Marcada = {marcada}, Correta = {correta}, Pixels = {marcacoes}")
        numero_questao += 1

# Salvar resultados
with open("respostas.txt", "w", encoding="utf-8") as f:
    f.write("Respostas detectadas:\n")
    f.write(", ".join(respostas) + "\n\n")
    f.write("Relatório detalhado:\n")
    f.write("\n".join(relatorio) + "\n")
    f.write(f"\nTotal de acertos: {corretas}/60\n")
    f.write(f"Aproveitamento: {corretas / 60 * 100:.2f}%\n")

# Salvar imagem limpa e corrigida
cv2.imwrite("cartao_corrigido_limpo.png", warped_masked)

print("✅ Correção finalizada. Verifique: 'respostas.txt', 'cartao_corrigido_limpo.png' e 'triangulos_detectados.png'.")
