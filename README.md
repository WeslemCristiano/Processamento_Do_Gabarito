

**Correção Automática de Cartões de Resposta**

**Alunos:** Weslem; Giovanni; Luis
**Professor:** Wellington Della Mura 

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
* `cv2.approxPolyDP()`: Aproximação de polígonos para contornos.
* `cv2.contourArea()`: Filtro por área mínima.
* `cv2.moments()` + centroide: Cálculo da posição central dos triângulos.

### 🎯 Objetivo:

Detectar os 4 triângulos nos cantos do cartão para permitir a **correção de perspectiva**. Essas formas são escolhidas por serem fáceis de identificar e resistentes a ruídos.

---

## 🔄 3. **Correção de Perspectiva (Homografia)**

### 📌 Técnicas:

* `cv2.getPerspectiveTransform()`: Cálculo da matriz de transformação.
* `cv2.warpPerspective()`: Aplicação da homografia para alinhar o cartão na imagem.

### 🎯 Objetivo:

Corrigir distorções provocadas por inclinação da câmera ou escaneamento torto, garantindo que o cartão fique "reto" e padronizado.

---

## 📊 4. **Segmentação do Cartão em Colunas e Linhas**

### 📌 Técnicas:

* Divisão da imagem com base em coordenadas conhecidas (divisão em 3 colunas e 20 linhas por coluna).
* Crop da altura inicial e final para isolar as linhas das questões.

### 🎯 Objetivo:

Facilitar o acesso direto a cada **linha de questão**, possibilitando análise independente de cada uma.

---

## 🧾 5. **Binarização**

### 📌 Técnicas:

* `cv2.threshold()` com método `cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU`

### 🎯 Objetivo:

Converter cada linha para **imagem binária (preto e branco)**. O método de Otsu ajusta automaticamente o limiar de binarização com base no histograma da imagem, sendo ideal para imagens com variação de iluminação.

---

## ⬛ 6. **Detecção das Alternativas por Contornos**

### 📌 Técnicas:

* `cv2.findContours()` novamente nas linhas binarizadas.
* `cv2.boundingRect()`: Extração das coordenadas das caixas de alternativas.
* Filtros por:

  * **Largura e altura**
  * **Aspect ratio**
  * **Área do contorno**

### 🎯 Objetivo:

Identificar as **5 caixas (A–E)** presentes em cada linha, sem depender de coordenadas fixas. Isso torna o sistema adaptável a pequenas variações de alinhamento e escaneamento.

---

## 📈 7. **Análise de Marcação**

### 📌 Técnicas:

* `np.count_nonzero()`: Contagem de pixels **brancos** dentro de cada caixa detectada.
* Comparação da contagem com um **limiar mínimo (`THRESHOLD_MARCACAO`)**.

### 🎯 Objetivo:

Determinar qual caixa está marcada com base na **intensidade da marcação** (mais pixels brancos indicam marcação mais escura na versão binária invertida).

---

## 🟩 8. **Depuração Visual (Debug)**

### 📌 Técnicas:

* `cv2.rectangle()`: Desenho das caixas detectadas.
* `cv2.putText()`: Colocação de letra indicadora (A–E).
* `cv2.imwrite()`: Salvamento de imagens com marcações visuais.

### 🎯 Objetivo:

Permitir **inspeção manual** das regiões de interesse para validação e ajuste do sistema.

---

## 📋 9. **Geração de Relatório**

### 📌 Técnicas:

* Escrita em arquivos `.txt` para salvar:

  * Respostas detectadas.
  * Correções com ✓/✘.
  * Total de acertos e porcentagem de aproveitamento.

---





