/* Fachada leve para vídeos do YouTube: mostra a miniatura e só carrega o player no clique.
   Marcação: <div class="yt-lite" data-id="ID" data-title="Título" [data-params="start=30"]>…</div>
   (gerada por tools/auditoria/codemod_site.py). Sem dependências. */
(function () {
  function abre(el) {
    if (el.querySelector("iframe")) return;
    var p = el.getAttribute("data-params");
    var f = document.createElement("iframe");
    f.src = "https://www.youtube.com/embed/" + el.getAttribute("data-id") + "?autoplay=1" + (p ? "&" + p : "");
    f.title = el.getAttribute("data-title") || "Vídeo do YouTube";
    f.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
    f.referrerPolicy = "strict-origin-when-cross-origin";
    f.allowFullscreen = true;
    el.appendChild(f);
    var b = el.querySelector("button");
    if (b) b.remove();
    f.focus();
  }
  document.addEventListener("click", function (e) {
    var el = e.target.closest && e.target.closest(".yt-lite");
    if (el) { e.preventDefault(); abre(el); }
  });
})();
