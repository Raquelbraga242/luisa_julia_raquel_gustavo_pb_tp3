# Planejamento do Modelo de Classificação e Teste Adversarial (TP3)

---

## 6.1 — Modelo Candidato

**Algoritmo escolhido:** Regressão Logística Multinomial com regularização L2, tendo o `LinearSVC` como alternativa para comparação.

**Motivo da escolha:**

Nosso problema consiste em classificar chamados de suporte em cinco intenções diferentes (`Refund request`, `Technical issue`, `Cancellation request`, `Product inquiry` e `Billing inquiry`). A escolha da Regressão Logística considera os seguintes aspectos:

* **Bom desempenho com dados de texto (matrizes esparsas):** Ao transformar os textos em contagens de palavras, obtemos uma matriz com milhares de colunas, muitas delas preenchidas com zeros. Modelos lineares como a Regressão Logística lidam bem com esse tipo de representação, oferecendo baixo custo computacional e treinamento rápido.
* **Interpretação e probabilidades:** O modelo aprende pesos associados às palavras para cada classe, permitindo analisar quais termos influenciam a classificação. Além disso, estima uma probabilidade para cada classe, o que pode ajudar a definir um limite mínimo de confiança na API. Para isso, será necessário avaliar essas estimativas com dados de validação.
* **Análise nos testes adversariais:** A análise dos pesos pode ajudar a entender como alterações no texto afetam as decisões do modelo. Durante os testes de pentest, poderemos avaliar mudanças como inserção de palavras, substituição por sinônimos e erros de digitação intencionais para verificar se essas alterações levam a classificações incorretas.

---

## 6.2 — Estratégia de Representação do Texto

**Técnica escolhida:** `CountVectorizer` (Scikit-Learn).

**Motivo da escolha:**

Como os algoritmos de classificação trabalham com valores numéricos, precisamos converter o texto da coluna `Ticket Description` em vetores. O `CountVectorizer` utiliza a abordagem *Bag-of-Words*, criando um vocabulário com as palavras da base e contando quantas vezes cada termo aparece em cada chamado.

Optamos por ele por ser uma abordagem simples e permitir o uso de parâmetros relacionados aos pontos identificados na análise exploratória (EDA):

* `lowercase=True`: converte o texto para letras minúsculas, evitando tratar a mesma palavra escrita com capitalização diferente como termos distintos;
* `ngram_range=(1, 2)`: considera palavras isoladas e pares de palavras consecutivas (ex.: *"refund request"*, *"not working"*, *"cancel subscription"*), permitindo representar expressões curtas;
* `min_df` e `max_df`: removem termos muito raros ou presentes em grande parte dos textos, conforme os limites definidos. Isso pode reduzir ruídos e ajudar a controlar o *overfitting*;
* Remoção de *stop words*: elimina palavras funcionais, como artigos e conectivos, quando não contribuem para a classificação.

Essa combinação gera uma representação leve, de processamento rápido e compatível com a Regressão Logística, adequada ao uso nos endpoints da API.

---

## 6.3 — Alvo para o teste adversarial

Para disponibilizar a API da equipe externamente, foi utilizado o **Cloudflare Tunnel**, apontando para a aplicação FastAPI executada localmente na porta `8000`.

O túnel foi iniciado com o comando:

```bash
cloudflared tunnel --url http://localhost:8000
```

A URL pública HTTPS gerada durante o TP3 foi:

```text
https://calibration-ban-winston-subsequently.trycloudflare.com
```

A documentação interativa da API ficou disponível em:

```text
https://calibration-ban-winston-subsequently.trycloudflare.com/docs
```

Essa URL será utilizada como referência para o alvo autorizado dos testes adversariais previstos no TP4.

Como foi utilizado um **Cloudflare Quick Tunnel**, a URL é temporária e depende da execução local da API e do processo `cloudflared`. Caso seja necessário realizar os testes em outro momento, um novo túnel poderá ser gerado e a URL ativa será compartilhada com a equipe responsável.
