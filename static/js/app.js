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
