<?php
/**
 * Template Name: Blog LIBRAS.SE
 * Description: Homepage do blog com posts em destaque, filtro por tipo editorial e mais lidos.
 */
get_header(); ?>

<main id="blog-home" class="lbs-blog-home">

  <!-- ── HERO DO BLOG ─────────────────────────────────────────────────────── -->
  <section class="lbs-blog-hero rv" aria-label="Blog LIBRAS.SE">
    <div class="w">
      <div class="lbs-blog-hero__label lbl">Blog</div>
      <h1 class="lbs-blog-hero__title">Tudo sobre Libras, Inclusão e Acessibilidade</h1>
      <p class="lbs-blog-hero__sub">Conteúdo educacional, institucional e instrucional para a comunidade surda, intérpretes e profissionais de acessibilidade.</p>
      <div class="lbs-cat-nav" role="navigation" aria-label="Navegar por tipo de conteúdo">
        <a href="<?php echo esc_url( get_term_link( 'educacional', 'category' ) ); ?>" class="lbs-cat-pill lbs-cat-pill--educacional">
          <span aria-hidden="true">📚</span> Educacional
        </a>
        <a href="<?php echo esc_url( get_term_link( 'institucional', 'category' ) ); ?>" class="lbs-cat-pill lbs-cat-pill--institucional">
          <span aria-hidden="true">🏛️</span> Institucional
        </a>
        <a href="<?php echo esc_url( get_term_link( 'instrucional', 'category' ) ); ?>" class="lbs-cat-pill lbs-cat-pill--instrucional">
          <span aria-hidden="true">🎯</span> Instrucional
        </a>
      </div>
    </div>
  </section>

  <!-- ── POSTS EM DESTAQUE ────────────────────────────────────────────────── -->
  <?php
  $featured_ids = get_option( 'lbs_featured_post_ids', [] );
  if ( ! empty( $featured_ids ) ) :
    $featured_query = new WP_Query( [
      'post__in'            => $featured_ids,
      'posts_per_page'      => 3,
      'orderby'             => 'post__in',
      'post_status'         => 'publish',
      'ignore_sticky_posts' => true,
    ] );
    if ( $featured_query->have_posts() ) : ?>

  <section class="lbs-featured rv" aria-label="Posts em destaque">
    <div class="w">
      <div class="lbs-section-header">
        <span class="lbl">Em Destaque</span>
        <h2>Artigos Selecionados</h2>
      </div>
      <div class="lbs-featured__grid">
        <?php $pos = 0; while ( $featured_query->have_posts() ) : $featured_query->the_post(); $pos++; ?>
        <article class="lbs-card lbs-card--featured <?php echo $pos === 1 ? 'lbs-card--hero' : 'lbs-card--secondary'; ?> glass rv d<?php echo $pos; ?>"
                 data-type="<?php echo esc_attr( get_post_meta( get_the_ID(), '_lbs_editorial_type', true ) ); ?>">
          <?php if ( has_post_thumbnail() ) : ?>
          <figure class="lbs-card__image">
            <?php the_post_thumbnail( $pos === 1 ? 'large' : 'medium_large', [
              'alt'     => esc_attr( get_the_title() ),
              'loading' => $pos === 1 ? 'eager' : 'lazy',
            ] ); ?>
          </figure>
          <?php endif; ?>
          <div class="lbs-card__body">
            <?php
            $editorial = get_post_meta( get_the_ID(), '_lbs_editorial_type', true );
            if ( $editorial ) : ?>
            <span class="lbs-card__badge lbs-card__badge--<?php echo esc_attr( $editorial ); ?>"><?php echo esc_html( ucfirst( $editorial ) ); ?></span>
            <?php endif; ?>
            <h3 class="lbs-card__title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
            <p class="lbs-card__excerpt"><?php echo esc_html( wp_trim_words( get_the_excerpt(), 20 ) ); ?></p>
            <div class="lbs-card__meta">
              <time datetime="<?php echo esc_attr( get_the_date( 'c' ) ); ?>"><?php echo esc_html( get_the_date( 'd M Y' ) ); ?></time>
              <span class="lbs-card__reading"><?php echo esc_html( lbs_reading_time( get_the_ID() ) ); ?> min de leitura</span>
            </div>
          </div>
        </article>
        <?php endwhile; wp_reset_postdata(); ?>
      </div>
    </div>
  </section>

    <?php endif; wp_reset_postdata();
  endif; ?>

  <!-- ── TODOS OS POSTS (FILTRÁVEIS) ──────────────────────────────────────── -->
  <?php
  $all_query = new WP_Query( [
    'posts_per_page'      => 12,
    'post_status'         => 'publish',
    'orderby'             => 'date',
    'order'               => 'DESC',
    'ignore_sticky_posts' => true,
  ] );
  if ( $all_query->have_posts() ) : ?>

  <section class="lbs-all-posts rv" aria-label="Todos os artigos">
    <div class="w">
      <div class="lbs-section-header">
        <span class="lbl">Artigos</span>
        <h2>Explorar Conteúdo</h2>
      </div>

      <!-- Filtro por tipo editorial -->
      <div class="lbs-filter-bar" role="tablist" aria-label="Filtrar artigos por tipo">
        <button class="lbs-filter-btn active" data-filter="all" role="tab" aria-selected="true">Todos</button>
        <button class="lbs-filter-btn" data-filter="educacional" role="tab" aria-selected="false">📚 Educacional</button>
        <button class="lbs-filter-btn" data-filter="institucional" role="tab" aria-selected="false">🏛️ Institucional</button>
        <button class="lbs-filter-btn" data-filter="instrucional" role="tab" aria-selected="false">🎯 Instrucional</button>
      </div>

      <div class="lbs-posts-grid" id="lbs-posts-grid" role="tabpanel" aria-live="polite">
        <?php $i = 0; while ( $all_query->have_posts() ) : $all_query->the_post(); $i++; ?>
        <?php $editorial = get_post_meta( get_the_ID(), '_lbs_editorial_type', true ) ?: 'geral'; ?>
        <article class="lbs-card glass rv d<?php echo min( $i, 6 ); ?>"
                 data-type="<?php echo esc_attr( $editorial ); ?>">
          <?php if ( has_post_thumbnail() ) : ?>
          <figure class="lbs-card__image lbs-card__image--small">
            <?php the_post_thumbnail( 'medium', [ 'alt' => esc_attr( get_the_title() ), 'loading' => 'lazy' ] ); ?>
          </figure>
          <?php endif; ?>
          <div class="lbs-card__body">
            <span class="lbs-card__badge lbs-card__badge--<?php echo esc_attr( $editorial ); ?>"><?php echo esc_html( ucfirst( $editorial ) ); ?></span>
            <h3 class="lbs-card__title lbs-card__title--sm"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
            <p class="lbs-card__excerpt lbs-card__excerpt--sm"><?php echo esc_html( wp_trim_words( get_the_excerpt(), 14 ) ); ?></p>
            <div class="lbs-card__meta">
              <time datetime="<?php echo esc_attr( get_the_date( 'c' ) ); ?>"><?php echo esc_html( get_the_date( 'd M Y' ) ); ?></time>
            </div>
          </div>
        </article>
        <?php endwhile; wp_reset_postdata(); ?>
      </div>
    </div>
  </section>

  <?php endif; ?>

  <!-- ── MAIS LIDOS ──────────────────────────────────────────────────────── -->
  <?php
  $popular_query = new WP_Query( [
    'posts_per_page' => 5,
    'post_status'    => 'publish',
    'meta_key'       => '_lbs_view_count',
    'orderby'        => 'meta_value_num',
    'order'          => 'DESC',
  ] );
  if ( $popular_query->have_posts() ) : ?>

  <section class="lbs-popular rv" aria-label="Artigos mais lidos">
    <div class="w">
      <div class="lbs-section-header">
        <span class="lbl">Popular</span>
        <h2>Mais Lidos</h2>
      </div>
      <ol class="lbs-popular__list" role="list">
        <?php $rank = 0; while ( $popular_query->have_posts() ) : $popular_query->the_post(); $rank++; ?>
        <li class="lbs-popular__item glass rv d<?php echo $rank; ?>">
          <span class="lbs-popular__rank" aria-hidden="true"><?php echo $rank; ?></span>
          <div class="lbs-popular__content">
            <h3 class="lbs-popular__title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
            <div class="lbs-popular__meta">
              <?php $views = (int) get_post_meta( get_the_ID(), '_lbs_view_count', true ); ?>
              <span><?php echo esc_html( number_format( $views ) ); ?> leituras</span>
              <time datetime="<?php echo esc_attr( get_the_date( 'c' ) ); ?>"><?php echo esc_html( get_the_date( 'd M Y' ) ); ?></time>
            </div>
          </div>
        </li>
        <?php endwhile; wp_reset_postdata(); ?>
      </ol>
    </div>
  </section>

  <?php endif; ?>

  <!-- ── NAVEGAR POR CATEGORIA ────────────────────────────────────────────── -->
  <section class="lbs-cat-section rv" aria-label="Navegar por categoria">
    <div class="w">
      <div class="lbs-section-header">
        <span class="lbl">Categorias</span>
        <h2>Explore por Tema</h2>
      </div>
      <div class="lbs-cat-grid">
        <?php
        $cat_data = [
          [ 'slug' => 'educacional',   'icon' => '📚', 'desc' => 'Aprenda Libras, cultura surda e linguística' ],
          [ 'slug' => 'institucional', 'icon' => '🏛️', 'desc' => 'Notícias, eventos e comunicados oficiais' ],
          [ 'slug' => 'instrucional',  'icon' => '🎯', 'desc' => 'Tutoriais, guias práticos e how-tos' ],
        ];
        foreach ( $cat_data as $cat ) :
          $term = get_term_by( 'slug', $cat['slug'], 'category' );
          if ( ! $term ) continue;
          $count = $term->count;
        ?>
        <a href="<?php echo esc_url( get_category_link( $term->term_id ) ); ?>"
           class="lbs-cat-card lbs-cat-card--<?php echo esc_attr( $cat['slug'] ); ?> glass rv">
          <span class="lbs-cat-card__icon" aria-hidden="true"><?php echo esc_html( $cat['icon'] ); ?></span>
          <span class="lbs-cat-card__name"><?php echo esc_html( $term->name ); ?></span>
          <span class="lbs-cat-card__desc"><?php echo esc_html( $cat['desc'] ); ?></span>
          <span class="lbs-cat-card__count"><?php echo esc_html( $count ); ?> artigos</span>
        </a>
        <?php endforeach; ?>
      </div>
    </div>
  </section>

  <!-- ── CTA FINAL ────────────────────────────────────────────────────────── -->
  <section class="lbs-blog-cta rv" aria-label="Conheça a plataforma LIBRAS.SE">
    <div class="w wc">
      <div class="lbs-blog-cta__inner">
        <span class="lbs-blog-cta__icon" aria-hidden="true">🤟</span>
        <h2 class="lbs-blog-cta__title">Traduza seu vídeo para Libras</h2>
        <p class="lbs-blog-cta__body">Intérpretes humanos certificados. Entrega em até 1 hora. Conheça a plataforma que já atendeu Natura, Nubank e Salesforce.</p>
        <div class="lbs-blog-cta__actions">
          <a href="<?php echo esc_url( home_url( '/' ) ); ?>" class="btn bgl" aria-label="Conheça a plataforma LIBRAS.SE">Conhecer a Plataforma</a>
          <a href="https://wa.me/5548996367511?text=Oi,%20quero%20saber%20mais%20sobre%20tradu%C3%A7%C3%A3o%20em%20Libras"
             class="btn bw"
             target="_blank"
             rel="noopener noreferrer"
             aria-label="Fale com a equipe LIBRAS.SE no WhatsApp">WhatsApp</a>
        </div>
      </div>
    </div>
  </section>

</main>

<script>
(function() {
  var filterBtns = document.querySelectorAll('.lbs-filter-btn');
  var cards      = document.querySelectorAll('#lbs-posts-grid .lbs-card');

  filterBtns.forEach(function(btn) {
    btn.addEventListener('click', function() {
      var filter = btn.getAttribute('data-filter');

      filterBtns.forEach(function(b) {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');

      cards.forEach(function(card) {
        if (filter === 'all' || card.getAttribute('data-type') === filter) {
          card.hidden = false;
        } else {
          card.hidden = true;
        }
      });
    });
  });
})();
</script>

<?php get_footer(); ?>
