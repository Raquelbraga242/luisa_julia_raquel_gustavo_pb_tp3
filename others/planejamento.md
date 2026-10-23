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