# Análise do Scan Passivo com OWASP ZAP (TP3)

Foi realizado um scan passivo final com OWASP ZAP contra a API executada localmente em `http://127.0.0.1:8000`.

Durante a navegação, o navegador utilizado pelo ZAP também gerou requisições para serviços externos, como Microsoft Edge, Bing, jsDelivr e outros domínios. Por esse motivo, os alertas foram analisados individualmente e foram considerados abaixo os 5 findings Medium ou High identificados na auditoria inicial relacionados diretamente à aplicação, juntamente com as correções aplicadas em `headers.py` e o resultado da reauditoria.

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
No arquivo `headers.py` (indicado com comentário `[CORREÇÃO ZAP]`), foi adicionado o cabeçalho `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload` (HSTS) no dicionário `HEADERS_SEGURANCA`. Além disso, para acesso externo e homologação, a API foi disponibilizada com conexão HTTPS através do Cloudflare Tunnel (`https://calibration-ban-winston-subsequently.trycloudflare.com`).

**Validação:**  
Na reauditoria, confirmou-se que o cabeçalho HSTS está ativo nas respostas da API. O alerta permanece no relatório local apenas porque o scan foi executado contra `http://127.0.0.1:8000` (sem TLS local). Através da URL HTTPS do Cloudflare Tunnel, o tráfego é criptografado por TLS, eliminando a exposição das credenciais em trânsito.

**Risco aceito:**  
O risco de uso de HTTP foi aceito exclusivamente para a execução em `localhost` durante o desenvolvimento, onde o tráfego não sai da máquina local. Em qualquer exposição externa, o acesso ocorre via HTTPS.

---

## 2. CSP - Failure to Define Directive with No Fallback

**Finding:** CSP: Failure to Define Directive with No Fallback

**Severidade:** Medium

**Confiança:** High

**URL afetada:** `http://127.0.0.1:8000/docs`

**O que foi detectado:**  
Na auditoria inicial, o ZAP identificou que a política Content-Security-Policy configurada pela aplicação não definia explicitamente a diretiva `form-action`, que não utiliza `default-src` como fallback.

**Por que é um problema:**  
Quando diretivas sem fallback (como `form-action` e `frame-ancestors`) não são definidas explicitamente, formulários ou quadros da página podem enviar dados ou ser embutidos em origens não autorizadas, reduzindo a proteção contra abusos de conteúdo e Clickjacking.

**Correção realizada:**  
No arquivo `headers.py` (sinalizado com comentário `[CORREÇÃO ZAP]`), foram incluídas explicitamente as diretivas `form-action 'self'` e `frame-ancestors 'none'` tanto na política das rotas da API (`CSP_API`) quanto na política da documentação (`CSP_DOCUMENTACAO`), em conjunto com o cabeçalho `X-Frame-Options: DENY`.

**Validação:**  
Após a alteração no código e reauditoria com o OWASP ZAP, foi comprovado que este finding foi completamente resolvido e deixou de existir no relatório final (0 ocorrências).

**Risco aceito:**  
Nenhum risco pendente. Vulnerabilidade integralmente corrigida no código.

---

## 3. CSP - script-src unsafe-inline

**Finding:** CSP: script-src unsafe-inline

**Severidade:** Medium

**Confiança:** High

**URL afetada:** `http://127.0.0.1:8000/docs`

**O que foi detectado:**  
A diretiva `script-src` da Content-Security-Policy na rota de documentação inclui `'unsafe-inline'`.

**Por que é um problema:**  
A utilização de `'unsafe-inline'` reduz a efetividade da CSP contra ataques de Cross-Site Scripting, pois permite a execução de scripts inline na página.

**Correção realizada:**  
No arquivo `headers.py`, as políticas de CSP foram separadas por rota. Para todos os endpoints da API (`/predict`, `/auth/token`, `/health`), foi aplicada a constante `CSP_API` (`default-src 'none'; frame-ancestors 'none'; form-action 'self'`), bloqueando qualquer execução de scripts. A constante `CSP_DOCUMENTACAO`, contendo `'unsafe-inline'` restrito a `'self'` e `https://cdn.jsdelivr.net`, foi isolada exclusivamente para as rotas `/docs` e `/redoc` para manter a documentação interativa do FastAPI funcional.

**Validação:**  
O relatório final do ZAP comprovou que os endpoints de operação da API não apresentam este alerta (0 ocorrências), ficando a ocorrência restrita unicamente à página `/docs`.

**Risco aceito:**  
O risco foi aceito estritamente na rota `/docs` para cumprir o requisito de disponibilizar a interface interativa do Swagger UI gerada pelo FastAPI.

---

## 4. CSP - style-src unsafe-inline

**Finding:** CSP: style-src unsafe-inline

**Severidade:** Medium

**Confiança:** High

**URL afetada:** `http://127.0.0.1:8000/docs`

**O que foi detectado:**  
A diretiva `style-src` da Content-Security-Policy na rota de documentação contém `'unsafe-inline'`.

**Por que é um problema:**  
Permitir estilos inline reduz a restrição oferecida pela CSP e pode facilitar determinados tipos de injeção de conteúdo caso exista outra vulnerabilidade na aplicação.

**Correção realizada:**  
No arquivo `headers.py`, aplicou-se a política restritiva `CSP_API` (`default-src 'none'`) em todas as rotas JSON da aplicação, eliminando qualquer permissão de estilo nos endpoints de serviço. Na rota `/docs` (`CSP_DOCUMENTACAO`), o escopo de estilos foi restrito a `'self'` e `https://cdn.jsdelivr.net`, mantendo `'unsafe-inline'` apenas nessa rota para renderizar a interface do Swagger UI.

**Validação:**  
Foi confirmado no relatório final do ZAP que nenhum endpoint funcional da API apresenta o alerta (0 ocorrências), ocorrendo especificamente na página `/docs`.

**Risco aceito:**  
O risco foi aceito apenas na rota `/docs` para garantir o funcionamento visual da documentação interativa.

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
No arquivo `headers.py`, o carregamento de recursos externos foi completamente bloqueado nas rotas da API por meio da política `CSP_API` (`default-src 'none'`). Nas rotas `/docs` e `/redoc` (`CSP_DOCUMENTACAO`), as origens permitidas na CSP foram restritas explicitamente ao domínio HTTPS `https://cdn.jsdelivr.net`, utilizado nativamente pelo FastAPI para montar o Swagger UI.

**Validação:**  
O relatório final do ZAP confirmou que as rotas da API não carregam recursos externos (0 ocorrências), restringindo o alerta às duas chamadas estáticas (CSS e JS) do Swagger UI em `/docs`.

**Risco aceito:**  
O risco foi aceito na rota `/docs` por se tratar do template padrão do FastAPI necessário para manter a documentação interativa ativa. Em produção, a documentação pode ser desabilitada ou seus arquivos estáticos podem ser servidos localmente com hash de integridade.

---

## Conclusão

Após as correções implementadas no middleware `headers.py` e a reauditoria com o OWASP ZAP:

1. O finding **CSP: Failure to Define Directive with No Fallback** (Medium) foi totalmente eliminado (0 ocorrências no relatório final) com a inclusão de `form-action 'self'` e `frame-ancestors 'none'`.
2. Os endpoints de serviço da API (`/predict`, `/auth/token`, `/health`) ficaram protegidos com `default-src 'none'`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff` e `Strict-Transport-Security`, não apresentando nenhum alerta de CSP ou SRI.
3. O finding High (**Credenciais de Autenticação Capturadas**) ocorre no relatório local unicamente pelo uso de `http://127.0.0.1:8000` nos testes locais, estando mitigado no código via HSTS e no acesso externo pelo uso de HTTPS via Cloudflare Tunnel.
4. Os três alertas Medium remanescentes no relatório final concentram-se exclusivamente na rota `/docs` e decorrem dos recursos padrão utilizados pelo FastAPI para renderizar o Swagger UI interativo exigido pelo projeto.

Alertas referentes a domínios externos capturados pelo navegador durante o scan não foram considerados vulnerabilidades da API.
