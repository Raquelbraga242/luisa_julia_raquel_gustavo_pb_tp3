# Análise do Scan Passivo com OWASP ZAP

Foi realizado um scan passivo com OWASP ZAP contra a API executada localmente em `http://127.0.0.1:8000`.

Durante a navegação, o navegador utilizado pelo ZAP também gerou requisições para serviços externos, como Microsoft Edge, Bing, jsDelivr e outros domínios. Por esse motivo, os alertas foram analisados individualmente e foram considerados abaixo apenas os findings Medium ou High relacionados diretamente à aplicação.

## 1. Credenciais de Autenticação Capturadas

**Finding:** Credenciais de Autenticação Capturadas

**Severidade:** High

**Confiança:** Medium

**URL afetada:** `http://127.0.0.1:8000/auth/token`

**O que foi detectado:**  
O ZAP identificou o envio de usuário e senha pelo endpoint de autenticação através de uma conexão HTTP.

**Por que é um problema:**  
Como HTTP não oferece criptografia durante o transporte, um atacante com acesso ao tráfego da rede poderia interceptar as credenciais enviadas para o endpoint de autenticação.

**Correção realizada:**  
A aplicação foi executada por HTTP apenas no ambiente local utilizado para desenvolvimento e testes. Para um ambiente de produção, o endpoint deve ser disponibilizado exclusivamente através de HTTPS, utilizando TLS para proteger as credenciais e os tokens em trânsito.

**Validação:**  
O finding foi identificado somente porque o scan foi realizado em `http://127.0.0.1:8000`. A aplicação deve ser novamente validada no ambiente de produção após a configuração de HTTPS.

**Risco aceito:**  
O risco foi aceito apenas no ambiente local de desenvolvimento, onde a aplicação não está exposta publicamente. O uso de HTTP não deve ser aceito em produção.

---

## 2. CSP - Failure to Define Directive with No Fallback

**Finding:** CSP: Failure to Define Directive with No Fallback

**Severidade:** Medium

**Confiança:** High

**URL afetada:** `http://127.0.0.1:8000/docs`

**O que foi detectado:**  
O ZAP identificou que a política Content-Security-Policy configurada pela aplicação não define explicitamente a diretiva `form-action`. Essa diretiva não utiliza `default-src` como fallback.

**Por que é um problema:**  
Quando determinadas diretivas não são definidas explicitamente, alguns comportamentos do navegador podem ficar menos restritos do que o esperado. Isso reduz a proteção adicional oferecida pela CSP contra determinados tipos de abuso de conteúdo.

**Correção realizada:**  
Nenhuma alteração foi aplicada nesta entrega porque o finding está restrito à interface automática do Swagger utilizada para documentação e testes da API.

**Validação:**  
Foi verificado no relatório que o finding ocorre especificamente na rota `/docs` e não nos endpoints JSON utilizados pela aplicação.

**Risco aceito:**  
O risco foi aceito para o ambiente de desenvolvimento. Em produção, a documentação Swagger pode ser desabilitada ou a CSP pode ser endurecida com a inclusão explícita das diretivas necessárias.

---

## 3. CSP - script-src unsafe-inline

**Finding:** CSP: script-src unsafe-inline

**Severidade:** Medium

**Confiança:** High

**URL afetada:** `http://127.0.0.1:8000/docs`

**O que foi detectado:**  
A diretiva `script-src` da Content-Security-Policy inclui `'unsafe-inline'`.

**Por que é um problema:**  
A utilização de `'unsafe-inline'` reduz a efetividade da CSP contra ataques de Cross-Site Scripting, pois permite a execução de scripts inline na página.

**Correção realizada:**  
O valor foi mantido nesta entrega porque a interface Swagger gerada pelo FastAPI depende de conteúdo utilizado na própria página de documentação.

**Validação:**  
O scan confirmou que o finding está relacionado à rota `/docs`, utilizada para documentação e testes da API.

**Risco aceito:**  
O risco foi aceito no ambiente de desenvolvimento por estar associado à interface Swagger. Em produção, a documentação pode ser desabilitada ou substituída por uma configuração que utilize nonce ou hash para permitir apenas scripts autorizados.

---

## 4. CSP - style-src unsafe-inline

**Finding:** CSP: style-src unsafe-inline

**Severidade:** Medium

**Confiança:** High

**URL afetada:** `http://127.0.0.1:8000/docs`

**O que foi detectado:**  
A diretiva `style-src` da Content-Security-Policy contém `'unsafe-inline'`.

**Por que é um problema:**  
Permitir estilos inline reduz a restrição oferecida pela CSP e pode facilitar determinados tipos de injeção de conteúdo caso exista outra vulnerabilidade na aplicação.

**Correção realizada:**  
O valor foi mantido para garantir o funcionamento adequado da interface Swagger no ambiente de desenvolvimento.

**Validação:**  
Foi confirmado através do relatório do ZAP que o finding está associado especificamente à página `/docs`.

**Risco aceito:**  
O risco foi aceito para a documentação de desenvolvimento. Para produção, a documentação pode ser desabilitada ou os estilos podem ser fornecidos de forma controlada, eliminando a necessidade de `'unsafe-inline'`.

---

## 5. Sub Resource Integrity Attribute Missing

**Finding:** Sub Resource Integrity Attribute Missing

**Severidade:** Medium

**Confiança:** High

**URL afetada:** `http://127.0.0.1:8000/docs`

**O que foi detectado:**  
A página do Swagger carrega arquivos CSS e JavaScript externos a partir do `cdn.jsdelivr.net` sem utilizar o atributo `integrity`.

**Por que é um problema:**  
Sem Subresource Integrity, o navegador não verifica se o conteúdo recebido do servidor externo corresponde exatamente ao arquivo esperado. Caso o recurso externo seja comprometido, conteúdo malicioso poderia ser carregado pela página.

**Correção realizada:**  
Nenhuma alteração foi feita nesta entrega porque esses recursos são carregados automaticamente pela interface Swagger gerada pelo FastAPI.

**Validação:**  
O relatório do ZAP identificou duas ocorrências, referentes ao CSS e ao JavaScript utilizados pelo Swagger UI.

**Risco aceito:**  
O risco foi aceito no ambiente de desenvolvimento. Em produção, a documentação Swagger pode ser desabilitada ou seus arquivos estáticos podem ser hospedados localmente com controle de integridade.

---

## Conclusão

O scan passivo identificou um finding High relacionado ao uso de HTTP no ambiente local e quatro findings Medium relacionados principalmente à interface de documentação Swagger.

O finding de maior impacto é o envio de credenciais sem criptografia durante o transporte. Esse risco é aceitável apenas durante o desenvolvimento local e deve ser eliminado antes de qualquer disponibilização da aplicação em produção através do uso obrigatório de HTTPS.

Os demais findings estão concentrados na rota `/docs` e foram aceitos no ambiente de desenvolvimento. Para um ambiente de produção, a interface Swagger pode ser desabilitada ou configurada de forma mais restritiva.

Alertas referentes a domínios externos capturados pelo navegador durante o scan não foram considerados vulnerabilidades da API.