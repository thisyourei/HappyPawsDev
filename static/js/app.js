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
  // Reiniciar la búsqueda al cambiar de pantalla (evita filas ocultas heredadas)
  const inputBusqueda = document.getElementById('buscador-input');
  if (inputBusqueda && inputBusqueda.value) {
    inputBusqueda.value = '';
    const wrap = document.querySelector('.buscador');
    if (wrap) wrap.classList.remove('con-texto');
    document.querySelectorAll('table.tabla tbody tr').forEach(tr => { tr.style.display = ''; });
    document.querySelectorAll('.buscador-sin-resultados').forEach(a => { a.style.display = 'none'; });
  }

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
   BUSCADOR — filtra filas de la pantalla activa
══════════════════════════════════════════════════ */
function buscarEnTabla(termino) {
  const q = (termino || '').trim().toLowerCase();
  const wrap = document.querySelector('.buscador');
  if (wrap) wrap.classList.toggle('con-texto', q.length > 0);

  // Si estamos en Inicio (sin tabla) y se empieza a buscar, ir a Pacientes
  // (cambio manual para no reiniciar el término de búsqueda)
  let activa = document.querySelector('.pantalla.activa');
  if (q && activa && activa.id === 'pantalla-inicio') {
    document.querySelectorAll('.pantalla').forEach(p => p.classList.remove('activa'));
    const dest = document.getElementById('pantalla-pacientes');
    if (dest) dest.classList.add('activa');
    const nav = document.querySelector('[data-pantalla="pacientes"]');
    if (nav) {
      document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('activo'));
      nav.classList.add('activo');
    }
    const titulo = document.getElementById('topbar-titulo');
    if (titulo) titulo.textContent = 'Pacientes';
    activa = dest;
  }
  if (!activa) return;

  let visibles = 0, totales = 0;
  activa.querySelectorAll('table.tabla tbody tr').forEach(tr => {
    // Saltar filas especiales (separadores de día, mensajes "no hay...")
    if (tr.querySelector('td[colspan]')) return;
    totales++;
    const coincide = !q || tr.textContent.toLowerCase().includes(q);
    tr.style.display = coincide ? '' : 'none';
    if (coincide) visibles++;
  });

  // Mostrar/ocultar aviso de "sin resultados"
  activa.querySelectorAll('table.tabla').forEach(tabla => {
    let aviso = tabla.parentElement.querySelector('.buscador-sin-resultados');
    if (q && totales > 0 && visibles === 0) {
      if (!aviso) {
        aviso = document.createElement('div');
        aviso.className = 'buscador-sin-resultados';
        aviso.style.cssText = 'text-align:center;color:var(--text-tertiary);padding:24px;font-size:13px';
        aviso.innerHTML = '<i class="ti ti-search-off"></i> Sin resultados para "<strong></strong>"';
        tabla.parentElement.appendChild(aviso);
      }
      aviso.querySelector('strong').textContent = termino;
      aviso.style.display = 'block';
    } else if (aviso) {
      aviso.style.display = 'none';
    }
  });
}

function limpiarBusqueda() {
  const input = document.getElementById('buscador-input');
  if (input) input.value = '';
  buscarEnTabla('');
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

  // Auto-cerrar alertas de éxito
  document.querySelectorAll('.alerta-exito').forEach(el => {
    setTimeout(() => el.remove(), 4000);
  });
});
