// ============================================================
// GESTIÓN DE CLIENTES - JavaScript (Limpio)
// ============================================================

let clienteEnEdicion = null;
let clientesActuales = [];

console.log('=== CLIENTES.JS CARGADO ===');

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

function formatearRUT(rut) {
  if (!rut) return '';
  const clean = rut.replace(/[\.\s-]/g, '').toUpperCase();
  if (clean.length < 2) return rut;
  const dv = clean.slice(-1);
  const num = clean.slice(0, -1);
  return num.replace(/(\d)(?=(\d{3})+$)/g, '$1.') + '-' + dv;
}

function normalizarRUT(rut) {
  return (rut || '').replace(/[\.\s-]/g, '').toUpperCase();
}

// ============================================================
// CARGAR Y RENDERIZAR
// ============================================================

function cargarClientes(estado) {
  const url = estado ? `/api/clientes-dev?estado=${encodeURIComponent(estado)}` : '/api/clientes-dev';
  
  fetch(url)
    .then(r => r.json())
    .then(data => {
      clientesActuales = Array.isArray(data) ? data : [];
      renderizarClientes(clientesActuales);
      console.log('Clientes cargados:', clientesActuales.length);
    })
    .catch(e => {
      console.error('Error:', e);
      mostrarAlerta('Error al cargar clientes', 'danger');
    });
}

function renderizarClientes(clientes) {
  const tbody = document.getElementById('cuerpoTablaClientes');
  if (!tbody) return;

  // Obtener rol del usuario desde el data attribute del body
  const userRole = document.body.getAttribute('data-user-role') || 'usuario';
  
  const filas = clientes.map(c => {
    const estaActivo = c.activo === 1 || c.activo === true;
    const estado = estaActivo 
      ? '<span class="badge bg-success">Activo</span>' 
      : '<span class="badge bg-secondary">Inactivo</span>';
    const iconoToggle = estaActivo ? 'fa-toggle-on' : 'fa-toggle-off';
    const tituloToggle = estaActivo ? 'Desactivar' : 'Activar';
    
    // Construir botones según el rol
    let botones = `<button class="btn btn-sm btn-outline-info" onclick="verCliente('${c.rut}'); return false;" title="Ver">
          <i class="fas fa-eye"></i>
        </button>`;
    
    // Solo admin puede editar, cambiar estado y eliminar
    if (userRole === 'admin' || userRole === 'usuario') {
      botones += `
        <button class="btn btn-sm btn-outline-warning" onclick="editarCliente('${c.rut}'); return false;" title="Editar">
          <i class="fas fa-edit"></i>
        </button>
        <button class="btn btn-sm btn-outline-success" onclick="toggleEstado('${c.rut}'); return false;" title="${tituloToggle}">
          <i class="fas ${iconoToggle}"></i>
        </button>
        <button class="btn btn-sm btn-outline-danger" onclick="eliminarCliente('${c.rut}'); return false;" title="Eliminar">
          <i class="fas fa-trash"></i>
        </button>`;
    }
    
    return `<tr>
      <td>${formatearRUT(c.rut)}</td>
      <td>${c.razon_social}</td>
      <td>${c.email || '-'}</td>
      <td>${c.telefono || '-'}</td>
      <td>${c.giro || '-'}</td>
      <td>${c.banco || '-'}</td>
      <td>${estado}</td>
      <td>${botones}</td>
    </tr>`;
  }).join('');

  tbody.innerHTML = filas;
  
  const contador = document.getElementById('clientesCount');
  if (contador) contador.textContent = clientes.length;
}

// ============================================================
// ACCIONES CRUD
// ============================================================

function verCliente(rut) {
  const rn = normalizarRUT(rut);
  
  fetch(`/api/clientes-dev/${rn}`)
    .then(r => {
      if (!r.ok) throw new Error('No encontrado');
      return r.json();
    })
    .then(c => {
      // Intentar usar Bootstrap Modal
      try {
        if (window.bootstrap && bootstrap.Modal) {
          document.getElementById('verRut').textContent = formatearRUT(c.rut);
          document.getElementById('verRazonSocial').textContent = c.razon_social;
          document.getElementById('verEmail').textContent = c.email || '-';
          document.getElementById('verTelefono').textContent = c.telefono || '-';
          document.getElementById('verGiro').textContent = c.giro || '-';
          document.getElementById('verBanco').textContent = c.banco || '-';
          document.getElementById('verDireccion').textContent = c.direccion || '-';
          document.getElementById('verObservaciones').textContent = c.observaciones || '-';
          
          const modal = document.getElementById('modalVerCliente');
          new bootstrap.Modal(modal).show();
        } else {
          alert('Cliente: ' + c.razon_social + '\nEmail: ' + (c.email || 'N/A'));
        }
      } catch (e) {
        console.error(e);
        alert('Cliente: ' + c.razon_social + '\nEmail: ' + (c.email || 'N/A'));
      }
    })
    .catch(e => {
      console.error('Error verCliente:', e);
      mostrarAlerta('Error al cargar detalles', 'danger');
    });
}

function editarCliente(rut) {
  const userRole = document.body.getAttribute('data-user-role') || 'usuario';
  
  if (userRole === 'consulta') {
    mostrarAlerta('No tienes permiso para editar clientes', 'danger');
    return;
  }
  
  const rn = normalizarRUT(rut);
  
  fetch(`/api/clientes-dev/${rn}`)
    .then(r => {
      if (!r.ok) throw new Error('No encontrado');
      return r.json();
    })
    .then(c => {
      clienteEnEdicion = c.rut;
      
      // Llenar formulario
      document.getElementById('clienteRut').value = c.rut;
      document.getElementById('clienteRut').readOnly = true;
      document.getElementById('clienteRazonSocial').value = c.razon_social || '';
      document.getElementById('clienteGiro').value = c.giro || '';
      document.getElementById('clienteTelefono').value = c.telefono || '';
      document.getElementById('clienteEmail').value = c.email || '';
      document.getElementById('clienteDireccion').value = c.direccion || '';
      document.getElementById('clienteObservaciones').value = c.observaciones || '';
      document.getElementById('clienteBanco').value = c.banco || '';
      document.getElementById('clienteCuentaCorriente').value = c.cuenta_corriente || '';
      document.getElementById('clienteActivo').checked = (c.activo === 1 || c.activo === true);
      
      document.getElementById('modalTitulo').textContent = 'Editar Cliente';
      document.getElementById('btnGuardarTexto').textContent = 'Actualizar';
      
      try {
        if (window.bootstrap && bootstrap.Modal) {
          const modal = document.getElementById('modalClienteNuevo');
          new bootstrap.Modal(modal).show();
        }
      } catch (e) {
        console.error(e);
      }
    })
    .catch(e => {
      console.error('Error editarCliente:', e);
      mostrarAlerta('Error al cargar cliente', 'danger');
    });
}

function eliminarCliente(rut) {
  const userRole = document.body.getAttribute('data-user-role') || 'usuario';
  
  if (userRole === 'consulta' || userRole === 'usuario') {
    mostrarAlerta('No tienes permiso para eliminar clientes', 'danger');
    return;
  }
  
  if (!confirm('¿Eliminar este cliente?')) return;
  
  const rn = normalizarRUT(rut);
  
  fetch(`/api/clientes-dev?rut=${rn}`, {
    method: 'DELETE'
  })
    .then(r => r.json())
    .then(data => {
      mostrarAlerta('Cliente eliminado', 'success');
      cargarClientes();
    })
    .catch(e => {
      console.error('Error eliminarCliente:', e);
      mostrarAlerta('Error al eliminar', 'danger');
    });
}

function toggleEstado(rut) {
  const userRole = document.body.getAttribute('data-user-role') || 'usuario';
  
  if (userRole === 'consulta') {
    mostrarAlerta('No tienes permiso para cambiar el estado de clientes', 'danger');
    return;
  }
  
  const rn = normalizarRUT(rut);
  console.log('Toggle para RUT normalizado:', rn);
  console.log('Clientes actuales:', clientesActuales.map(c => ({ rut: c.rut, norm: normalizarRUT(c.rut), activo: c.activo })));
  
  // Buscar exactamente el cliente con este RUT (sin normalizar para comparación)
  let cliente = null;
  for (let i = 0; i < clientesActuales.length; i++) {
    if (normalizarRUT(clientesActuales[i].rut) === rn) {
      cliente = clientesActuales[i];
      console.log('Cliente encontrado en índice', i, ':', cliente);
      break;
    }
  }
  
  if (!cliente) {
    mostrarAlerta('Cliente no encontrado', 'danger');
    return;
  }
  
  const nuevoEstado = (cliente.activo === 1 || cliente.activo === true) ? 0 : 1;
  console.log('Estado anterior:', cliente.activo, '-> nuevo estado:', nuevoEstado);
  
  const datos = {
    rut: cliente.rut,
    razon_social: cliente.razon_social,
    email: cliente.email || '',
    giro: cliente.giro || '',
    telefono: cliente.telefono || '',
    direccion: cliente.direccion || '',
    observaciones: cliente.observaciones || '',
    banco: cliente.banco || '',
    cuenta_corriente: cliente.cuenta_corriente || '',
    activo: nuevoEstado
  };
  
  console.log('Datos a enviar:', datos);
  
  fetch('/api/clientes-dev', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos)
  })
    .then(r => r.json())
    .then(data => {
      const mensaje = nuevoEstado === 1 ? 'Cliente activado' : 'Cliente desactivado';
      mostrarAlerta(mensaje, 'success');
      cargarClientes();
    })
    .catch(e => {
      console.error('Error toggleEstado:', e);
      mostrarAlerta('Error al cambiar estado', 'danger');
    });
}

function guardarCliente() {
  const rut = document.getElementById('clienteRut').value.trim();
  const razonSocial = document.getElementById('clienteRazonSocial').value.trim();
  
  if (!rut || !razonSocial) {
    mostrarAlerta('RUT y Razón Social son requeridos', 'danger');
    return;
  }
  
  const datos = {
    rut: rut,
    razon_social: razonSocial,
    giro: document.getElementById('clienteGiro').value.trim(),
    telefono: document.getElementById('clienteTelefono').value.trim(),
    email: document.getElementById('clienteEmail').value.trim(),
    direccion: document.getElementById('clienteDireccion').value.trim(),
    observaciones: document.getElementById('clienteObservaciones').value.trim(),
    banco: document.getElementById('clienteBanco').value.trim(),
    cuenta_corriente: document.getElementById('clienteCuentaCorriente').value.trim(),
    activo: document.getElementById('clienteActivo').checked ? 1 : 0
  };
  
  fetch('/api/clientes-dev', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos)
  })
    .then(r => r.json())
    .then(data => {
      mostrarAlerta('Cliente guardado correctamente', 'success');
      try {
        if (window.bootstrap && bootstrap.Modal) {
          const modal = document.getElementById('modalClienteNuevo');
          bootstrap.Modal.getInstance(modal).hide();
        }
      } catch (e) {
        console.error(e);
      }
      limpiarFormulario();
      cargarClientes();
    })
    .catch(e => {
      console.error('Error guardarCliente:', e);
      mostrarAlerta('Error al guardar', 'danger');
    });
}

function limpiarFormulario() {
  const form = document.getElementById('formCliente');
  if (form) form.reset();
  
  document.getElementById('clienteRut').readOnly = false;
  document.getElementById('modalTitulo').textContent = 'Nuevo Cliente';
  document.getElementById('btnGuardarTexto').textContent = 'Guardar';
  clienteEnEdicion = null;
}

function filtrarClientes() {
  const q = (document.getElementById('buscarCliente') || {}).value.toLowerCase();
  const estado = (document.getElementById('filtroEstado') || {}).value;
  
  if (estado) {
    cargarClientes(estado);
    return;
  }
  
  const filtrados = clientesActuales.filter(c =>
    !q || 
    (c.rut || '').toLowerCase().includes(q) ||
    (c.razon_social || '').toLowerCase().includes(q) ||
    (c.email || '').toLowerCase().includes(q)
  );
  
  renderizarClientes(filtrados);
}

function limpiarFiltros() {
  document.getElementById('buscarCliente').value = '';
  document.getElementById('filtroEstado').value = '';
  renderizarClientes(clientesActuales);
}

// ============================================================
// INICIALIZACIÓN
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM Ready - Inicializando gestión de clientes');
  
  // Cargar clientes al inicio (por defecto activos)
  const filtroEstado = document.getElementById('filtroEstado');
  if (filtroEstado && filtroEstado.value) {
    cargarClientes(filtroEstado.value);
  } else {
    cargarClientes('activo');
  }
  
  // Listeners para filtros
  const buscar = document.getElementById('buscarCliente');
  if (buscar) buscar.addEventListener('keyup', filtrarClientes);
  
  const filtro = document.getElementById('filtroEstado');
  if (filtro) filtro.addEventListener('change', filtrarClientes);
  
  // Modal nueva cliente
  const modalNuevo = document.getElementById('modalClienteNuevo');
  if (modalNuevo) {
    modalNuevo.addEventListener('hidden.bs.modal', limpiarFormulario);
  }
  
  // Botón nueva cliente
  const btnNuevo = document.getElementById('btnNuevaCliente');
  if (btnNuevo) {
    btnNuevo.addEventListener('click', function() {
      limpiarFormulario();
      try {
        if (window.bootstrap && bootstrap.Modal) {
          new bootstrap.Modal(modalNuevo).show();
        }
      } catch (e) {
        console.error(e);
      }
    });
  }
  
  // Botón guardar
  const btnGuardar = document.getElementById('btnGuardarCliente');
  if (btnGuardar) {
    btnGuardar.addEventListener('click', guardarCliente);
  }
  
  // Botón limpiar filtros
  const btnLimpiar = document.getElementById('btnLimpiarFiltros');
  if (btnLimpiar) {
    btnLimpiar.addEventListener('click', limpiarFiltros);
  }
  
  console.log('=== INICIALIZACIÓN COMPLETA ===');
});
