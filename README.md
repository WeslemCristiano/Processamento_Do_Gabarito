## 📄 Correção Automática de Cartões de Resposta

* **Alunos:** Weslem, Giovanni, Luis
* **Professor:** Wellington Della Mura

**Projeto:** Leitor automático de cartões de múltipla escolha com detecção visual de marcações.
**Tecnologias:** Python, OpenCV, NumPy

---

## 🔍 1. **Leitura e Pré-processamento da Imagem**

### 📌 Técnicas:

* `cv2.imread()`: Leitura da imagem.
* `cv2.cvtColor()`: Conversão para tons de cinza (grayscale).
* `cv2.GaussianBlur()`: Suavização da imagem para remover ruído.
* `cv2.Canny()`: Detecção de bordas.

### 🎯 Objetivo:

Melhorar a qualidade visual e extrair bordas para permitir a **detecção dos marcadores (triângulos)** nos cantos do cartão.

---

## 📐 2. **Detecção de Marcadores de Referência (Triângulos)**

### 📌 Técnicas:

* `cv2.findContours()`: Identificação de contornos.
* `cv2.approxPolyDP()`: Aproximação de polígonos.
* `cv2.contourArea()`: Filtro por área mínima.
* `cv2.moments()` + centroide: Cálculo do centro de massa de cada triângulo.
* **Filtro vertical**: Ignora triângulos muito acima (ex: próximos ao código de barras).

### 🎯 Objetivo:

Detectar os 4 triângulos posicionados nas bordas do cartão. Esses pontos são fundamentais para **corrigir a perspectiva da imagem** e alinhar o cartão.

---

## 🔁 3. **Ordenação dos Triângulos**

### 📌 Técnicas:

* Função `ordenar_pontos_triangulos()`:

  * Baseada na **soma e diferença das coordenadas** `x + y` e `x - y`
  * Identifica e ordena os triângulos em: **superior esquerdo**, **superior direito**, **inferior direito**, **inferior esquerdo**

### 🎯 Objetivo:

Evitar distorções ao aplicar a homografia. A ordem correta dos pontos é essencial para gerar uma imagem “reta” e proporcional.

---

## 🔄 4. **Correção de Perspectiva (Homografia)**

### 📌 Técnicas:

* `cv2.getPerspectiveTransform()`: Cálculo da matriz de transformação.
* `cv2.warpPerspective()`: Aplicação da transformação para alinhar o cartão.

### 🎯 Objetivo:

Elimina distorções de inclinação da câmera ou escaneamento torto, permitindo análise precisa das marcações.

---

## 🧼 5. **Limpeza Fora da Área do Cartão (Máscara Branca)**

### 📌 Técnicas:

* `cv2.fillConvexPoly()`: Criação de máscara poligonal da área do cartão.
* `cv2.bitwise_and()` + substituição de pixels externos por branco (`255`).

### 🎯 Objetivo:

**Remover sujeiras, bordas escaneadas, texto, barras e sombras** fora do cartão — mantendo apenas o conteúdo relevante.

---

## 📊 6. **Segmentação do Cartão em Colunas e Linhas**

### 📌 Técnicas:

* Divisão do cartão em 3 colunas fixas.
* Corte vertical para eliminar espaço superior e inferior.
* Cálculo da altura de cada linha proporcionalmente.

### 🎯 Objetivo:

Organizar visualmente a imagem para permitir análise individual de cada questão.

---

## 🧾 7. **Binarização**

### 📌 Técnicas:

* `cv2.threshold()` com `cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU`

### 🎯 Objetivo:

Transformar as linhas em preto e branco, facilitando a análise de marcações. O método de Otsu ajusta automaticamente o limiar com base no contraste local.

---

## ⬛ 8. **Detecção das Alternativas por Contornos**

### 📌 Técnicas:

* `cv2.findContours()` nas imagens binárias.
* `cv2.boundingRect()` para extrair coordenadas.
* Filtros por:

  * Largura e altura (ex: 8–50 px)
  * Aspect ratio (0.6–1.4)
  * Área mínima (> 30 px)

### 🎯 Objetivo:

Detectar as caixas das alternativas A–E **sem depender de posições fixas**, o que torna o sistema flexível a diferentes modelos de cartões.

---

## 📈 9. **Análise de Marcação**

### 📌 Técnicas:

* `np.count_nonzero()`: Conta os pixels brancos (correspondentes a marcações pretas invertidas).
* Seleciona a alternativa com maior quantidade de pixels acima do **limiar de marcação**.

### 🎯 Objetivo:

Determinar com confiabilidade qual alternativa foi marcada em cada linha.

---

## 🟩 10. **Depuração Visual (Debug)**

### 📌 Técnicas:

* `cv2.rectangle()`: Desenha retângulos nas caixas detectadas.
* `cv2.putText()`: Rotula cada caixa com sua letra correspondente (A–E).
* `cv2.imwrite()`: Salva imagens da análise de cada linha (`debug_linhas/`).

### 🎯 Objetivo:

Permitir inspeção manual do processo — fundamental para ajuste e validação do sistema.

---

## 📋 11. **Geração de Relatório Final**

### 📌 Técnicas:

* Escrita em `.txt` com:

  * Lista das alternativas detectadas.
  * Comparação com gabarito.
  * Correções marcadas com `✓` e `✘`.
  * Total de acertos e percentual de aproveitamento.

---
