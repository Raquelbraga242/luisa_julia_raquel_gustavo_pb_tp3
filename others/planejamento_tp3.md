# Planejamento do Modelo de Classificação e Teste Adversarial (TP3)

Este documento define a abordagem de Machine Learning para a próxima etapa do projeto e registra o endereço da API que será utilizado nos testes adversariais .

---

## 6.1 — Modelo Candidato

**Algoritmo escolhido:** Regressão Logística Multinomial (com regularização L2) — tendo o `LinearSVC` como alternativa direta para comparação.

**Motivo da escolha:**
O nosso problema consiste em classificar os chamados de suporte em 5 intenções diferentes (`Refund request`, `Technical issue`, `Cancellation request`, `Product inquiry` e `Billing inquiry`). Escolhemos a Regressão Logística pelos seguintes pontos práticos:

* **Bom desempenho com dados de texto (matrizes esparsas):** Quando transformamos texto em contagens de palavras, a matriz resultante tem milhares de colunas preenchidas majoritariamente por zeros. Modelos lineares como a Regressão Logística lidam muito bem com esse formato, treinando rápido e com baixo custo computacional.
* **Facilidade de interpretação e probabilidades:** Diferente de modelos mais complexos (como redes neurais), a Regressão Logística atribui pesos diretos para cada palavra em relação a cada classe, permitindo entender quais termos puxam a decisão do modelo. Além disso, ela retorna a probabilidade de cada classe (via função *softmax*), o que ajuda a definir um corte mínimo de confiança na API.
* **Análise nos testes adversariais (TP4/TP5):** Como os pesos das palavras são diretos e lineares, fica mais fácil analisar o comportamento do modelo durante o pentest quando testarmos injeção de palavras, troca de sinônimos ou erros de digitação propositais para tentar enganar o classificador.

---

## 6.2 — Estratégia de Representação do Texto

**Técnica escolhida:** `CountVectorizer` (Scikit-Learn).

**Motivo da escolha:**
Como algoritmos de classificação só processam valores numéricos, precisamos converter o texto da coluna `Ticket Description` em vetores. O `CountVectorizer` aplica a abordagem *Bag-of-Words*, montando um vocabulário com as palavras da base e contando quantas vezes cada termo aparece no chamado.

Optamos por ele porque resolve o problema de forma simples e permite aplicar direto os filtros que identificamos na análise exploratória (EDA):
* `lowercase=True`: padroniza tudo em letras minúsculas para não duplicar palavras iguais;
* `ngram_range=(1, 2)`: considera tanto palavras isoladas quanto pares de palavras seguidas (ex.: *"refund request"*, *"not working"*, *"cancel subscription"*), o que evita perder o sentido de expressões curtas;
* `min_df` e `max_df`: descarta palavras que aparecem em quase todos os textos (que não ajudam a diferenciar a intenção) e termos muito raros ou erros de digitação, reduzindo o risco de *overfitting*;
* Remoção de *stop words*: limpa conectivos e artigos sem valor para a classificação.

Essa combinação gera uma representação leve, rápida de processar nos endpoints da API e diretamente compatível com a Regressão Logística.

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
