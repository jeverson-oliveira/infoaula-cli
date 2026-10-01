# Segurança — InfoAula

Projeto educacional, repo público, sem dados sensíveis por design.

## O que é seguro por padrão

- API **somente leitura (GET)** — sem login, sem escrita, sem upload.
- Nenhum secret no código. Banco Postgres local usa `.env` (veja `.env.example`).
  Valores no compose são **dev-only** e o banco não expõe porta.
- Conteúdo exibido no terminal é escapado (Rich `escape`) — `seed.json` ou
  API remota não consegue injetar formatação.
- `/sync` limitado a ~2MB; queries da API com `max_length` e `limit <= 100`;
  nginx com rate-limit (10 r/s) e `limit_except GET`.

## Riscos que a escola/VPS deve tratar

1. **HTTP vs HTTPS (mais importante).**
   `curl $URL/infoaula.sh | bash` e `infoaula sync` via `http://` permitem
   MITM na rede da escola. Em produção sirva a API em **https://**
   (Caddy, Traefik ou Cloudflare Tunnel) e distribua
   `INFOAULA_URL=https://...`. O script e o `sync` avisam quando detectam
   `http://` fora de localhost.
2. **Conteúdo da API é confiável por configuração.**
   `INFOAULA_API_URL` aponta para onde o CLI baixa conteúdo. Aponte só para
   sua VPS. Não use URL de terceiros.
3. **Senha do Postgres.** Troque via `.env` na VPS
   (`POSTGRES_PASSWORD=...` forte). Nunca commite `.env`.
4. **Rede.** Não publique a porta do Postgres. Só `8080` (nginx/API)
   precisa ser acessível pelos alunos.

## Reportar vulnerabilidade

Abra uma issue privada ou e-mail ao mantenedor com: descrição, passos para
reproduzir e impacto. Não abra PoC pública antes da correção. Miramos resposta
em até 7 dias e correção em até 30 dias para issues críticas.
