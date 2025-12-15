// JS para editar clientes desde el botón de lápiz en la tabla

document.addEventListener('DOMContentLoaded', function () {
    // Delegación para botones de editar cliente
    document.querySelectorAll('.btn-editar-cliente').forEach(btn => {
        btn.addEventListener('click', function () {
            const rut = this.dataset.rut;
            fetch(`/api/clientes/${rut}`)
                .then(res => res.json())
                .then(cliente => {
                    document.getElementById('edit_rut').value = cliente.rut || '';
                    document.getElementById('edit_razon_social').value = cliente.razon_social || '';
                    document.getElementById('edit_giro').value = cliente.giro || '';
                    document.getElementById('edit_telefono').value = cliente.telefono || '';
                    document.getElementById('edit_email').value = cliente.email || '';
                    document.getElementById('edit_direccion').value = cliente.direccion || '';
                    document.getElementById('edit_comuna').value = cliente.comuna || '';
                    document.getElementById('edit_cuenta_corriente').value = cliente.cuenta_corriente || '';
                    document.getElementById('edit_banco').value = cliente.banco || '';
                    if (window.$ && $('#modalEditarCliente').modal) {
                        $('#modalEditarCliente').modal('show');
                    } else {
                        document.getElementById('modalEditarCliente').style.display = 'block';
                    }
                });
        });
    });

    // Guardar cambios del cliente editado
    const form = document.getElementById('formEditarCliente');
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const rut = document.getElementById('edit_rut').value;
            const data = {
                razon_social: document.getElementById('edit_razon_social').value,
                giro: document.getElementById('edit_giro').value,
                telefono: document.getElementById('edit_telefono').value,
                email: document.getElementById('edit_email').value,
                direccion: document.getElementById('edit_direccion').value,
                comuna: document.getElementById('edit_comuna').value,
                cuenta_corriente: document.getElementById('edit_cuenta_corriente').value,
                banco: document.getElementById('edit_banco').value
            };
            fetch(`/api/clientes/${rut}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(resp => {
                if (resp.success) {
                    if (window.$ && $('#modalEditarCliente').modal) {
                        $('#modalEditarCliente').modal('hide');
                    } else {
                        document.getElementById('modalEditarCliente').style.display = 'none';
                    }
                    location.reload();
                } else {
                    alert(resp.error || 'Error al actualizar');
                }
            });
        });
    }
});
