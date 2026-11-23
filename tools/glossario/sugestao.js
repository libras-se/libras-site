/* Formulário "Sugira uma correção ou novo termo" do índice do glossário: CRM (LibrasLead) + webhook do n8n. */
const WEBHOOK_URL = 'https://n8n.trngl.com.br/webhook/glossario-sugestao';
document.getElementById('sform').addEventListener('submit', async function(e) {
  e.preventDefault();
  const btn = document.getElementById('sbtn');
  const status = document.getElementById('sform-status');
  const f = e.target;
  const name = f.name.value.trim(), email = f.email.value.trim(),
        type = f.type.value, suggestion = f.suggestion.value.trim();

  if (!name || !email || !type || !suggestion) {
    status.className = 'err'; status.textContent = 'Por favor, preencha todos os campos antes de enviar.'; return;
  }

  btn.disabled = true; btn.textContent = 'Enviando…';
  status.className = ''; status.textContent = '';

  // Captação no CRM interno — em paralelo; o n8n continua sendo quem confirma o envio
  if (window.LibrasLead) {
    const hp = document.getElementById('s-website');
    window.LibrasLead.send({
      formId: 'glossario-sugestao',
      formType: 'glossary_suggestion',
      website: hp ? hp.value : undefined,
      contact: { name: name.slice(0, 200), email: email.slice(0, 200) },
      consent: { privacyPolicyAccepted: true },
      request: { description: suggestion.slice(0, 4000), additionalData: { tipo: type } }
    });
  }

  try {
    const res = await fetch(WEBHOOK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ page: location.href, page_title: document.title, name, email, type, suggestion, submitted_at: new Date().toISOString() })
    });
    if (res.ok) {
      status.className = 'ok';
      status.textContent = 'Sugestão enviada com sucesso! Nossa equipe editorial analisará em breve. Obrigado!';
      f.reset();
    } else { throw new Error('HTTP ' + res.status); }
  } catch {
    status.className = 'err';
    status.textContent = 'Não foi possível enviar agora. Tente novamente ou escreva para contato@libras.se.';
  } finally { btn.disabled = false; btn.textContent = 'Enviar sugestão →'; }
});

