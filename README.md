# 📄 Correção Automática de Cartões de Resposta

* **Alunos:** Weslem, Giovanni, Luis
* **Professor:** Wellington Della Mura

**Projeto:** Leitor automático de cartões de múltipla escolha com detecção visual de marcações.
**Tecnologias:** Python, OpenCV, NumPy, CSV

---

## 🎯 Objetivo Geral

Desenvolver um sistema que leia imagens digitalizadas de cartões de resposta de múltipla escolha, detecte automaticamente as alternativas marcadas, compare com um gabarito e gere estatísticas de desempenho, com suporte a depuração visual.

---

## 🧠 Visão Geral do Funcionamento

O sistema realiza:

1. **Leitura e correção da imagem do cartão**
2. **Segmentação e detecção das alternativas marcadas**
3. **Geração de arquivos com as respostas detectadas**
4. **Comparação automática com um gabarito oficial**
5. **Cálculo de métricas como acurácia, tempo e memória**

---

## 🔍 1. Leitura e Pré-processamento da Imagem

### 📌 Técnicas:

* `cv2.imread()` – Carrega a imagem do cartão.
* `cv2.cvtColor()` – Conversão para escala de cinza.
* `cv2.GaussianBlur()` – Redução de ruído.
* `cv2.Canny()` – Detecção de bordas.

### 🎯 Objetivo:

Preparar a imagem para localizar os triângulos de marcação, melhorando a nitidez das bordas e a confiabilidade na detecção dos elementos gráficos.

---

## 📐 2. Detecção dos Triângulos de Referência

### 📌 Técnicas:

* `cv2.findContours()` – Encontra contornos.
* `cv2.approxPolyDP()` – Aproxima polígonos.
* `cv2.contourArea()` – Filtro por área.
* `cv2.moments()` – Cálculo do centro de massa.
* Filtro vertical – Ignora triângulos fora da área útil.

### 🎯 Objetivo:

Detectar os 4 triângulos posicionados nos cantos do cartão para corrigir a perspectiva e alinhar o conteúdo.

---

## 🔁 3. Ordenação dos Pontos

### 📌 Técnicas:

* Função `ordenar_pontos_triangulos()` baseada na **soma** e **diferença** das coordenadas (x + y, x - y).

### 🎯 Objetivo:

Garantir a ordem correta dos pontos: superior esquerdo, superior direito, inferior direito, inferior esquerdo, essencial para a homografia.

---

## 🔄 4. Correção de Perspectiva (Homografia)

### 📌 Técnicas:

* `cv2.getPerspectiveTransform()`
* `cv2.warpPerspective()`

### 🎯 Objetivo:

Remover distorções de perspectiva e alinhar o cartão em uma visualização plana para análise posterior.

---

## 🧼 5. Limpeza da Área Externa (Máscara)

### 📌 Técnicas:

* `cv2.fillConvexPoly()` – Criação da máscara do cartão.
* Substituição dos pixels externos por branco (`255`).

### 🎯 Objetivo:

Eliminar sombras, bordas e elementos fora do cartão para garantir que apenas o conteúdo útil seja processado.

---

## 📊 6. Segmentação do Cartão em Colunas e Linhas

### 📌 Técnicas:

* Divisão em 3 colunas fixas.
* Corte da parte superior e inferior irrelevante.
* Cálculo automático da altura de cada linha de questão.

### 🎯 Objetivo:

Isolar cada questão do cartão para que possa ser processada de forma independente.

---

## 🧾 7. Binarização

### 📌 Técnicas:

* `cv2.threshold()` com `cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU`

### 🎯 Objetivo:

Converter as marcações escuras em áreas brancas de alto contraste, facilitando a detecção das alternativas marcadas.

---

## ⬛ 8. Detecção das Alternativas por Contorno

### 📌 Técnicas:

* `cv2.findContours()`, `cv2.boundingRect()`
* Filtros por:

  * Tamanho (entre 8 e 50 pixels)
  * Aspect ratio (entre 0.6 e 1.4)
  * Área (> 30 pixels)

### 🎯 Objetivo:

Detectar dinamicamente as caixas das alternativas (A–E), sem depender de posições fixas, tornando o sistema flexível a diferentes modelos de prova.

---

## 📈 9. Análise de Marcação

### 📌 Técnicas:

* `np.count_nonzero()` – Conta pixels brancos em cada caixa (correspondentes às marcações).
* Seleção da alternativa com mais pixels, se acima de um **limiar de marcação** (ex: 30).

### 🎯 Objetivo:

Determinar qual alternativa foi marcada de forma clara. Marcações fracas ou ausentes são ignoradas (`?`).

---

## 🟩 10. Depuração Visual (Modo Debug)

### 📌 Técnicas:

* `cv2.rectangle()`, `cv2.putText()`, `cv2.imwrite()`
* Armazenamento em pastas organizadas por prova e linha.

### 🎯 Objetivo:

Facilitar a inspeção visual das marcações detectadas, útil para ajustes de parâmetros e testes.

---

## 📤 11. Exportação de Resultados

### 📌 Arquivos gerados:

* `respostas_PROVA_XXX.txt` – Resumo das alternativas marcadas.
* `cartao_corrigido_PROVA_XXX.png` – Imagem final corrigida.
* `resposta.csv` – Consolidado com colunas `id_prova`, `questao`, `resposta`.

### 🛠 Ajustes Importantes:

* O arquivo `resposta.csv` agora está no **formato correto esperado pela rotina de correção**, com ordem: `id_prova;questao;resposta`.

---

## ✅ 12. Correção com Gabarito Oficial

Um segundo script compara as respostas detectadas com um gabarito oficial em CSV.

### 📌 Funcionalidades:

* Verifica se os arquivos têm as colunas certas.
* Corrige problemas com codificação UTF-8 (ex: BOM em nomes de coluna).
* Compara automaticamente cada resposta com o gabarito.
* Gera um **log detalhado** com ✓ para acertos e ✘ para erros.
* Calcula métricas finais e exporta o arquivo `log_comparacao.csv`.

---

## 📊 Métricas Produzidas (Execução Real)

O sistema foi testado com um conjunto real de cartões. A seguir, os resultados obtidos:

| Métrica                      | Valor            |
| ---------------------------- | ---------------- |
| Total de comparações válidas | **14.656**       |
| Total de acertos             | **10.215**       |
| Acurácia                     | **69.70%**       |
| Tempo de execução            | **1.00 segundo** |
| Pico de memória utilizada    | **9601.69 KB**   |

> ⚙️ Esses dados foram obtidos com base no processamento real feito na máquina local (Windows, Python + OpenCV).


