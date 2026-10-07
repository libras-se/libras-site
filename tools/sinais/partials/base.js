const nav = document.getElementById('nav');
window.addEventListener('scroll', () => nav.classList.toggle('sc', scrollY > 60), { passive: true });

const mob  = document.getElementById('mobm');
const hamb = document.getElementById('hamb');
const mobx = document.getElementById('mobx');

function openMenu() {
  mob.classList.add('open');
  hamb.setAttribute('aria-expanded', 'true');
  hamb.setAttribute('aria-label', 'Fechar menu');
  mob.querySelector('a').focus();
}
function closeMenu() {
  mob.classList.remove('open');
  hamb.setAttribute('aria-expanded', 'false');
  hamb.setAttribute('aria-label', 'Abrir menu');
}
function cm() { closeMenu(); }

hamb.addEventListener('click', openMenu);
mobx.addEventListener('click', closeMenu);
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && mob.classList.contains('open')) closeMenu();
});

const rvO = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('on'); rvO.unobserve(e.target); }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -24px 0px' });
document.querySelectorAll('.rv').forEach(el => rvO.observe(el));

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  });
});
