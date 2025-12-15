// ============================================================
// ADMINISTRACIÓN - JavaScript
// ============================================================

let perfilEnEdicion = null;
let perfilesActuales = [];

console.log('=== ADMINISTRACION.JS CARGADO ===');

// ============================================================
// HELPERS
// ============================================================

function mostrarAlerta(msg, tipo) {
  const alertClass = tipo === 'success' ? 'alert-success' : 'alert-danger';
  const html = `<div class="alert ${alertClass} alert-dismissible fade show" role="alert" style="position:fixed;top:20px;right:20px;z-index:9999;width:300px;">
    ${msg}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  </div>`;
  const div = document.createElement('div');
  div.innerHTML = html;
  document.body.appendChild(div.firstElementChild);
  setTimeout(() => {
    const alert = document.querySelector('.alert');
    if (alert) alert.remove();
  }, 4000);
}

// ============================================================
// CAMBIAR CONTRASEÑA
// ============================================================

function cambiarPassword() {
  const passwordActual = document.getElementById('passwordActual').value.trim();
  const passwordNueva = document.getElementById('passwordNueva').value.trim();
  const passwordConfirm = document.getElementById('passwordConfirm').value.trim();

  if (!passwordActual || !passwordNueva || !passwordConfirm) {
    mostrarAlerta('Todos los campos son requeridos', 'danger');
    return;
  }

  if (passwordNueva.length < 8) {
    mostrarAlerta('La contraseña debe tener mínimo 8 caracteres', 'danger');
    return;
  }

  if (passwordNueva !== passwordConfirm) {
    mostrarAlerta('Las contraseñas no coinciden', 'danger');
    return;
  }

  const datos = {
    password_actual: passwordActual,
    password_nueva: passwordNueva
  };

  fetch('/api/cambiar-password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos)
  })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        mostrarAlerta('Contraseña cambiad correctamente', 'success');
        document.getElementById('formCambiarPassword').reset();
      } else {
        mostrarAlerta(data.error || 'Error al cambiar contraseña', 'danger');
      }
    })
    .catch(e => {
      console.error('Error:', e);
      mostrarAlerta('Error al cambiar contraseña', 'danger');
    });
}

// ============================================================
// GESTIONAR PERFILES
// ============================================================

function cargarPerfiles() {
  fetch('/api/usuarios-dev')
    .then(r => r.json())
    .then(data => {
      perfilesActuales = Array.isArray(data) ? data : [];
      renderizarPerfiles(perfilesActuales);
      console.log('Perfiles cargados:', perfilesActuales.length);
    })
    .catch(e => {
      console.error('Error:', e);
      mostrarAlerta('Error al cargar perfiles', 'danger');
    });
}

function renderizarPerfiles(perfiles) {
  const tbody = document.getElementById('cuerpoTablaPerfiles');
  if (!tbody) return;

  const filas = perfiles.map(p => {
    const estado = (p.activo === 1 || p.activo === true)
      ? '<span class="badge bg-success">Activo</span>'
      : '<span class="badge bg-secondary">Inactivo</span>';

    return `<tr>
      <td class="fw-500">${p.username}</td>
      <td>${p.nombre || '-'}</td>
      <td>${p.email || '-'}</td>
      <td><span class="badge bg-info">${p.rol || 'usuario'}</span></td>
      <td>${estado}</td>
      <td>${p.fecha_creacion ? p.fecha_creacion.split(' ')[0] : '-'}</td>
      <td>
        <button class="btn btn-sm btn-outline-warning" onclick="editarPerfil('${p.id}'); return false;" title="Editar">
          <i class="fas fa-edit"></i>
        </button>
        <button class="btn btn-sm btn-outline-danger" onclick="eliminarPerfil('${p.id}', '${p.username}'); return false;" title="Eliminar">
          <i class="fas fa-trash"></i>
        </button>
      </td>
    </tr>`;
  }).join('');

  tbody.innerHTML = filas || '<tr><td colspan="7" class="text-center text-muted">No hay perfiles cargados</td></tr>';
}

function editarPerfil(usuarioId) {
  const usuario = perfilesActuales.find(p => p.id == usuarioId);
  
  if (!usuario) {
    mostrarAlerta('Perfil no encontrado', 'danger');
    return;
  }

  perfilEnEdicion = usuarioId;
  
  document.getElementById('perfilUsername').value = usuario.username;
  document.getElementById('perfilUsername').readOnly = true;
  document.getElementById('perfilNombre').value = usuario.nombre || '';
  document.getElementById('perfilEmail').value = usuario.email || '';
  document.getElementById('perfilRol').value = usuario.rol || 'usuario';
  document.getElementById('perfilPassword').value = '';
  document.getElementById('perfilPassword').placeholder = 'Dejar vacío para mantener contraseña actual';
  document.getElementById('perfilActivo').checked = (usuario.activo === 1 || usuario.activo === true);
  
  document.getElementById('modalPerfilTitulo').textContent = 'Editar Perfil: ' + usuario.username;
  document.getElementById('btnGuardarPerfilTexto').textContent = 'Actualizar Perfil';

  try {
    if (window.bootstrap && bootstrap.Modal) {
      const modal = document.getElementById('modalNuevoPerfil');
      new bootstrap.Modal(modal).show();
    }
  } catch (e) {
    console.error(e);
  }
}

function eliminarPerfil(usuarioId, username) {
  if (!confirm(`¿Eliminar perfil "${username}"? Esta acción no se puede deshacer.`)) {
    return;
  }

  fetch(`/api/usuarios-dev?id=${usuarioId}`, {
    method: 'DELETE'
  })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        mostrarAlerta('Perfil eliminado correctamente', 'success');
        cargarPerfiles();
      } else {
        mostrarAlerta(data.error || 'Error al eliminar', 'danger');
      }
    })
    .catch(e => {
      console.error('Error:', e);
      mostrarAlerta('Error al eliminar perfil', 'danger');
    });
}

function guardarPerfil() {
  const username = document.getElementById('perfilUsername').value.trim();
  const nombre = document.getElementById('perfilNombre').value.trim();
  const email = document.getElementById('perfilEmail').value.trim();
  const rol = document.getElementById('perfilRol').value.trim();
  const password = document.getElementById('perfilPassword').value.trim();
  const activo = document.getElementById('perfilActivo').checked ? 1 : 0;

  if (!username || !nombre || !email || !rol) {
    mostrarAlerta('Completa todos los campos requeridos', 'danger');
    return;
  }

  if (!perfilEnEdicion && !password) {
    mostrarAlerta('La contraseña es requerida para nuevos perfiles', 'danger');
    return;
  }

  if (password && password.length < 8) {
    mostrarAlerta('La contraseña debe tener mínimo 8 caracteres', 'danger');
    return;
  }

  const datos = {
    username: username,
    nombre: nombre,
    email: email,
    rol: rol,
    activo: activo
  };

  if (password) {
    datos.password = password;
  }

  if (perfilEnEdicion) {
    datos.id = perfilEnEdicion;
  }

  fetch('/api/usuarios-dev', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos)
  })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        const msg = perfilEnEdicion ? 'Perfil actualizado' : 'Perfil creado';
        mostrarAlerta(msg + ' correctamente', 'success');
        try {
          if (window.bootstrap && bootstrap.Modal) {
            const modal = document.getElementById('modalNuevoPerfil');
            bootstrap.Modal.getInstance(modal).hide();
          }
        } catch (e) {
          console.error(e);
        }
        limpiarFormularioPerfil();
        cargarPerfiles();
      } else {
        mostrarAlerta(data.error || 'Error al guardar', 'danger');
      }
    })
    .catch(e => {
      console.error('Error:', e);
      mostrarAlerta('Error al guardar perfil', 'danger');
    });
}

function limpiarFormularioPerfil() {
  const form = document.getElementById('formPerfil');
  if (form) form.reset();
  
  document.getElementById('perfilUsername').readOnly = false;
  document.getElementById('modalPerfilTitulo').textContent = 'Nuevo Perfil';
  document.getElementById('btnGuardarPerfilTexto').textContent = 'Guardar Perfil';
  perfilEnEdicion = null;
}

// ============================================================
// INICIALIZACIÓN
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM Ready - Inicializando administración');

  // Verificar rol del usuario (se pasa desde el template)
  const userRole = document.body.getAttribute('data-user-role') || 'usuario';
  
  if (userRole !== 'admin') {
    // Si no es admin, redirigir al inicio
    console.warn('Acceso denegado: rol requerido es admin, actual es:', userRole);
    window.location.href = '/';
    return;
  }

  // Formulario cambiar contraseña
  const formPassword = document.getElementById('formCambiarPassword');
  if (formPassword) {
    formPassword.addEventListener('submit', function(e) {
      e.preventDefault();
      cambiarPassword();
    });
  }

  // Formulario nuevo/editar perfil
  const formPerfil = document.getElementById('formPerfil');
  if (formPerfil) {
    formPerfil.addEventListener('submit', function(e) {
      e.preventDefault();
      guardarPerfil();
    });
  }

  // Modal nueva perfil
  const modalNuevo = document.getElementById('modalNuevoPerfil');
  if (modalNuevo) {
    modalNuevo.addEventListener('hidden.bs.modal', limpiarFormularioPerfil);
    modalNuevo.addEventListener('show.bs.modal', function() {
      if (!perfilEnEdicion) {
        limpiarFormularioPerfil();
      }
    });
  }

  // Cargar perfiles al abrir tab de perfiles
  const perfilesTab = document.getElementById('perfiles-tab');
  if (perfilesTab) {
    perfilesTab.addEventListener('click', cargarPerfiles);
  }

  console.log('=== INICIALIZACIÓN COMPLETA ===');
});
