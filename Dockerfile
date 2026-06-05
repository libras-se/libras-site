FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf

WORKDIR /usr/share/nginx/html

COPY 404.html index.html llms-full.txt llms.txt manifest.json robots.txt sitemap.xml ./
COPY acessibilidade-para-curta-metragem/ ./acessibilidade-para-curta-metragem/
COPY acessibilidade-para-documentario/ ./acessibilidade-para-documentario/
COPY acessibilidade-para-festival-de-cinema/ ./acessibilidade-para-festival-de-cinema/
COPY acessibilidade-para-longa-metragem/ ./acessibilidade-para-longa-metragem/
COPY acessibilidade-para-projetos-culturais/ ./acessibilidade-para-projetos-culturais/
COPY acessibilidade-para-serie/ ./acessibilidade-para-serie/
COPY assets/ ./assets/
COPY autora/ ./autora/
COPY blog/ ./blog/
COPY category/ ./category/
COPY contato/ ./contato/
COPY elementor-466/ ./elementor-466/
COPY glossario/ ./glossario/
COPY hello-world/ ./hello-world/
COPY jogo/ ./jogo/
COPY libras-ao-vivo/ ./libras-ao-vivo/
COPY libras-para-campanhas-politicas/ ./libras-para-campanhas-politicas/
COPY libras-para-empresas/ ./libras-para-empresas/
COPY libras-para-publicidade/ ./libras-para-publicidade/
COPY libras-para-videoaulas/ ./libras-para-videoaulas/
COPY nossa-te/ ./nossa-te/
COPY nossa-tecnologia/ ./nossa-tecnologia/
COPY orcamento/ ./orcamento/
COPY politica/ ./politica/
COPY portfolio/ ./portfolio/
COPY post/ ./post/
COPY privacidade/ ./privacidade/
COPY produtos/ ./produtos/
COPY proposito/ ./proposito/
COPY sejatils/ ./sejatils/
COPY sinal/ ./sinal/
COPY solucoes/ ./solucoes/
COPY tecnologia/ ./tecnologia/
COPY trabalhos/ ./trabalhos/
COPY video/ ./video/
COPY voce-sabe-o-que-e-datilologia/ ./voce-sabe-o-que-e-datilologia/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
