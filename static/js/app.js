/* ══════════════════════════════════════════════════
   AUTO-CIERRE DE SESIÓN POR INACTIVIDAD
   4 min sin interacción → advertencia con 60s de gracia
   (5 min en total) → cierre automático de sesión
══════════════════════════════════════════════════ */
(function () {
  const IDLE_MS = 4 * 60 * 1000;   // 4 minutos hasta la advertencia
  const GRACIA_S = 60;             // 60 segundos de gracia

  let idleTimer = null;
  let countdownTimer = null;

  function logoutUrl() { return window.LOGOUT_URL || '/logout/'; }
  function modal() { return document.getElementById('modal-inactividad'); }

  function reiniciarInactividad() {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(mostrarAdvertencia, IDLE_MS);
  }

  function mostrarAdvertencia() {
    const m = modal();
    if (!m) return;
    m.classList.add('activo');

    let restante = GRACIA_S;
    const cont = document.getElementById('inactividad-contador');
    if (cont) cont.textContent = restante;

    countdownTimer = setInterval(() => {
      restante -= 1;
      if (cont) cont.textContent = restante;
      if (restante <= 0) cerrarSesionAhora();
    }, 1000);
  }

  // Expuestas globalmente para los botones del modal
  window.seguirActivo = function () {
    const m = modal();
    if (m) m.classList.remove('activo');
    clearInterval(countdownTimer);
    reiniciarInactividad();
  };

  window.cerrarSesionAhora = function () {
    clearInterval(countdownTimer);
    clearTimeout(idleTimer);
    window.location.href = logoutUrl();
  };

  // Cualquier interacción reinicia el contador — salvo durante la advertencia,
  // donde el usuario debe confirmar manualmente que sigue presente.
  ['mousemove', 'mousedown', 'keydown', 'scroll', 'touchstart', 'click'].forEach(evt => {
    document.addEventListener(evt, () => {
      const m = modal();
      if (m && m.classList.contains('activo')) return;
      reiniciarInactividad();
    }, { passive: true });
  });

  document.addEventListener('DOMContentLoaded', reiniciarInactividad);
})();

/* ══════════════════════════════════════════════════
   SEGUIMIENTOS — revelar más sin saturar (de a 6)
══════════════════════════════════════════════════ */
function verMasSeguimientos() {
  const ocultos = document.querySelectorAll('#seg-lista .seg-oculto');
  let mostrados = 0;
  ocultos.forEach(el => {
    if (mostrados < 6) { el.classList.remove('seg-oculto'); mostrados++; }
  });
  // Si ya no quedan ocultos, esconder el botón
  if (document.querySelectorAll('#seg-lista .seg-oculto').length === 0) {
    const btn = document.getElementById('seg-vermas');
    if (btn) btn.style.display = 'none';
  }
}

/* ══════════════════════════════════════════════════
   TABLAS — revelar filas de a 20 (Pacientes / Tutores)
══════════════════════════════════════════════════ */
function verMasFilas(tipo) {
  const tbody = document.getElementById('tbody-' + tipo);
  if (!tbody) return;
  const ocultas = tbody.querySelectorAll('tr.fila-oculta');
  let n = 0;
  ocultas.forEach(tr => { if (n < 20) { tr.classList.remove('fila-oculta'); n++; } });

  const restantes = tbody.querySelectorAll('tr.fila-oculta').length;
  const total = tbody.querySelectorAll('tr.buscable').length;
  const info = document.getElementById(tipo + '-visibles');
  if (info) info.textContent = total - restantes;

  if (restantes === 0) {
    const footer = document.getElementById('footer-' + tipo);
    const btn = document.getElementById(tipo + '-vermas');
    if (btn) btn.style.display = 'none';
    if (footer) footer.querySelector('.tabla-footer-info').textContent =
      'Mostrando los ' + total + ' registros';
  }
}

/* ══════════════════════════════════════════════════
   SIDEBAR TOGGLE
══════════════════════════════════════════════════ */
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  sidebar.classList.toggle('colapsado');
  const abierto = !sidebar.classList.contains('colapsado');

  // El overlay solo importa en móvil; lo activamos según el estado
  if (overlay) overlay.classList.toggle('activo', abierto);

  // En escritorio recordamos la preferencia; en móvil siempre arranca cerrado
  if (window.innerWidth > 768) {
    localStorage.setItem('hp-sidebar', abierto ? '1' : '0');
  }
}

/* ══════════════════════════════════════════════════
   TEMA — día / noche
══════════════════════════════════════════════════ */
function _actualizarIconoTema(isDark) {
  const icono = document.getElementById('tema-icono');
  const label = document.getElementById('tema-label');
  if (icono) icono.className = isDark ? 'ti ti-sun' : 'ti ti-moon';
  if (label) label.textContent  = isDark ? 'Modo claro'  : 'Modo oscuro';
}

function toggleTema() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const nuevo  = isDark ? 'light' : 'dark';

  // Transición suave
  document.body.classList.add('tema-transicion');
  document.documentElement.setAttribute('data-theme', nuevo);
  localStorage.setItem('hp-tema', nuevo);
  _actualizarIconoTema(nuevo === 'dark');

  setTimeout(() => document.body.classList.remove('tema-transicion'), 350);
}

/* ══════════════════════════════════════════════════
   NAVEGACIÓN SPA
══════════════════════════════════════════════════ */
const titulos = {
  inicio:    'Inicio',
  pacientes: 'Pacientes',
  tutores:   'Tutores',
  consultas: 'Consultas',
  perfil:    'Perfil — Paciente',
  nuevo:     'Nuevo registro',
  usuarios:  'Gestión de usuarios',
};

function mostrarPantalla(id, el) {
  // Cerrar el dropdown del buscador al cambiar de pantalla
  if (typeof cerrarDropdownBusqueda === 'function') cerrarDropdownBusqueda();

  document.querySelectorAll('.pantalla').forEach(p => p.classList.remove('activa'));
  const pantalla = document.getElementById('pantalla-' + id);
  if (pantalla) pantalla.classList.add('activa');

  const titulo = document.getElementById('topbar-titulo');
  if (titulo) titulo.textContent = titulos[id] || id;

  if (el) {
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('activo'));
    el.classList.add('activo');
  }

  // En móvil, cerrar el sidebar al elegir una opción
  if (window.innerWidth <= 768) {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    if (sidebar && !sidebar.classList.contains('colapsado')) {
      sidebar.classList.add('colapsado');
      if (overlay) overlay.classList.remove('activo');
    }
  }
}


/* ══════════════════════════════════════════════════
   BUSCADOR — autocompletado (typeahead, máx. 5)
══════════════════════════════════════════════════ */
const MAX_RESULTADOS = 5;
let _indiceBusqueda = null;   // se construye una vez
let _seleccionado = -1;       // índice resaltado en el dropdown

function _construirIndice() {
  if (_indiceBusqueda) return _indiceBusqueda;
  _indiceBusqueda = Array.from(document.querySelectorAll('tr.buscable')).map(tr => ({
    nombre: tr.dataset.nombre || '',
    tipo:   tr.dataset.tipo || '',
    sub:    tr.dataset.sub || '',
    url:    tr.dataset.url || '',
    buscar: (tr.dataset.buscar || '').toLowerCase(),
  })).filter(x => x.nombre);
  return _indiceBusqueda;
}

function _escapeHtml(s) {
  return s.replace(/[&<>"']/g, c => (
    {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]
  ));
}

function _resaltar(nombre, q) {
  const i = nombre.toLowerCase().indexOf(q);
  if (i < 0 || !q) return _escapeHtml(nombre);
  return _escapeHtml(nombre.slice(0, i)) +
         '<mark>' + _escapeHtml(nombre.slice(i, i + q.length)) + '</mark>' +
         _escapeHtml(nombre.slice(i + q.length));
}

function _posicionarDropdown() {
  const wrap = document.querySelector('.buscador');
  const cont = document.getElementById('buscador-resultados');
  if (!wrap || !cont) return;
  const r = wrap.getBoundingClientRect();
  cont.style.top = (r.bottom + 6) + 'px';
  cont.style.left = r.left + 'px';
  cont.style.width = r.width + 'px';
}

function buscarTypeahead(termino) {
  const q = (termino || '').trim().toLowerCase();
  const wrap = document.querySelector('.buscador');
  const cont = document.getElementById('buscador-resultados');
  if (wrap) wrap.classList.toggle('con-texto', q.length > 0);
  if (!cont) return;

  _seleccionado = -1;
  if (!q) { cont.classList.remove('activo'); cont.innerHTML = ''; return; }
  _posicionarDropdown();

  // Ranking: empieza-con > nombre-incluye > texto-incluye
  const idx = _construirIndice();
  const resultados = idx
    .map(item => {
      const nom = item.nombre.toLowerCase();
      let score = -1;
      if (nom.startsWith(q)) score = 0;
      else if (nom.includes(q)) score = 1;
      else if (item.buscar.includes(q)) score = 2;
      return { item, score };
    })
    .filter(r => r.score >= 0)
    .sort((a, b) => a.score - b.score || a.item.nombre.localeCompare(b.item.nombre))
    .slice(0, MAX_RESULTADOS);

  if (resultados.length === 0) {
    cont.innerHTML = '<div class="buscador-vacio"><i class="ti ti-search-off"></i> Sin resultados</div>';
    cont.classList.add('activo');
    return;
  }

  cont.innerHTML = resultados.map((r, n) => {
    const it = r.item;
    const icono = it.tipo === 'Tutor' ? '👤' : '🐾';
    return `<div class="buscador-item" data-n="${n}" data-url="${_escapeHtml(it.url)}"
              data-nombre="${_escapeHtml(it.nombre)}" data-tipo="${_escapeHtml(it.tipo)}"
              onmousedown="seleccionarResultado(${n})">
      <div class="buscador-item-icono">${icono}</div>
      <div class="buscador-item-texto">
        <div class="buscador-item-nombre">${_resaltar(it.nombre, q)}</div>
        ${it.sub ? `<div class="buscador-item-sub">${_escapeHtml(it.sub)}</div>` : ''}
      </div>
      <span class="buscador-item-tipo">${_escapeHtml(it.tipo)}</span>
    </div>`;
  }).join('');
  cont.classList.add('activo');
}

function _itemsDropdown() {
  return Array.from(document.querySelectorAll('#buscador-resultados .buscador-item'));
}

function buscadorTeclado(e) {
  const items = _itemsDropdown();
  if (e.key === 'Escape') { cerrarDropdownBusqueda(); return; }
  if (!items.length) return;

  if (e.key === 'ArrowDown') {
    e.preventDefault();
    _seleccionado = (_seleccionado + 1) % items.length;
    _pintarSeleccion(items);
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    _seleccionado = (_seleccionado - 1 + items.length) % items.length;
    _pintarSeleccion(items);
  } else if (e.key === 'Enter') {
    e.preventDefault();
    const n = _seleccionado >= 0 ? _seleccionado : 0;   // Enter abre el primero
    seleccionarResultado(n);
  }
}

function _pintarSeleccion(items) {
  items.forEach((el, i) => el.classList.toggle('seleccionado', i === _seleccionado));
  if (_seleccionado >= 0) items[_seleccionado].scrollIntoView({ block: 'nearest' });
}

function seleccionarResultado(n) {
  const items = _itemsDropdown();
  const el = items[n];
  if (!el) return;
  const url = el.dataset.url;
  if (url) {
    window.location.href = url;
  } else {
    // Sin permiso de edición: ir a la pantalla correspondiente y filtrar la tabla
    const tipo = el.dataset.tipo;
    const pantalla = tipo === 'Tutor' ? 'tutores' : 'pacientes';
    const nav = document.querySelector(`[data-pantalla="${pantalla}"]`);
    mostrarPantalla(pantalla, nav);
    cerrarDropdownBusqueda();
  }
}

function cerrarDropdownBusqueda() {
  const cont = document.getElementById('buscador-resultados');
  if (cont) { cont.classList.remove('activo'); }
  _seleccionado = -1;
}

function limpiarBusqueda() {
  const input = document.getElementById('buscador-input');
  if (input) input.value = '';
  buscarTypeahead('');
  if (input) input.focus();
}

function mostrarFormulario(id, btn) {
  document.querySelectorAll('.contenido-form').forEach(f => f.classList.remove('activo'));
  document.querySelectorAll('.btn-form').forEach(b => b.classList.remove('activo'));
  const form = document.getElementById(id);
  if (form) form.classList.add('activo');
  if (btn) btn.classList.add('activo');
}

function mostrarTabConsulta(id, el) {
  document.querySelectorAll('.tab-consulta').forEach(t => t.style.display = 'none');
  const panel = document.getElementById('pantalla-consultas');
  if (panel) panel.querySelectorAll('.pestania').forEach(p => p.classList.remove('activa'));
  const tab = document.getElementById(id);
  if (tab) tab.style.display = 'block';
  if (el) el.classList.add('activa');
}

/* ══════════════════════════════════════════════════
   INIT
══════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  // Estado inicial del sidebar
  const sidebar = document.getElementById('sidebar');
  if (sidebar) {
    if (window.innerWidth <= 768) {
      // En móvil siempre arranca cerrado (flota sobre el contenido)
      sidebar.classList.add('colapsado');
    } else if (localStorage.getItem('hp-sidebar') === '0') {
      // En escritorio respetamos la preferencia guardada
      sidebar.classList.add('colapsado');
    }
  }

  // Sincronizar icono con el tema ya aplicado (anti-flash lo aplicó antes)
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  _actualizarIconoTema(isDark);

  // Navegar a pantalla si viene ?pantalla=X en la URL
  const params  = new URLSearchParams(window.location.search);
  const pantalla = params.get('pantalla');
  if (pantalla) {
    const navEl = document.querySelector(`[data-pantalla="${pantalla}"]`);
    mostrarPantalla(pantalla, navEl);
    const url = new URL(window.location);
    url.searchParams.delete('pantalla');
    window.history.replaceState({}, '', url);
  }

  // Cerrar el dropdown del buscador al hacer clic fuera
  document.addEventListener('mousedown', (e) => {
    if (!e.target.closest('.buscador')) cerrarDropdownBusqueda();
  });
  // Reposicionar el dropdown si cambia el tamaño de la ventana
  window.addEventListener('resize', () => {
    const cont = document.getElementById('buscador-resultados');
    if (cont && cont.classList.contains('activo')) _posicionarDropdown();
  });

  // Auto-cerrar alertas de éxito
  document.querySelectorAll('.alerta-exito').forEach(el => {
    setTimeout(() => el.remove(), 4000);
  });
});
