/* ══════════════════════════════════════════════════
   SIDEBAR TOGGLE
══════════════════════════════════════════════════ */
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  sidebar.classList.toggle('colapsado');
  localStorage.setItem('hp-sidebar', sidebar.classList.contains('colapsado') ? '0' : '1');
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
  // Restaurar estado del sidebar
  const sidebarAbierto = localStorage.getItem('hp-sidebar');
  if (sidebarAbierto === '0') {
    document.getElementById('sidebar')?.classList.add('colapsado');
  }

  // En móvil, colapsar por defecto si no hay preferencia guardada
  if (sidebarAbierto === null && window.innerWidth <= 640) {
    document.getElementById('sidebar')?.classList.add('colapsado');
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
