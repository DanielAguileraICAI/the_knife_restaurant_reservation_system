// Variables globales
let restauranteActual = null;
let platosDisponibles = [];
let platosFactura = []; // Array de {plato: objeto, cantidad: numero}

document.addEventListener('DOMContentLoaded', function() {
  // Check if restaurant is already logged in
  const loggedRestaurant = sessionStorage.getItem('currentRestaurant');
  if (loggedRestaurant) {
    const restaurante = JSON.parse(loggedRestaurant);
    restauranteActual = restaurante;
    cargarDatosRestaurante(restaurante);
    document.getElementById('restaurantLoginForm').closest('.card').style.display = 'none';
  }

  // Restaurant Login Form
  const restaurantLoginForm = document.getElementById('restaurantLoginForm');
  if (restaurantLoginForm) {
    restaurantLoginForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const idRestaurante = document.getElementById('restaurantId').value.trim();
      
      if (!idRestaurante) {
        alert('Por favor ingresa el ID del restaurante');
        return;
      }
      
      try {
        const response = await fetch(`/api/restaurantes/${idRestaurante}`);
        const data = await response.json();
        
        if (data.restaurante) {
          restauranteActual = data.restaurante;
          // Guardar en sessionStorage
          sessionStorage.setItem('currentRestaurant', JSON.stringify(data.restaurante));
          await cargarDatosRestaurante(data.restaurante);
          // Ocultar formulario de login
          restaurantLoginForm.closest('.card').style.display = 'none';
        } else {
          document.getElementById('restaurantPanel').style.display = 'none';
          document.getElementById('noRestaurant').style.display = 'block';
        }
      } catch (error) {
        console.error('Error:', error);
        alert('Error al buscar el restaurante');
      }
    });
  }

  // Form para crear factura
  const crearFacturaForm = document.getElementById('crearFacturaForm');
  if (crearFacturaForm) {
    crearFacturaForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      await generarFactura();
    });
  }

  // Form para añadir plato
  const anadirPlatoForm = document.getElementById('anadirPlatoForm');
  if (anadirPlatoForm) {
    anadirPlatoForm.addEventListener('submit', function(e) {
      e.preventDefault();
      anadirPlatoAFactura();
    });
  }
});

async function cargarDatosRestaurante(restaurante) {
  // Mostrar info del restaurante
  document.getElementById('restaurantInfo').innerHTML = `
    <div class="row">
      <div class="col-md-6">
        <p class="mb-2"><strong>Nombre:</strong> ${restaurante.nombre}</p>
        <p class="mb-2"><strong>ID:</strong> ${restaurante.id}</p>
        <p class="mb-2"><strong>Ciudad:</strong> ${restaurante.ciudad}</p>
      </div>
      <div class="col-md-6">
        <p class="mb-2"><strong>CCAA:</strong> ${restaurante.ccaa}</p>
        <p class="mb-2"><strong>Tipo Comida:</strong> ${restaurante.tipo_comida}</p>
        <p class="mb-2"><strong>Estrellas Michelin:</strong> ${'⭐'.repeat(restaurante.estrellas)}</p>
      </div>
    </div>
  `;

  // Cargar platos del restaurante
  await cargarPlatos(restaurante.id);

  // Cargar reservas
  const reservasResponse = await fetch(`/api/restaurantes/${restaurante.id}/reservas`);
  const reservasData = await reservasResponse.json();
  const reservas = reservasData.reservas || [];

  // Cargar facturas del restaurante
  const facturasResponse = await fetch(`/api/restaurantes/${restaurante.id}/facturas`);
  const facturasData = await facturasResponse.json();
  const facturas = facturasData.facturas || [];

  // Crear mapa de facturas por id_reserva
  const facturasMap = {};
  facturas.forEach(f => {
    if (f.id_reserva) {
      facturasMap[f.id_reserva] = f;
    }
  });

  // Calcular estadísticas
  const ingresosTotales = facturas.reduce((sum, f) => sum + f.precio, 0);
  document.getElementById('totalReservasRestaurante').textContent = reservas.length;
  document.getElementById('totalFacturasRestaurante').textContent = facturas.length;
  document.getElementById('ingresosTotales').textContent = ingresosTotales.toFixed(2) + '€';

  // Renderizar reservas
  const reservasContainer = document.getElementById('reservasRestaurante');
  if (reservas.length === 0) {
    reservasContainer.innerHTML = '<p class="text-muted-custom">No hay reservas registradas.</p>';
  } else {
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);

    reservasContainer.innerHTML = `
      <div class="table-responsive">
        <table class="table table-hover">
          <thead>
            <tr>
              <th>ID Reserva</th>
              <th>Cliente</th>
              <th>Fecha</th>
              <th>Hora</th>
              <th>Personas</th>
              <th>Estado</th>
              <th>Acción</th>
            </tr>
          </thead>
          <tbody>
            ${reservas.map(r => {
              const fechaReserva = new Date(r.fecha + 'T00:00:00');
              const esPasada = fechaReserva < hoy;
              const tieneFactura = facturasMap[r.id_reserva];
              
              return `
                <tr>
                  <td><code>${r.id_reserva}</code></td>
                  <td>${r.nombre_cliente}</td>
                  <td>${r.fecha}</td>
                  <td>${r.hora}</td>
                  <td>${r.num_personas}</td>
                  <td>
                    <span class="badge ${r.estado && (r.estado.toLowerCase() === 'confirmada') ? 'bg-success' : 'bg-secondary'}">
                      ${r.estado ? r.estado.charAt(0).toUpperCase() + r.estado.slice(1).toLowerCase() : ''}
                    </span>
                    ${esPasada ? '<span class="badge bg-secondary ms-1">Pasada</span>' : ''}
                    ${tieneFactura ? '<span class="badge bg-info ms-1">Facturada</span>' : ''}
                  </td>
                  <td>
                    ${esPasada && !tieneFactura ? `
                      <button class="btn btn-sm btn-primary" onclick="abrirModalCrearFactura('${r.id_reserva}', '${r.id_cliente}', '${r.nombre_cliente}', '${r.fecha}', '${r.hora}')">
                        <i class="fas fa-receipt"></i> Crear Factura
                      </button>
                    ` : tieneFactura ? `
                      <span class="text-success"><i class="fas fa-check-circle"></i> Factura: ${tieneFactura.id_factura} (${tieneFactura.precio.toFixed(2)}€)</span>
                    ` : `
                      <span class="text-muted">Pendiente</span>
                    `}
                  </td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>
    `;
  }

  document.getElementById('restaurantPanel').style.display = 'block';
  document.getElementById('noRestaurant').style.display = 'none';
}

async function cargarPlatos(idRestaurante) {
  try {
    const response = await fetch(`/api/restaurantes/${idRestaurante}/platos`);
    const data = await response.json();
    platosDisponibles = data.platos || [];
    console.log('Platos cargados:', platosDisponibles);
  } catch (error) {
    console.error('Error al cargar platos:', error);
    platosDisponibles = [];
  }
}

function abrirModalCrearFactura(idReserva, idCliente, nombreCliente, fecha, hora) {
  // Resetear platos seleccionados
  platosFactura = [];
  actualizarListaPlatos();
  
  // Llenar datos del modal
  document.getElementById('facturaIdReserva').value = idReserva;
  document.getElementById('facturaIdCliente').value = idCliente;
  document.getElementById('facturaIdRestaurante').value = restauranteActual.id;
  document.getElementById('facturaReservaInfo').innerHTML = `
    <strong>Reserva:</strong> ${idReserva}<br>
    <strong>Cliente:</strong> ${nombreCliente}<br>
    <strong>Fecha:</strong> ${fecha} - ${hora}
  `;
  
  // Abrir modal
  const modal = new bootstrap.Modal(document.getElementById('crearFacturaModal'));
  modal.show();
}

function abrirModalAnadirPlato() {
  // Llenar select con platos disponibles
  const selectPlato = document.getElementById('selectPlato');
  selectPlato.innerHTML = '<option value="">Selecciona un plato...</option>' +
    platosDisponibles.map((p, idx) => 
      `<option value="${idx}">${p.nombre} (${p.tipo}) - ${p.precio.toFixed(2)}€</option>`
    ).join('');
  
  // Resetear cantidad
  document.getElementById('cantidadPlato').value = 1;
  
  // Abrir modal
  const modal = new bootstrap.Modal(document.getElementById('anadirPlatoModal'));
  modal.show();
}

function anadirPlatoAFactura() {
  const selectPlato = document.getElementById('selectPlato');
  const cantidad = parseInt(document.getElementById('cantidadPlato').value);
  const platoIdx = parseInt(selectPlato.value);
  
  if (isNaN(platoIdx) || cantidad < 1) {
    alert('Por favor selecciona un plato y una cantidad válida');
    return;
  }
  
  const plato = platosDisponibles[platoIdx];
  
  // Verificar si el plato ya está en la lista
  const existente = platosFactura.find(p => p.plato.nombre === plato.nombre);
  if (existente) {
    existente.cantidad += cantidad;
  } else {
    platosFactura.push({
      plato: { ...plato },
      cantidad: cantidad
    });
  }
  
  actualizarListaPlatos();
  
  // Cerrar modal
  const modal = bootstrap.Modal.getInstance(document.getElementById('anadirPlatoModal'));
  modal.hide();
}

function actualizarListaPlatos() {
  const container = document.getElementById('platosSeleccionados');
  
  if (platosFactura.length === 0) {
    container.innerHTML = '<p class="text-muted-custom small mb-0">No hay platos añadidos. Añade al menos uno.</p>';
    document.getElementById('totalFactura').textContent = '0.00€';
    return;
  }
  
  let total = 0;
  container.innerHTML = platosFactura.map((item, idx) => {
    const subtotal = item.plato.precio * item.cantidad;
    total += subtotal;
    return `
      <div class="d-flex justify-content-between align-items-center p-2 mb-1" style="background: rgba(255,255,255,0.1); border-radius: 5px;">
        <div>
          <strong>${item.plato.nombre}</strong> (${item.plato.tipo})<br>
          <small>${item.cantidad} × ${item.plato.precio.toFixed(2)}€ = ${subtotal.toFixed(2)}€</small>
        </div>
        <button type="button" class="btn btn-sm btn-danger" onclick="eliminarPlato(${idx})">
          <i class="fas fa-trash"></i>
        </button>
      </div>
    `;
  }).join('');
  
  document.getElementById('totalFactura').textContent = total.toFixed(2) + '€';
}

function eliminarPlato(idx) {
  platosFactura.splice(idx, 1);
  actualizarListaPlatos();
}

async function generarFactura() {
  if (platosFactura.length === 0) {
    alert('Debes añadir al menos un plato a la factura');
    return;
  }
  
  const idReserva = document.getElementById('facturaIdReserva').value;
  const idCliente = document.getElementById('facturaIdCliente').value;
  const idRestaurante = document.getElementById('facturaIdRestaurante').value;
  
  // Calcular total
  const total = platosFactura.reduce((sum, item) => sum + (item.plato.precio * item.cantidad), 0);
  
  // Preparar datos para enviar
  const facturaData = {
    id_reserva: idReserva,
    id_cliente: idCliente,
    id_restaurante: idRestaurante,
    precio: total,
    platos: platosFactura.map(item => ({
      nombre: item.plato.nombre,
      tipo: item.plato.tipo,
      precio: item.plato.precio,
      cantidad: item.cantidad
    }))
  };
  
  try {
    const response = await fetch('/api/restaurantes/factura/crear', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(facturaData)
    });
    
    const data = await response.json();
    
    if (response.ok) {
      alert(`Factura generada correctamente!\n\nID: ${data.id_factura}\nTotal: ${total.toFixed(2)}€`);
      
      // Cerrar modal
      const modal = bootstrap.Modal.getInstance(document.getElementById('crearFacturaModal'));
      modal.hide();
      
      // Recargar datos del restaurante
      await cargarDatosRestaurante(restauranteActual);
    } else {
      alert('Error: ' + data.mensaje);
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Error al generar la factura');
  }
}

// Función para cerrar sesión del restaurante
function cerrarSesionRestaurante() {
  if (confirm('¿Estás seguro de que quieres cerrar sesión?')) {
    sessionStorage.removeItem('currentRestaurant');
    window.location.reload();
  }
}

// ===== ANALYTICS FUNCTIONS =====

// Listener para cargar analytics cuando se activa el tab
document.getElementById('analytics-tab')?.addEventListener('shown.bs.tab', async function() {
  if (restauranteActual) {
    await cargarAnalytics(restauranteActual.id);
  }
});

async function cargarAnalytics(idRestaurante) {
  try {
    // Cargar clientes sin valorar
    await cargarClientesSinValorar(idRestaurante);
    
    // Cargar gasto medio
    await cargarGastoMedio(idRestaurante);
    
    // Cargar día más concurrido
    await cargarDiaMasConcurrido(idRestaurante);
    
    // Cargar top platos
    await cargarTopPlatos(idRestaurante);
    
    // Cargar gráfico comparativo de precios
    await cargarGraficoPrecioComparativo(idRestaurante);
  } catch (error) {
    console.error('Error cargando analytics:', error);
  }
}

async function cargarClientesSinValorar(idRestaurante) {
  try {
    const response = await fetch(`/api/restaurantes/${idRestaurante}/analytics/sin-valorar`);
    const data = await response.json();
    
    const container = document.getElementById('clientesSinValorar');
    
    if (!data.clientes || data.clientes.length === 0) {
      container.innerHTML = '<p class="text-muted-custom">¡Genial! Todos los clientes han valorado tu restaurante.</p>';
      return;
    }
    
    container.innerHTML = `
      <div class="table-responsive">
        <table class="table table-hover">
          <thead>
            <tr>
              <th>Cliente</th>
              <th>Email</th>
              <th>Fecha Visita</th>
              <th>Acción</th>
            </tr>
          </thead>
          <tbody>
            ${data.clientes.map(c => `
              <tr>
                <td>
                  <strong>${c.nombre}</strong><br>
                  <small class="text-muted-custom">ID: ${c.id_cliente}</small>
                </td>
                <td>${c.email}</td>
                <td>${c.fecha_visita}</td>
                <td>
                  <button class="btn btn-sm btn-warning" onclick="abrirModalEmail('${c.id_cliente}', '${c.nombre}', '${c.email}', '${restauranteActual.nombre}')">
                    <i class="fas fa-envelope"></i> Enviar Recordatorio
                  </button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  } catch (error) {
    console.error('Error:', error);
  }
}

async function cargarGastoMedio(idRestaurante) {
  try {
    const response = await fetch(`/api/restaurantes/${idRestaurante}/analytics/gasto-medio`);
    const data = await response.json();
    
    const container = document.getElementById('gastoMedio');
    container.innerHTML = `
      <div class="text-center py-4">
        <h2 class="display-4" style="color: var(--primary);">${data.gasto_medio}€</h2>
        <p class="text-muted-custom">por persona</p>
      </div>
    `;
  } catch (error) {
    console.error('Error:', error);
  }
}

async function cargarDiaMasConcurrido(idRestaurante) {
  try {
    const response = await fetch(`/api/restaurantes/${idRestaurante}/analytics/grafico-dias`);
    const data = await response.json();
    
    const container = document.getElementById('diaMasConcurrido');
    
    if (data.imagen) {
      container.innerHTML = `
        <div class="text-center">
          <img src="data:image/png;base64,${data.imagen}" alt="Gráfico de reservas por día" class="img-fluid" style="max-width: 100%; height: auto;">
        </div>
      `;
    } else {
      container.innerHTML = '<p class="text-muted-custom">No hay datos suficientes para generar el gráfico.</p>';
    }
  } catch (error) {
    console.error('Error:', error);
    document.getElementById('diaMasConcurrido').innerHTML = '<p class="text-danger">Error al cargar el gráfico.</p>';
  }
}

async function cargarTopPlatos(idRestaurante) {
  try {
    const response = await fetch(`/api/restaurantes/${idRestaurante}/analytics/top-platos`);
    const data = await response.json();
    
    const container = document.getElementById('topPlatos');
    
    if (!data.platos || data.platos.length === 0) {
      container.innerHTML = '<p class="text-muted-custom">No hay datos de platos pedidos aún.</p>';
      return;
    }
    
    const medallas = ['🥇', '🥈', '🥉'];
    const colores = ['#FFD700', '#C0C0C0', '#CD7F32'];
    
    container.innerHTML = `
      <div class="row g-3">
        ${data.platos.map((plato, idx) => `
          <div class="col-md-4">
            <div class="card text-center h-100" style="background: linear-gradient(135deg, ${colores[idx]}22, ${colores[idx]}11); border: 2px solid ${colores[idx]};">
              <div class="card-body">
                <div style="font-size: 3rem;">${medallas[idx]}</div>
                <h5 class="card-title">${plato.nombre}</h5>
                <span class="badge bg-secondary mb-2">${plato.tipo}</span>
                <p class="mb-0"><strong>${plato.total_pedidos}</strong> pedidos</p>
              </div>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  } catch (error) {
    console.error('Error:', error);
  }
}

// Función para abrir modal de email
function abrirModalEmail(idCliente, nombreCliente, email, nombreRestaurante) {
  const mensaje = `Estimado/a ${nombreCliente},

Esperamos que hayas disfrutado de tu reciente visita a ${nombreRestaurante}.

Nos gustaría mucho conocer tu opinión sobre tu experiencia en nuestro restaurante. Tu valoración nos ayuda a mejorar nuestro servicio y ofrecer la mejor experiencia posible a nuestros clientes.

¿Podrías dedicar un momento para valorar tu visita? Puedes hacerlo accediendo a tu área de cliente con tu ID: ${idCliente}

Muchas gracias por tu tiempo y esperamos verte pronto de nuevo.

Saludos cordiales,
Equipo de ${nombreRestaurante}`;

  document.getElementById('emailDestinatario').textContent = `${nombreCliente} <${email}>`;
  document.getElementById('emailMensaje').value = mensaje;
  
  // Guardar datos para el envío
  document.getElementById('enviarEmailModal').dataset.clienteId = idCliente;
  document.getElementById('enviarEmailModal').dataset.email = email;
  
  const modal = new bootstrap.Modal(document.getElementById('enviarEmailModal'));
  modal.show();
}

// Función ficticia para enviar email
function enviarEmailRecordatorio() {
  const modal = bootstrap.Modal.getInstance(document.getElementById('enviarEmailModal'));
  const email = document.getElementById('enviarEmailModal').dataset.email;
  
  alert(`✅ Email enviado exitosamente a ${email}\n\nEl cliente recibirá el recordatorio en breve.`);
  modal.hide();
}

// Función para cargar gráfico comparativo de precios
async function cargarGraficoPrecioComparativo(idRestaurante) {
  try {
    const response = await fetch(`/api/restaurantes/${idRestaurante}/analytics/grafico-precio-comparativo`);
    const data = await response.json();
    
    const container = document.getElementById('graficoPrecioComparativo');
    
    if (data.imagen) {
      let infoHtml = '';
      if (data.percentil !== null) {
        const interpretacion = data.percentil < 25 ? 'económico' : 
                              data.percentil < 50 ? 'precio medio-bajo' :
                              data.percentil < 75 ? 'precio medio-alto' : 'premium';
        infoHtml = `
          <div class="alert alert-info mt-3">
            <strong>📊 Análisis:</strong> Tu restaurante está en el <strong>percentil ${data.percentil}</strong> del mercado (${interpretacion}).
            <br>
            <strong>Tu precio:</strong> ${data.gasto_restaurante}€/persona | 
            <strong>Media del mercado:</strong> ${data.media_mercado}€/persona | 
            <strong>Muestra:</strong> ${data.total_restaurantes} restaurantes
          </div>
        `;
      }
      
      container.innerHTML = `
        <div class="text-center">
          <img src="data:image/png;base64,${data.imagen}" alt="Gráfico comparativo de precios" class="img-fluid" style="max-width: 100%; height: auto;">
          ${infoHtml}
        </div>
      `;
    } else {
      container.innerHTML = '<p class="text-muted-custom">No hay datos suficientes para generar el gráfico.</p>';
    }
  } catch (error) {
    console.error('Error:', error);
    document.getElementById('graficoPrecioComparativo').innerHTML = '<p class="text-danger">Error al cargar el gráfico comparativo.</p>';
  }
}
