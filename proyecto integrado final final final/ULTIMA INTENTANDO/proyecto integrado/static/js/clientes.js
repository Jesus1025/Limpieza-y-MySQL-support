// ============================================================
// CLIENTES.JS - Funciones auxiliares
// Las funciones principales están en el template
// ============================================================

console.log('=== CLIENTES.JS CARGADO ===');

// Cargar clientes al inicio
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM Ready');
  cargarClientes();
});

function cargarClientes() {
  const filtro = document.getElementById('filtroEstado');
  const estado = filtro ? filtro.value : 'activo';
  const url = estado ? `/api/clientes-dev?estado=${estado}` : '/api/clientes-dev';
  
  fetch(url)
    .then(r => r.json())
    .then(clientes => {
      console.log('Clientes cargados:', clientes.length);
      renderizarTabla(clientes);
    })
    .catch(e => console.error('Error cargando clientes:', e));
}

function renderizarTabla(clientes) {
  const tbody = document.getElementById('cuerpoTablaClientes');
  if (!tbody) return;
  
  // Verificar si el usuario es de solo consulta (variable definida en el template)
  const esConsulta = typeof ES_CONSULTA !== 'undefined' && ES_CONSULTA;
  
  if (clientes.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted py-4">No hay clientes</td></tr>';
    return;
  }
  
  tbody.innerHTML = clientes.map(c => {
    const estado = c.activo == 1 
      ? '<span class="badge bg-success">Activo</span>' 
      : '<span class="badge bg-secondary">Inactivo</span>';
    
    // Solo mostrar botones de acción si NO es usuario de consulta
    let botonesAccion = `<button class="btn btn-sm btn-outline-info" onclick="verCliente('${c.rut}')" title="Ver"><i class="fas fa-eye"></i></button>`;
    
    if (!esConsulta) {
      const botonToggle = c.activo == 1
        ? `<button class="btn btn-sm btn-outline-secondary" onclick="toggleEstadoCliente('${c.rut}')" title="Desactivar cliente"><i class="fas fa-toggle-on"></i></button>`
        : `<button class="btn btn-sm btn-outline-success" onclick="toggleEstadoCliente('${c.rut}')" title="Activar cliente"><i class="fas fa-toggle-off"></i></button>`;
      
      botonesAccion += `
        <button class="btn btn-sm btn-outline-warning" onclick="editarCliente('${c.rut}')" title="Editar"><i class="fas fa-edit"></i></button>
        ${botonToggle}
        <button class="btn btn-sm btn-outline-danger" onclick="eliminarCliente('${c.rut}')" title="Eliminar"><i class="fas fa-trash"></i></button>`;
    }
    
    return `<tr>
      <td>${formatearRUT(c.rut)}</td>
      <td>${c.razon_social || ''}</td>
      <td>${c.email || '-'}</td>
      <td>${c.telefono || '-'}</td>
      <td>${c.giro || '-'}</td>
      <td>${c.banco || '-'}</td>
      <td>${estado}</td>
      <td>${botonesAccion}</td>
    </tr>`;
  }).join('');
  
  const contador = document.getElementById('clientesCount');
  if (contador) contador.textContent = clientes.length;
}

function formatearRUT(rut) {
  if (!rut) return '';
  const clean = rut.replace(/[\.\s\-]/g, '').toUpperCase();
  if (clean.length < 2) return rut;
  const dv = clean.slice(-1);
  const num = clean.slice(0, -1);
  return num.replace(/(\d)(?=(\d{3})+$)/g, '$1.') + '-' + dv;
}

// Filtro por estado
const filtroEstado = document.getElementById('filtroEstado');
if (filtroEstado) {
  filtroEstado.addEventListener('change', cargarClientes);
}

// Búsqueda
const buscarInput = document.getElementById('buscarCliente');
if (buscarInput) {
  buscarInput.addEventListener('keyup', function() {
    const q = this.value.toLowerCase();
    const filas = document.querySelectorAll('#cuerpoTablaClientes tr');
    filas.forEach(fila => {
      const texto = fila.textContent.toLowerCase();
      fila.style.display = texto.includes(q) ? '' : 'none';
    });
  });
}
