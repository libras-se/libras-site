# Redirecionador do old.libras.se

O blog antigo da LIBRAS.SE (Wix) ainda responde em `old.libras.se`, com os mesmos posts do blog novo
e canonical apontando para ele mesmo. Isso divide a autoridade entre as duas cópias. Este container
troca o Wix por um nginx que devolve **301** de cada endereço antigo para o post certo em `libras.se`.

- `default.conf`: servidor nginx. Robots liberado, `/saude` para o health check, 301 para o resto.
- `redirects.map`: mapa origem → destino. **Gerado** por `python3 tools/seo/redirects.py` a partir de
  `tools/seo/redirects.json`. Não edite à mão.
- `Dockerfile`: `nginx:alpine` + `nginx -t` no build.

## Subir no Dokploy (servidor 72.61.35.64, o mesmo de api, huet e tils)

1. **Create Service → Application.** Provider: GitHub, repositório `libras-se/libras-site`, branch `main`.
2. **Build Type:** Dockerfile.
   - Docker File: `tools/redirects/old-libras-se/Dockerfile`
   - Docker Context Path: `tools/redirects/old-libras-se`
3. **Domains:** `old.libras.se`, porta do container `80`, HTTPS ligado, certificado Let's Encrypt.
4. **Deploy.** Teste antes de mexer no DNS (o Traefik do Dokploy roteia pelo Host):

   ```sh
   curl -sI --resolve old.libras.se:80:72.61.35.64 http://old.libras.se/post/surdos-estrangeiros-na-propria-patria
   # esperado: 301 e Location para o Traefik (https) ou para https://libras.se/blog/surdos-estrangeiros-na-propria-patria/
   ```

## DNS na Hostinger (hPanel → Domínios → libras.se → DNS)

1. Um dia antes, baixe o TTL do registro `old` (hoje CNAME `pointing.wixdns.net`) para 300.
2. Troque o registro: apague o CNAME `old` e crie **A `old` → 72.61.35.64** (TTL 300).
3. Espere propagar (`dig +short old.libras.se` deve devolver 72.61.35.64) e reemita o certificado no
   Dokploy, se ele não tiver saído sozinho. O Let's Encrypt só valida depois que o DNS aponta para o servidor.
4. Confira:

   ```sh
   curl -sI https://old.libras.se/post/crian%C3%A7a-surda-batizada-em-libras-em-caruaru
   # 301 → https://libras.se/blog/crianca-surda-batizada-em-libras-em-caruaru/
   ```

## Depois

- No Wix: desconecte o domínio `old.libras.se` e despublique o site (o endereço `*.wixsite.com` também fica no ar).
- No Search Console: com a propriedade de domínio `libras.se` verificada, o `old.` aparece junto.
  Acompanhe em Páginas a queda das URLs do `old.` e o aumento das de `libras.se/blog/`.
- Para incluir um endereço novo: edite `tools/seo/redirects.json`, rode `python3 tools/seo/redirects.py`,
  faça o merge e redeploy deste serviço no Dokploy.
