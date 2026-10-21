/* Grifo animado nos posts do blog (no estilo do g1).
   Cada <mark class="grifo"> começa sem cor e ganha a classe .on quando entra na tela;
   o CSS do post faz o marca-texto passar pela frase, da esquerda para a direita, linha a linha.
   Vários grifos na tela ao mesmo tempo são pintados em sequência, na ordem de leitura. */
(function () {
  'use strict';
  var marks = Array.prototype.slice.call(document.querySelectorAll('mark.grifo'));
  if (!marks.length) return;

  function pintar(el) { el.classList.add('on'); }

  if (!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches) {
    marks.forEach(pintar);
    return;
  }

  var livre = 0; // quando o grifo anterior libera o "marca-texto"
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      var el = e.target;
      // frase longa leva mais tempo, como na mão: entre 0,6s e 1,6s
      var ms = Math.min(1600, Math.max(600, el.textContent.length * 15));
      el.style.setProperty('--grifo-d', ms + 'ms');
      var agora = performance.now();
      var inicio = Math.max(agora + 250, livre);
      livre = inicio + ms * 0.8;
      setTimeout(function () { requestAnimationFrame(function () { pintar(el); }); }, inicio - agora);
    });
  }, { rootMargin: '0px 0px -20% 0px' });

  marks.forEach(function (el) { io.observe(el); });
})();
