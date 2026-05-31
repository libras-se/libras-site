import fs from 'node:fs/promises';
import path from 'node:path';

const exportPath = path.resolve('blog/old-libras-se-blog-export.json');

const currentPosts = new Map([
  ['como-sao-criados-sinais-de-pessoas-na-libras', 'blog/como-sao-criados-sinais-de-pessoas-na-libras/'],
  ['libras-nao-e-segunda-lingua-oficial-do-brasil', 'blog/libras-nao-e-segunda-lingua-oficial-do-brasil/'],
  ['voce-sabe-o-que-e-datilologia', 'blog/voce-sabe-o-que-e-datilologia/'],
  ['libras-ou-legendas-entenda-quando-ecomo-cada-recurso-deve-ser-usado', 'blog/libras-ou-legendas-entenda-quando-ecomo-cada-recurso-deve-ser-usado/'],
  ['o-que-e-libras', 'blog/o-que-e-libras/'],
  ['videoaulas-acessiveis-com-libras', 'blog/videoaulas-acessiveis-com-libras/'],
  ['libras-tem-sotaque-e-giria', 'blog/libras-tem-sotaque-e-giria/'],
  ['acessibilidade-em-eventos-como-garantir-interpreta%C3%A7%C3%A3o-em-libras-sem-improviso', 'blog/garantir-libras-sem-improviso/'],
]);

const high = new Map([
  ['surdos-voce-precisa-saber-se-comunicar-com-eles', 'Tema educativo amplo, com potencial de busca recorrente sobre comunicação com pessoas surdas.'],
  ['como-sao-criados-sinais-de-pessoas-na-libras', 'Conteudo explicativo evergreen, ja publicado com tratamento editorial.'],
  ['o-que-o-filme-ganhador-do-oscar-ensina-sobre-libras', 'Pode virar analise educativa sobre representacao, Libras e cultura surda.'],
  ['dia-nacional-dos-surdos-conquistas-e-reflex%C3%B5es', 'Data recorrente com potencial institucional e SEO anual.'],
  ['voce-sabe-o-que-e-datilologia', 'Conteudo conceitual evergreen, ja publicado com pagina elaborada.'],
  ['libras-ou-legendas-entenda-quando-ecomo-cada-recurso-deve-ser-usado', 'Comparativo educativo direto para busca e decisao de acessibilidade.'],
  ['entenda-porque-e-errado-o-termo-surdo-mudo', 'Tema conceitual recorrente com forte intencao educativa.'],
  ['dia-mundial-da-conscientiza%C3%A7%C3%A3o-sobre-o-autismo-como-a-l%C3%ADngua-de-sinais-tem-ajudado-crian%C3%A7as-com-aut', 'Tema explicativo que cruza acessibilidade, autismo e lingua de sinais.'],
  ['por-que-nao-ha-surdos-nas-paralimpiadas', 'Pergunta evergreen com potencial de busca e explicacao cultural/esportiva.'],
  ['papel-do-tradutor-e-interprete-de-libras-na-escola-bilingue', 'Tema de servico e educacao com alta profundidade possivel.'],
  ['o-papel-do-interprete-de-libras-na-sociedade', 'Tema educativo amplo sobre funcao profissional e impacto social.'],
  ['o-que-e-capacitismo', 'Conceito evergreen importante para busca e educacao inclusiva.'],
  ['libras-nao-e-segunda-lingua-oficial-do-brasil', 'Tema conceitual evergreen, ja publicado com pagina elaborada.'],
  ['4-erros-comuns-ao-inserir-libras-em-v%C3%ADdeos-e-como-evit%C3%A1-los', 'Guia pratico com forte potencial de conversao e SEO.'],
  ['dia-nacional-da-libras-inclusao-da-comunidade-surda', 'Data recorrente e tema institucional com potencial de atualizacao anual.'],
  ['entrevista-libras-nao-e-portugues-com-as-maos', 'Tema conceitual forte que pode virar pilar editorial sobre Libras.'],
  ['gestuante-entra-para-a-l%C3%ADngua-portuguesa-entenda-o-significado-e-o-uso-do-novo-termo', 'Explicacao de termo com potencial de busca e educacao linguistica.'],
  ['o-que-e-libras', 'Conteudo pilar evergreen, ja publicado com pagina elaborada.'],
  ['4-dicas-para-ser-mais-inclusivo-na-internet', 'Guia pratico evergreen sobre inclusao digital.'],
  ['videoaulas-acessiveis-com-libras', 'Conteudo de servico com potencial comercial e SEO, ja publicado.'],
  ['por-que-incluir-janela-de-libras-em-videos', 'Pergunta comercial/educativa com alta intencao de busca.'],
  ['o-papel-da-libras-na-inclusao-do-surdo', 'Conteudo pilar sobre inclusao e Libras.'],
  ['20-anos-da-lei-de-libras-avancos-e-desafios', 'Tema legal e historico, recorrente em buscas sobre a Lei de Libras.'],
  ['acessibilidade-em-eventos-para-pessoas-surdas', 'Tema de servico com potencial comercial e SEO para eventos acessiveis.'],
  ['libras-tem-sotaque-e-giria', 'Conteudo conceitual evergreen, ja publicado com pagina elaborada.'],
  ['acessibilidade-em-eventos-como-garantir-interpreta%C3%A7%C3%A3o-em-libras-sem-improviso', 'Guia de servico e conversao para eventos, ja publicado com novo slug.'],
  ['surdolimpiadas-as-olimpiadas-exclusivas-para-surdos', 'Tema explicativo com potencial de busca sobre esporte e cultura surda.'],
  ['dia-internacional-linguas-de-sinais', 'Data recorrente e tema institucional com potencial SEO anual.'],
]);

const medium = new Map([
  ['surdos-estrangeiros-na-propria-patria', 'Reflexao social relevante, mas menos direta como pagina pilar.'],
  ['influenciadores-surdos-relatam-dificuldade-com-publis', 'Tema de mercado e representatividade, pode render analise sem exigir layout complexo.'],
  ['documentarios-sobre-surdez-gratis-youtube', 'Lista util com potencial de busca moderado.'],
  ['interpretes-de-libras-traduzem-partos-para-pais-surdos', 'Materia pontual com tema humano forte e possibilidade de contextualizacao.'],
  ['makkari-a-super-hero%C3%ADna-surda', 'Tema cultural com potencial de representatividade, mas baseado em personagem especifica.'],
  ['manifesto-por-libras-em-videos', 'Conteudo de posicionamento editorial, bom para campanha e autoridade.'],
  ['inovacao-caminho-para-avancar-no-contexto-da-acessibilidade', 'Tema amplo, mas mais opinativo do que pilar direto de busca.'],
  ['b%C3%ADblia-completamente-traduzida-para-libras', 'Noticia com impacto cultural amplo e valor de contexto.'],
  ['4-marcas-que-investem-em-libras-nos-videos', 'Lista de exemplos com potencial comercial moderado.'],
  ['responsavel-pelo-que-entendem', 'Reflexao de marca/conteudo, boa para autoridade mas menor demanda orgânica.'],
  ['oscar-coda-melhor-filme-do-mundo-sobre-surdez', 'Tema cultural relevante, mais contextual do que pilar evergreen.'],
]);

const lowReason = 'Noticia ou caso pontual sobre Libras/surdez, importante para acervo, mas com menor potencial de SEO evergreen e menor necessidade de layout elaborado.';

function classify(slug) {
  if (high.has(slug)) {
    return { complexidadeLayout: 'alta', motivoComplexidade: high.get(slug) };
  }
  if (medium.has(slug)) {
    return { complexidadeLayout: 'media', motivoComplexidade: medium.get(slug) };
  }
  return { complexidadeLayout: 'baixa', motivoComplexidade: lowReason };
}

const data = JSON.parse(await fs.readFile(exportPath, 'utf8'));
const now = new Date().toISOString();

data.posts = data.posts.map((post) => {
  const currentPath = currentPosts.get(post.slug) ?? null;
  const published = Boolean(currentPath);
  return {
    ...post,
    migration: {
      publicado: published ? 'sim' : 'nao',
      currentBlogPath: currentPath,
      incluirNoBacklog: published ? 'nao' : 'sim',
      ...classify(post.slug),
    },
  };
});

const byComplexity = data.posts.reduce((acc, post) => {
  const key = post.migration.complexidadeLayout;
  acc[key] = (acc[key] ?? 0) + 1;
  return acc;
}, {});
const unpublishedByComplexity = data.posts.filter((post) => post.migration.publicado === 'nao').reduce((acc, post) => {
  const key = post.migration.complexidadeLayout;
  acc[key] = (acc[key] ?? 0) + 1;
  return acc;
}, {});

data.migrationSummary = {
  classifiedAt: now,
  totalPosts: data.posts.length,
  publishedPosts: data.posts.filter((post) => post.migration.publicado === 'sim').length,
  backlogPosts: data.posts.filter((post) => post.migration.incluirNoBacklog === 'sim').length,
  byComplexity,
  backlogByComplexity: unpublishedByComplexity,
  notes: [
    'Publicado sim foi marcado por cruzamento com pastas existentes em blog/.',
    'O post antigo de acessibilidade em eventos foi cruzado com o slug atual blog/garantir-libras-sem-improviso/.',
    'Complexidade alta indica pagina evergreen, explicativa, comercial ou com maior potencial SEO.',
    'Complexidade baixa indica noticia/caso pontual que pode usar layout editorial mais simples.',
  ],
};

await fs.writeFile(exportPath, `${JSON.stringify(data, null, 2)}\n`, 'utf8');
process.stdout.write(`Classified ${data.posts.length} posts in ${exportPath}\n`);
process.stdout.write(`${JSON.stringify(data.migrationSummary, null, 2)}\n`);
