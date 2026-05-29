const titulos = {
  inicio: 'Inicio',
  pacientes: 'Pacientes',
  tutores: 'Tutores',
  consultas: 'Consultas',
  perfil: 'Perfil — Rocky',
  nuevo: 'Nuevo registro'
};

function mostrarPantalla(id, el) {
  document.querySelectorAll('.pantalla').forEach(p => p.classList.remove('activa'));
  document.getElementById('pantalla-' + id).classList.add('activa');
  document.getElementById('topbar-titulo').textContent = titulos[id] || id;
  if (el) {
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('activo'));
    el.classList.add('activo');
  }
}

function mostrarTab(id, el) {
  document.querySelectorAll('.contenido-tab').forEach(t => t.classList.remove('activo'));
  document.querySelectorAll('.pestania').forEach(p => p.classList.remove('activa'));
  document.getElementById(id).classList.add('activo');
  el.classList.add('activa');
}

function mostrarFormulario(id, btn) {
  document.querySelectorAll('.contenido-form').forEach(f => f.classList.remove('activo'));
  document.querySelectorAll('.btn-form').forEach(b => b.classList.remove('activo'));
  document.getElementById(id).classList.add('activo');
  btn.classList.add('activo');
}

document.addEventListener('DOMContentLoaded', () => {
  // Inicialización opcional: asegurar la pantalla por defecto
  // ya está marcada en el HTML; si se desea, se puede aplicar lógica adicional aquí.
});
