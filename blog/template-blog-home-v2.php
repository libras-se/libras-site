<?php
/**
 * Template Name: Blog LIBRAS.SE v2
 * Template Post Type: page
 *
 * Homepage do blog — usa design system do librase-blog-template.md
 * (Bricolage Grotesque + Lora, paleta teal-dark)
 */
if ( ! defined( 'ABSPATH' ) ) exit;

// Opções configuráveis via WP (filtráveis por hooks)
$featured_ids   = get_option( 'lbs_featured_post_ids', [] );
$posts_per_page = 12;

// Post em destaque principal
$hero_post = null;
if ( ! empty( $featured_ids ) ) {
    $hero_post = get_post( (int) $featured_ids[0] );
}
if ( ! $hero_post ) {
    $hero_q = new WP_Query( [ 'posts_per_page' => 1, 'post_status' => 'publish', 'ignore_sticky_posts' => true ] );
    $hero_post = $hero_q->have_posts() ? $hero_q->posts[0] : null;
}

// Posts em destaque (2 secundários)
$secondary_featured = [];
if ( count( $featured_ids ) > 1 ) {
    foreach ( array_slice( $featured_ids, 1, 2 ) as $fid ) {
        $p = get_post( (int) $fid );
        if ( $p ) $secondary_featured[] = $p;
    }
}
if ( count( $secondary_featured ) < 2 ) {
    $excl = $hero_post ? [ $hero_post->ID ] : [];
    foreach ( $secondary_featured as $p ) $excl[] = $p->ID;
    $sf_q = new WP_Query( [
        'posts_per_page'      => 2 - count( $secondary_featured ),
        'post_status'         => 'publish',
        'ignore_sticky_posts' => true,
        'post__not_in'        => $excl,
    ] );
    $secondary_featured = array_merge( $secondary_featured, $sf_q->posts );
}

// Todos os posts (com paginação)
$paged    = max( 1, get_query_var( 'paged' ) );
$excl_all = $hero_post ? [ $hero_post->ID ] : [];
foreach ( $secondary_featured as $p ) $excl_all[] = $p->ID;

$all_posts = new WP_Query( [
    'posts_per_page'      => $posts_per_page,
    'post_status'         => 'publish',
    'paged'               => $paged,
    'ignore_sticky_posts' => true,
    'post__not_in'        => $excl_all,
    'orderby'             => 'date',
    'order'               => 'DESC',
] );

// Posts mais lidos
$popular_posts = new WP_Query( [
    'posts_per_page' => 4,
    'post_status'    => 'publish',
    'orderby'        => 'meta_value_num',
    'meta_key'       => '_lbs_view_count',
    'order'          => 'DESC',
] );

// Categorias editoriais
$editorial_cats = get_terms( [
    'taxonomy'   => 'category',
    'slug__in'   => [ 'educacional', 'institucional', 'instrucional' ],
    'hide_empty' => false,
] );

// Helper: tipo editorial de um post
function lbs_home_editorial_type( int $post_id ): string {
    $t = get_post_meta( $post_id, '_lbs_editorial_type', true );
    return $t ?: 'educacional';
}

function lbs_home_editorial_label( string $type ): string {
    return match ( $type ) {
        'educacional'   => 'Educacional',
        'institucional' => 'Institucional',
        'instrucional'  => 'Instrucional',
        default         => ucfirst( $type ),
    };
}

function lbs_home_card_html( WP_Post $post, string $size = 'md' ): string {
    $type    = lbs_home_editorial_type( $post->ID );
    $label   = lbs_home_editorial_label( $type );
    $thumb   = get_the_post_thumbnail_url( $post->ID, $size === 'lg' ? 'large' : 'medium_large' );
    $url     = get_permalink( $post->ID );
    $date    = get_the_date( 'd M Y', $post->ID );
    $excerpt = wp_trim_words( get_the_excerpt( $post->ID ), 18, '…' );
    $read    = function_exists( 'lbs_reading_time' ) ? lbs_reading_time( $post->ID ) : 3;
    $title   = esc_html( get_the_title( $post->ID ) );
    $alt     = esc_attr( get_the_title( $post->ID ) );

    $thumb_html = $thumb
        ? '<img src="' . esc_url( $thumb ) . '" alt="' . $alt . '" loading="lazy">'
        : '<div class="lbs2-card__thumb-placeholder" aria-hidden="true"><span>🤟</span></div>';

    return '
    <article class="lbs2-card lbs2-card--' . esc_attr( $size ) . '" data-type="' . esc_attr( $type ) . '" itemscope itemtype="https://schema.org/BlogPosting">
      <a href="' . esc_url( $url ) . '" class="lbs2-card__thumb" aria-label="' . $alt . '">
        ' . $thumb_html . '
        <span class="lbs2-card__badge">' . esc_html( $label ) . '</span>
      </a>
      <div class="lbs2-card__body">
        <div class="lbs2-card__meta">
          <time datetime="' . esc_attr( get_the_date( 'c', $post->ID ) ) . '" itemprop="datePublished">' . esc_html( $date ) . '</time>
          <span class="lbs2-card__dot" aria-hidden="true"></span>
          <span>' . $read . ' min</span>
        </div>
        <h3 class="lbs2-card__title" itemprop="headline"><a href="' . esc_url( $url ) . '">' . $title . '</a></h3>
        <p class="lbs2-card__excerpt" itemprop="description">' . esc_html( $excerpt ) . '</p>
        <a href="' . esc_url( $url ) . '" class="lbs2-card__read" aria-label="Ler: ' . $alt . '">Ler artigo →</a>
      </div>
    </article>';
}

get_header();
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title><?php wp_title( '|', true, 'right' ); echo esc_html( get_bloginfo( 'name' ) ); ?> Blog</title>
  <?php wp_head(); ?>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700;12..96,800&family=Lora:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">

  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Blog",
    "name": "Blog LIBRAS.SE",
    "url": "<?php echo esc_js( get_permalink() ); ?>",
    "description": "Artigos sobre Libras, acessibilidade audiovisual, interpretação e inclusão da comunidade surda.",
    "publisher": {
      "@type": "Organization",
      "name": "LIBRAS.SE",
      "url": "https://libras.se",
      "logo": {
        "@type": "ImageObject",
        "url": "<?php echo esc_js( get_site_icon_url( 512 ) ); ?>"
      }
    },
    "inLanguage": "pt-BR"
  }
  </script>

  <style>
    /* ---- Design System Blog v2 ---- */
    :root {
      --teal-dark:   #1e6e6e;
      --teal-mid:    #2a9090;
      --teal-light:  #48bfb2;
      --teal-pale:   #a8e6df;
      --teal-bg:     #f0fafa;
      --ink:         #0f2a2a;
      --ink-soft:    #2d4f4f;
      --orange:      #f4892a;
      --orange-soft: #fef3e8;
      --white:       #ffffff;
      --cream:       #f8fdfd;
      --grey-light:  #e8f4f4;
      --radius-card: 20px;
      --shadow-card: 0 2px 16px rgba(30,110,110,.09), 0 1px 4px rgba(30,110,110,.05);
      --shadow-hover: 0 8px 32px rgba(30,110,110,.16), 0 2px 8px rgba(30,110,110,.08);
      --transition:  0.28s cubic-bezier(.4,0,.2,1);
    }

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Bricolage Grotesque', system-ui, sans-serif;
      background: var(--cream);
      color: var(--ink);
      -webkit-font-smoothing: antialiased;
    }

    a { color: inherit; text-decoration: none; }
    img { display: block; width: 100%; height: 100%; object-fit: cover; }

    .lbs2-container {
      max-width: 1160px;
      margin: 0 auto;
      padding: 0 32px;
    }
    @media (max-width: 700px) { .lbs2-container { padding: 0 18px; } }

    /* ---- Progress bar ---- */
    #lbs2-progress {
      position: fixed;
      top: 0; left: 0;
      height: 3px;
      width: 0%;
      background: linear-gradient(90deg, var(--teal-dark), var(--teal-light));
      z-index: 9999;
      transition: width .1s linear;
    }

    /* ---- Nav ---- */
    .lbs2-nav {
      position: sticky;
      top: 0;
      z-index: 100;
      padding: 16px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      backdrop-filter: blur(16px);
      background: rgba(240,250,250,.88);
      border-bottom: 1px solid rgba(42,144,144,.12);
      transition: box-shadow var(--transition);
    }
    .lbs2-nav--scrolled { box-shadow: 0 2px 24px rgba(30,110,110,.10); }
    .lbs2-nav__logo {
      font-weight: 800;
      font-size: 1.1rem;
      color: var(--teal-dark);
      letter-spacing: -.02em;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .lbs2-nav__logo-icon {
      width: 28px; height: 28px;
      background: linear-gradient(135deg, var(--teal-mid), var(--teal-light));
      border-radius: 50%;
      display: grid;
      place-items: center;
      font-size: 13px;
    }
    .lbs2-nav__links {
      display: flex;
      align-items: center;
      gap: 22px;
    }
    .lbs2-nav__link {
      font-size: .78rem;
      font-weight: 600;
      color: var(--ink-soft);
      letter-spacing: .02em;
      transition: color var(--transition);
    }
    .lbs2-nav__link:hover, .lbs2-nav__link[aria-current="page"] { color: var(--teal-dark); }
    .lbs2-nav__cta {
      font-size: .78rem;
      font-weight: 700;
      background: var(--teal-dark);
      color: var(--white);
      padding: 8px 18px;
      border-radius: 100px;
      transition: background var(--transition), transform var(--transition);
      white-space: nowrap;
    }
    .lbs2-nav__cta:hover { background: var(--teal-mid); transform: translateY(-1px); }
    @media (max-width: 768px) {
      .lbs2-nav { padding: 14px 18px; }
      .lbs2-nav__links { display: none; }
    }

    /* ---- Blog Hero ---- */
    .lbs2-blog-hero {
      padding: 72px 0 56px;
      background: linear-gradient(155deg, #0d3d3d 0%, #1e6e6e 40%, #2a9090 70%, #48bfb2 100%);
      position: relative;
      overflow: hidden;
    }
    .lbs2-blog-hero::before {
      content: '';
      position: absolute; inset: 0;
      background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    }
    .lbs2-blog-hero__content {
      position: relative;
      text-align: center;
      max-width: 640px;
      margin: 0 auto;
      padding: 0 32px;
    }
    .lbs2-blog-hero__kicker {
      display: inline-block;
      font-size: .7rem;
      font-weight: 700;
      letter-spacing: .14em;
      text-transform: uppercase;
      color: var(--teal-pale);
      margin-bottom: 16px;
      padding: 5px 14px;
      border: 1px solid rgba(168,230,223,.3);
      border-radius: 100px;
    }
    .lbs2-blog-hero__title {
      font-size: clamp(2rem, 4.5vw, 3rem);
      font-weight: 800;
      color: var(--white);
      letter-spacing: -.03em;
      line-height: 1.15;
      margin-bottom: 16px;
    }
    .lbs2-blog-hero__title em {
      font-style: normal;
      color: var(--teal-pale);
    }
    .lbs2-blog-hero__desc {
      font-family: 'Lora', serif;
      font-style: italic;
      font-size: 1.05rem;
      color: rgba(255,255,255,.78);
      line-height: 1.6;
      margin-bottom: 28px;
    }
    .lbs2-blog-hero__stats {
      display: flex;
      justify-content: center;
      gap: 28px;
      flex-wrap: wrap;
    }
    .lbs2-blog-hero__stat {
      text-align: center;
    }
    .lbs2-blog-hero__stat strong {
      display: block;
      font-size: 1.4rem;
      font-weight: 800;
      color: var(--white);
    }
    .lbs2-blog-hero__stat span {
      font-size: .72rem;
      color: var(--teal-pale);
      letter-spacing: .06em;
      text-transform: uppercase;
    }

    /* ---- Search bar ---- */
    .lbs2-search {
      padding: 32px 0;
      background: var(--white);
      border-bottom: 1px solid var(--grey-light);
    }
    .lbs2-search__form {
      display: flex;
      max-width: 540px;
      margin: 0 auto;
      gap: 10px;
    }
    .lbs2-search__input {
      flex: 1;
      font-family: 'Bricolage Grotesque', sans-serif;
      font-size: .9rem;
      padding: 11px 18px;
      border: 1.5px solid var(--grey-light);
      border-radius: 100px;
      background: var(--cream);
      color: var(--ink);
      outline: none;
      transition: border-color var(--transition);
    }
    .lbs2-search__input:focus { border-color: var(--teal-mid); }
    .lbs2-search__btn {
      font-family: 'Bricolage Grotesque', sans-serif;
      font-size: .82rem;
      font-weight: 700;
      padding: 11px 20px;
      background: var(--teal-dark);
      color: var(--white);
      border: none;
      border-radius: 100px;
      cursor: pointer;
      transition: background var(--transition);
    }
    .lbs2-search__btn:hover { background: var(--teal-mid); }

    /* ---- Section headers ---- */
    .lbs2-section-head {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 28px;
      padding-bottom: 14px;
      border-bottom: 2px solid var(--grey-light);
    }
    .lbs2-section-head__title {
      font-size: 1.1rem;
      font-weight: 800;
      color: var(--ink);
      letter-spacing: -.02em;
    }
    .lbs2-section-head__title em {
      font-style: normal;
      color: var(--teal-dark);
    }
    .lbs2-section-head__link {
      font-size: .78rem;
      font-weight: 600;
      color: var(--teal-mid);
      transition: color var(--transition);
    }
    .lbs2-section-head__link:hover { color: var(--teal-dark); }

    /* ---- Featured block ---- */
    .lbs2-featured { padding: 56px 0 48px; }
    .lbs2-featured__grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-template-rows: auto auto;
      gap: 20px;
    }
    .lbs2-featured__hero { grid-column: 1; grid-row: 1 / 3; }
    .lbs2-featured__secondary { grid-column: 2; }
    @media (max-width: 900px) {
      .lbs2-featured__grid { grid-template-columns: 1fr; }
      .lbs2-featured__hero { grid-row: auto; }
      .lbs2-featured__secondary { grid-column: 1; }
    }

    /* ---- Card ---- */
    .lbs2-card {
      background: var(--white);
      border-radius: var(--radius-card);
      overflow: hidden;
      box-shadow: var(--shadow-card);
      transition: box-shadow var(--transition), transform var(--transition);
      height: 100%;
      display: flex;
      flex-direction: column;
    }
    .lbs2-card:hover { box-shadow: var(--shadow-hover); transform: translateY(-3px); }

    .lbs2-card__thumb {
      display: block;
      position: relative;
      overflow: hidden;
      background: var(--grey-light);
    }
    .lbs2-card--lg .lbs2-card__thumb { aspect-ratio: 16/9; }
    .lbs2-card--md .lbs2-card__thumb { aspect-ratio: 3/2; }
    .lbs2-card--sm .lbs2-card__thumb { aspect-ratio: 4/3; }

    .lbs2-card__thumb img { transition: transform .4s ease; }
    .lbs2-card:hover .lbs2-card__thumb img { transform: scale(1.04); }

    .lbs2-card__thumb-placeholder {
      width: 100%; height: 100%;
      min-height: 160px;
      display: grid;
      place-items: center;
      background: linear-gradient(135deg, var(--grey-light), var(--teal-bg));
    }
    .lbs2-card__thumb-placeholder span { font-size: 2.5rem; opacity: .5; }

    .lbs2-card__badge {
      position: absolute;
      top: 12px; left: 12px;
      font-size: .65rem;
      font-weight: 700;
      letter-spacing: .08em;
      text-transform: uppercase;
      background: var(--teal-dark);
      color: var(--white);
      padding: 4px 10px;
      border-radius: 100px;
    }
    .lbs2-card__body {
      padding: 20px;
      display: flex;
      flex-direction: column;
      flex: 1;
    }
    .lbs2-card--lg .lbs2-card__body { padding: 24px 28px; }

    .lbs2-card__meta {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: .72rem;
      color: var(--ink-soft);
      opacity: .7;
      margin-bottom: 10px;
    }
    .lbs2-card__dot {
      width: 3px; height: 3px;
      border-radius: 50%;
      background: currentColor;
    }
    .lbs2-card__title {
      font-size: 1rem;
      font-weight: 700;
      color: var(--ink);
      line-height: 1.35;
      margin-bottom: 10px;
      letter-spacing: -.015em;
    }
    .lbs2-card--lg .lbs2-card__title { font-size: 1.3rem; margin-bottom: 12px; }
    .lbs2-card__title a { transition: color var(--transition); }
    .lbs2-card__title a:hover { color: var(--teal-dark); }

    .lbs2-card__excerpt {
      font-family: 'Lora', serif;
      font-size: .875rem;
      color: var(--ink-soft);
      line-height: 1.65;
      flex: 1;
      margin-bottom: 16px;
    }
    .lbs2-card__read {
      font-size: .78rem;
      font-weight: 700;
      color: var(--teal-dark);
      transition: gap var(--transition), color var(--transition);
      align-self: flex-start;
    }
    .lbs2-card__read:hover { color: var(--teal-mid); }

    /* ---- Filter bar ---- */
    .lbs2-filter { padding: 48px 0 36px; }
    .lbs2-filter__bar {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 32px;
    }
    .lbs2-filter__label {
      font-size: .72rem;
      font-weight: 700;
      letter-spacing: .1em;
      text-transform: uppercase;
      color: var(--ink-soft);
      opacity: .6;
      margin-right: 4px;
    }
    .lbs2-filter__btn {
      font-family: 'Bricolage Grotesque', sans-serif;
      font-size: .78rem;
      font-weight: 600;
      padding: 7px 16px;
      border-radius: 100px;
      border: 1.5px solid var(--grey-light);
      background: var(--white);
      color: var(--ink-soft);
      cursor: pointer;
      transition: all var(--transition);
    }
    .lbs2-filter__btn:hover { border-color: var(--teal-light); color: var(--teal-dark); }
    .lbs2-filter__btn[aria-selected="true"] {
      background: var(--teal-dark);
      border-color: var(--teal-dark);
      color: var(--white);
    }

    /* ---- Posts grid ---- */
    .lbs2-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 24px;
    }
    @media (max-width: 1000px) { .lbs2-grid { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 600px)  { .lbs2-grid { grid-template-columns: 1fr; } }

    .lbs2-grid__item { opacity: 1; transition: opacity .3s, transform .3s; }
    .lbs2-grid__item--hidden { display: none; }

    /* ---- Popular ---- */
    .lbs2-popular {
      padding: 56px 0;
      background: var(--teal-bg);
      border-top: 1px solid var(--grey-light);
      border-bottom: 1px solid var(--grey-light);
    }
    .lbs2-popular__grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;
    }
    @media (max-width: 900px)  { .lbs2-popular__grid { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 540px)  { .lbs2-popular__grid { grid-template-columns: 1fr; } }

    .lbs2-popular-card {
      background: var(--white);
      border-radius: 16px;
      padding: 20px;
      display: flex;
      gap: 14px;
      align-items: flex-start;
      box-shadow: var(--shadow-card);
      transition: box-shadow var(--transition), transform var(--transition);
    }
    .lbs2-popular-card:hover { box-shadow: var(--shadow-hover); transform: translateY(-2px); }
    .lbs2-popular-card__rank {
      font-size: 1.5rem;
      font-weight: 800;
      color: var(--teal-pale);
      letter-spacing: -.04em;
      line-height: 1;
      flex-shrink: 0;
      min-width: 28px;
    }
    .lbs2-popular-card__title {
      font-size: .88rem;
      font-weight: 700;
      color: var(--ink);
      line-height: 1.4;
      letter-spacing: -.01em;
    }
    .lbs2-popular-card__title a { transition: color var(--transition); }
    .lbs2-popular-card__title a:hover { color: var(--teal-dark); }
    .lbs2-popular-card__views {
      font-size: .7rem;
      color: var(--ink-soft);
      opacity: .6;
      margin-top: 6px;
    }

    /* ---- Categories ---- */
    .lbs2-categories { padding: 56px 0; }
    .lbs2-cat-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
    }
    @media (max-width: 700px) { .lbs2-cat-grid { grid-template-columns: 1fr; } }

    .lbs2-cat-card {
      background: var(--white);
      border-radius: 20px;
      padding: 28px 24px;
      border: 1.5px solid var(--grey-light);
      transition: border-color var(--transition), box-shadow var(--transition), transform var(--transition);
      cursor: pointer;
    }
    .lbs2-cat-card:hover {
      border-color: var(--teal-light);
      box-shadow: 0 4px 24px rgba(30,110,110,.10);
      transform: translateY(-2px);
    }
    .lbs2-cat-card__icon {
      font-size: 2rem;
      margin-bottom: 12px;
      display: block;
    }
    .lbs2-cat-card__name {
      font-size: 1.05rem;
      font-weight: 800;
      color: var(--ink);
      margin-bottom: 6px;
      letter-spacing: -.02em;
    }
    .lbs2-cat-card__desc {
      font-size: .82rem;
      font-family: 'Lora', serif;
      color: var(--ink-soft);
      line-height: 1.55;
      margin-bottom: 14px;
    }
    .lbs2-cat-card__count {
      font-size: .7rem;
      font-weight: 700;
      color: var(--teal-mid);
      letter-spacing: .06em;
      text-transform: uppercase;
    }

    /* ---- Newsletter ---- */
    .lbs2-newsletter {
      padding: 64px 0;
      background: linear-gradient(135deg, #0d3d3d 0%, #1e6e6e 60%, #2a9090 100%);
      text-align: center;
    }
    .lbs2-newsletter__kicker {
      font-size: .7rem;
      font-weight: 700;
      letter-spacing: .14em;
      text-transform: uppercase;
      color: var(--teal-pale);
      margin-bottom: 12px;
    }
    .lbs2-newsletter__title {
      font-size: clamp(1.4rem, 3vw, 2rem);
      font-weight: 800;
      color: var(--white);
      letter-spacing: -.03em;
      margin-bottom: 10px;
    }
    .lbs2-newsletter__desc {
      font-family: 'Lora', serif;
      font-style: italic;
      color: rgba(255,255,255,.72);
      font-size: .95rem;
      margin-bottom: 28px;
      max-width: 440px;
      margin-left: auto; margin-right: auto;
    }
    <?php echo get_search_form( [ 'echo' => false ] ) ? '' : '' ?>

    /* ---- Pagination ---- */
    .lbs2-pagination {
      display: flex;
      justify-content: center;
      gap: 6px;
      padding: 40px 0 56px;
    }
    .lbs2-pagination a, .lbs2-pagination span {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 38px; height: 38px;
      border-radius: 10px;
      font-size: .84rem;
      font-weight: 600;
      border: 1.5px solid var(--grey-light);
      color: var(--ink-soft);
      transition: all var(--transition);
    }
    .lbs2-pagination a:hover { border-color: var(--teal-light); color: var(--teal-dark); }
    .lbs2-pagination .current {
      background: var(--teal-dark);
      border-color: var(--teal-dark);
      color: var(--white);
    }

    /* ---- Footer ---- */
    .lbs2-footer {
      background: var(--ink);
      color: rgba(255,255,255,.7);
      padding: 56px 0 32px;
    }
    .lbs2-footer__grid {
      display: grid;
      grid-template-columns: 2fr 1fr 1fr;
      gap: 48px;
      padding-bottom: 40px;
      border-bottom: 1px solid rgba(255,255,255,.08);
    }
    @media (max-width: 768px) { .lbs2-footer__grid { grid-template-columns: 1fr; gap: 32px; } }
    .lbs2-footer__brand-name {
      font-size: 1.1rem;
      font-weight: 800;
      color: var(--white);
      letter-spacing: -.02em;
      margin-bottom: 10px;
    }
    .lbs2-footer__brand-desc {
      font-family: 'Lora', serif;
      font-style: italic;
      font-size: .88rem;
      line-height: 1.6;
      margin-bottom: 20px;
    }
    .lbs2-footer__social {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    .lbs2-footer__social a {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 34px; height: 34px;
      border-radius: 8px;
      background: rgba(255,255,255,.08);
      font-size: .8rem;
      transition: background var(--transition);
    }
    .lbs2-footer__social a:hover { background: var(--teal-dark); }
    .lbs2-footer__col-title {
      font-size: .72rem;
      font-weight: 700;
      letter-spacing: .12em;
      text-transform: uppercase;
      color: rgba(255,255,255,.4);
      margin-bottom: 14px;
    }
    .lbs2-footer__links { list-style: none; }
    .lbs2-footer__links li { margin-bottom: 8px; }
    .lbs2-footer__links a {
      font-size: .84rem;
      transition: color var(--transition);
    }
    .lbs2-footer__links a:hover { color: var(--teal-pale); }
    .lbs2-footer__bottom {
      padding-top: 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }
    .lbs2-footer__copy { font-size: .78rem; }
    .lbs2-footer__legal {
      display: flex;
      gap: 16px;
      font-size: .78rem;
    }
    .lbs2-footer__legal a { transition: color var(--transition); }
    .lbs2-footer__legal a:hover { color: var(--teal-pale); }

    /* ---- Reveal on scroll ---- */
    .rv {
      opacity: 0;
      transform: translateY(20px);
      transition: opacity .7s ease, transform .7s ease;
    }
    .rv.on { opacity: 1; transform: none; }
    .rv.d1 { transition-delay: .05s; }
    .rv.d2 { transition-delay: .12s; }
    .rv.d3 { transition-delay: .19s; }
    .rv.d4 { transition-delay: .26s; }

    @media (prefers-reduced-motion: reduce) {
      .rv { opacity: 1; transform: none; transition: none; }
      * { transition: none !important; animation: none !important; }
    }
  </style>
</head>
<body>
<div id="lbs2-progress" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-label="Progresso de leitura"></div>

<!-- Nav -->
<nav class="lbs2-nav" id="lbs2-nav" role="navigation" aria-label="Navegação principal do blog">
  <a href="https://libras.se" class="lbs2-nav__logo">
    <span class="lbs2-nav__logo-icon" aria-hidden="true">🤟</span>
    LIBRAS.SE
  </a>
  <div class="lbs2-nav__links">
    <a href="<?php echo esc_url( get_permalink() ); ?>" class="lbs2-nav__link" aria-current="page">Blog</a>
    <a href="https://libras.se/blog/glossario" class="lbs2-nav__link">Glossário</a>
    <a href="https://libras.se/solucoes" class="lbs2-nav__link">Soluções</a>
    <a href="https://libras.se/portfolio" class="lbs2-nav__link">Portfólio</a>
  </div>
  <a href="https://huet.libras.se/" class="lbs2-nav__cta" target="_blank" rel="noopener noreferrer">
    Traduzir agora →
  </a>
</nav>

<!-- Blog Hero -->
<header class="lbs2-blog-hero" role="banner">
  <div class="lbs2-blog-hero__content">
    <div class="lbs2-blog-hero__kicker rv">Conteúdo & Inclusão</div>
    <h1 class="lbs2-blog-hero__title rv d1">
      Conhecimento sobre<br><em>Libras e Acessibilidade</em>
    </h1>
    <p class="lbs2-blog-hero__desc rv d2">
      Artigos educacionais, instrucionais e institucionais para quem quer entender e produzir conteúdo acessível.
    </p>
    <div class="lbs2-blog-hero__stats rv d3">
      <div class="lbs2-blog-hero__stat">
        <strong><?php echo esc_html( wp_count_posts()->publish ); ?></strong>
        <span>Artigos</span>
      </div>
      <div class="lbs2-blog-hero__stat">
        <strong>3</strong>
        <span>Categorias</span>
      </div>
      <div class="lbs2-blog-hero__stat">
        <strong>10.7M</strong>
        <span>Surdos no Brasil</span>
      </div>
    </div>
  </div>
</header>

<!-- Search -->
<section class="lbs2-search" aria-label="Buscar no blog">
  <form class="lbs2-search__form" role="search" action="<?php echo esc_url( home_url( '/' ) ); ?>">
    <input type="search" name="s" class="lbs2-search__input"
           placeholder="Buscar artigos sobre Libras, acessibilidade…"
           aria-label="Buscar no blog"
           value="<?php echo esc_attr( get_search_query() ); ?>">
    <button type="submit" class="lbs2-search__btn">Buscar</button>
  </form>
</section>

<!-- Featured Posts -->
<?php if ( $hero_post ) : ?>
<section class="lbs2-featured" aria-label="Posts em destaque">
  <div class="lbs2-container">
    <div class="lbs2-section-head">
      <h2 class="lbs2-section-head__title"><em>Em destaque</em></h2>
    </div>
    <div class="lbs2-featured__grid">
      <div class="lbs2-featured__hero rv">
        <?php echo lbs_home_card_html( $hero_post, 'lg' ); ?>
      </div>
      <?php foreach ( $secondary_featured as $i => $sfp ) : ?>
      <div class="lbs2-featured__secondary rv d<?php echo $i + 1; ?>">
        <?php echo lbs_home_card_html( $sfp, 'md' ); ?>
      </div>
      <?php endforeach; ?>
    </div>
  </div>
</section>
<?php endif; ?>

<!-- All Posts with Filter -->
<section class="lbs2-filter" id="posts" aria-label="Todos os artigos">
  <div class="lbs2-container">
    <div class="lbs2-section-head">
      <h2 class="lbs2-section-head__title">Todos os <em>artigos</em></h2>
      <span class="lbs2-section-head__link"><?php echo esc_html( $all_posts->found_posts ); ?> artigos</span>
    </div>

    <!-- Filter Bar -->
    <div class="lbs2-filter__bar" role="tablist" aria-label="Filtrar por tipo editorial">
      <span class="lbs2-filter__label" aria-hidden="true">Filtrar:</span>
      <button class="lbs2-filter__btn" role="tab" aria-selected="true" data-filter="all">Todos</button>
      <button class="lbs2-filter__btn" role="tab" aria-selected="false" data-filter="educacional">📚 Educacional</button>
      <button class="lbs2-filter__btn" role="tab" aria-selected="false" data-filter="institucional">🏛️ Institucional</button>
      <button class="lbs2-filter__btn" role="tab" aria-selected="false" data-filter="instrucional">🎯 Instrucional</button>
    </div>

    <!-- Grid -->
    <?php if ( $all_posts->have_posts() ) : ?>
    <div class="lbs2-grid" id="lbs2-posts-grid">
      <?php while ( $all_posts->have_posts() ) : $all_posts->the_post(); ?>
      <div class="lbs2-grid__item rv" data-type="<?php echo esc_attr( lbs_home_editorial_type( get_the_ID() ) ); ?>">
        <?php echo lbs_home_card_html( get_post(), 'sm' ); ?>
      </div>
      <?php endwhile; wp_reset_postdata(); ?>
    </div>

    <!-- Pagination -->
    <nav class="lbs2-pagination" aria-label="Navegação de páginas">
      <?php
      echo paginate_links( [
          'base'      => str_replace( 999999999, '%#%', esc_url( get_pagenum_link( 999999999 ) ) ),
          'format'    => '?paged=%#%',
          'current'   => $paged,
          'total'     => $all_posts->max_num_pages,
          'prev_text' => '←',
          'next_text' => '→',
          'type'      => 'list',
          'before_page_number' => '<span class="screen-reader-text">Página </span>',
      ] );
      ?>
    </nav>
    <?php else : ?>
    <p style="text-align:center; padding: 48px 0; color: var(--ink-soft); font-family: 'Lora', serif; font-style: italic;">
      Nenhum artigo encontrado. <a href="https://libras.se/blog" style="color: var(--teal-dark);">Ver todos os posts</a>.
    </p>
    <?php endif; ?>
  </div>
</section>

<!-- Popular Posts -->
<?php if ( $popular_posts->have_posts() ) : ?>
<section class="lbs2-popular" aria-label="Mais lidos">
  <div class="lbs2-container">
    <div class="lbs2-section-head">
      <h2 class="lbs2-section-head__title"><em>Mais lidos</em></h2>
      <a href="<?php echo esc_url( get_permalink() ); ?>" class="lbs2-section-head__link">Ver todos →</a>
    </div>
    <div class="lbs2-popular__grid">
      <?php $rank = 1; while ( $popular_posts->have_posts() ) : $popular_posts->the_post(); ?>
      <article class="lbs2-popular-card rv d<?php echo $rank; ?>" itemscope itemtype="https://schema.org/BlogPosting">
        <span class="lbs2-popular-card__rank" aria-hidden="true"><?php echo sprintf( '%02d', $rank ); ?></span>
        <div>
          <div class="lbs2-popular-card__title" itemprop="headline">
            <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
          </div>
          <div class="lbs2-popular-card__views">
            <?php
            $views = (int) get_post_meta( get_the_ID(), '_lbs_view_count', true );
            echo $views > 0 ? number_format( $views ) . ' leituras' : 'Popular';
            ?>
          </div>
        </div>
      </article>
      <?php $rank++; endwhile; wp_reset_postdata(); ?>
    </div>
  </div>
</section>
<?php endif; ?>

<!-- Editorial Categories -->
<section class="lbs2-categories" aria-label="Navegar por categoria">
  <div class="lbs2-container">
    <div class="lbs2-section-head">
      <h2 class="lbs2-section-head__title">Navegar por <em>tema</em></h2>
    </div>
    <div class="lbs2-cat-grid">
      <?php
      $cat_info = [
          'educacional'   => [ 'icon' => '📚', 'desc' => 'Aprenda sobre Libras, gramática, história e cultura surda.' ],
          'institucional' => [ 'icon' => '🏛️', 'desc' => 'Legislação, direitos, inclusão e políticas públicas.' ],
          'instrucional'  => [ 'icon' => '🎯', 'desc' => 'Guias práticos para produzir conteúdo acessível.' ],
      ];
      if ( ! is_wp_error( $editorial_cats ) ) :
          foreach ( $editorial_cats as $i => $cat ) :
              $info  = $cat_info[ $cat->slug ] ?? [ 'icon' => '📝', 'desc' => '' ];
              $url   = get_term_link( $cat );
              ?>
      <a href="<?php echo esc_url( $url ); ?>" class="lbs2-cat-card rv d<?php echo $i + 1; ?>" aria-label="Ver artigos de <?php echo esc_attr( $cat->name ); ?>">
        <span class="lbs2-cat-card__icon" aria-hidden="true"><?php echo $info['icon']; ?></span>
        <div class="lbs2-cat-card__name"><?php echo esc_html( $cat->name ); ?></div>
        <p class="lbs2-cat-card__desc"><?php echo esc_html( $info['desc'] ); ?></p>
        <span class="lbs2-cat-card__count"><?php echo (int) $cat->count; ?> artigos</span>
      </a>
              <?php
          endforeach;
      else :
          // Fallback sem termos cadastrados
          foreach ( $cat_info as $slug => $info ) :
              $count = 0;
              $cat   = get_category_by_slug( $slug );
              if ( $cat ) $count = $cat->count;
              ?>
      <a href="<?php echo esc_url( home_url( '/categoria/' . $slug ) ); ?>" class="lbs2-cat-card rv">
        <span class="lbs2-cat-card__icon" aria-hidden="true"><?php echo $info['icon']; ?></span>
        <div class="lbs2-cat-card__name"><?php echo esc_html( ucfirst( $slug ) ); ?></div>
        <p class="lbs2-cat-card__desc"><?php echo esc_html( $info['desc'] ); ?></p>
        <span class="lbs2-cat-card__count"><?php echo $count; ?> artigos</span>
      </a>
              <?php
          endforeach;
      endif;
      ?>
    </div>
  </div>
</section>

<!-- Newsletter / CTA -->
<section class="lbs2-newsletter" aria-label="Chamada para ação">
  <div class="lbs2-container">
    <p class="lbs2-newsletter__kicker">Acessibilidade que transforma</p>
    <h2 class="lbs2-newsletter__title">Seu vídeo em Libras em até 1 hora</h2>
    <p class="lbs2-newsletter__desc">Intérpretes reais, entrega editada, pronta para publicar.</p>
    <div style="display:flex; gap:12px; justify-content:center; flex-wrap:wrap;">
      <a href="https://huet.libras.se/"
         style="font-family:'Bricolage Grotesque',sans-serif; font-size:.88rem; font-weight:700; background:#fff; color:var(--teal-dark); padding:12px 26px; border-radius:100px; transition:transform .2s;"
         target="_blank" rel="noopener noreferrer"
         onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform=''">
        Traduzir agora →
      </a>
      <a href="https://wa.me/5548996367511?text=Ol%C3%A1%2C+estava+no+blog+do+Libras.se+e+quero+saber+mais!"
         style="font-family:'Bricolage Grotesque',sans-serif; font-size:.88rem; font-weight:700; background:transparent; color:#fff; padding:12px 26px; border-radius:100px; border:1.5px solid rgba(255,255,255,.4); transition:border-color .2s;"
         target="_blank" rel="noopener noreferrer"
         onmouseover="this.style.borderColor='rgba(255,255,255,.8)'" onmouseout="this.style.borderColor='rgba(255,255,255,.4)'">
        Falar no WhatsApp
      </a>
    </div>
  </div>
</section>

<!-- Footer -->
<footer class="lbs2-footer" role="contentinfo">
  <div class="lbs2-container">
    <div class="lbs2-footer__grid">
      <div>
        <div class="lbs2-footer__brand-name">🤟 LIBRAS.SE</div>
        <p class="lbs2-footer__brand-desc">
          Tradução profissional de vídeos para Libras.<br>
          Intérpretes reais, entrega rápida, impacto real.
        </p>
        <div class="lbs2-footer__social" aria-label="Redes sociais">
          <a href="https://instagram.com/libras.se" target="_blank" rel="noopener noreferrer" aria-label="Instagram">📸</a>
          <a href="https://linkedin.com/company/librasse" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">💼</a>
          <a href="https://youtube.com/@librasse" target="_blank" rel="noopener noreferrer" aria-label="YouTube">▶️</a>
          <a href="https://tiktok.com/@libras.se" target="_blank" rel="noopener noreferrer" aria-label="TikTok">🎵</a>
          <a href="https://facebook.com/librasse" target="_blank" rel="noopener noreferrer" aria-label="Facebook">📘</a>
        </div>
      </div>
      <div>
        <div class="lbs2-footer__col-title">Blog</div>
        <ul class="lbs2-footer__links">
          <li><a href="<?php echo esc_url( get_permalink() ); ?>">Todos os artigos</a></li>
          <li><a href="https://libras.se/blog/glossario">Glossário de Libras</a></li>
          <li><a href="<?php echo esc_url( get_term_link( 'educacional', 'category' ) ?: '#' ); ?>">Educacional</a></li>
          <li><a href="<?php echo esc_url( get_term_link( 'institucional', 'category' ) ?: '#' ); ?>">Institucional</a></li>
          <li><a href="<?php echo esc_url( get_term_link( 'instrucional', 'category' ) ?: '#' ); ?>">Instrucional</a></li>
        </ul>
      </div>
      <div>
        <div class="lbs2-footer__col-title">LIBRAS.SE</div>
        <ul class="lbs2-footer__links">
          <li><a href="https://libras.se/solucoes">Soluções</a></li>
          <li><a href="https://libras.se/portfolio">Portfólio</a></li>
          <li><a href="https://libras.se/tecnologia">Tecnologia</a></li>
          <li><a href="https://libras.se/sejatradutor">Seja TIL</a></li>
          <li><a href="https://libras.se/proposito">Propósito</a></li>
          <li><a href="mailto:contato@libras.se">contato@libras.se</a></li>
        </ul>
      </div>
    </div>
    <div class="lbs2-footer__bottom">
      <p class="lbs2-footer__copy">&copy; <?php echo date( 'Y' ); ?> LIBRAS.SE — Todos os direitos reservados.</p>
      <nav class="lbs2-footer__legal" aria-label="Links legais">
        <a href="https://libras.se/privacidade">Privacidade</a>
        <a href="https://libras.se/termos">Termos</a>
        <a href="https://libras.se/acessibilidade">Acessibilidade</a>
      </nav>
    </div>
  </div>
</footer>

<?php wp_footer(); ?>

<script>
(function () {
  'use strict';

  // Scroll reveal
  const observer = new IntersectionObserver(
    (entries) => entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('on'); observer.unobserve(e.target); } }),
    { threshold: 0.12 }
  );
  document.querySelectorAll('.rv').forEach(el => observer.observe(el));

  // Nav shadow on scroll
  const nav = document.getElementById('lbs2-nav');
  window.addEventListener('scroll', () => {
    nav.classList.toggle('lbs2-nav--scrolled', window.scrollY > 40);
  }, { passive: true });

  // Filter bar
  const filterBtns = document.querySelectorAll('.lbs2-filter__btn');
  const gridItems  = document.querySelectorAll('.lbs2-grid__item');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      filterBtns.forEach(b => { b.setAttribute('aria-selected', 'false'); });
      this.setAttribute('aria-selected', 'true');

      const filter = this.dataset.filter;
      gridItems.forEach(item => {
        if (filter === 'all' || item.dataset.type === filter) {
          item.classList.remove('lbs2-grid__item--hidden');
        } else {
          item.classList.add('lbs2-grid__item--hidden');
        }
      });
    });
  });
})();
</script>
</body>
</html>
<?php get_footer(); ?>
