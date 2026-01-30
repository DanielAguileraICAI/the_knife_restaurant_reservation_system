// ===== THE KNIFE - CLIENT WEB APP =====
// Global state
const state = {
  restaurantes: [],
  filteredRestaurantes: [],
  currentClientId: '99727933D', // Demo client
  alergiaSeleccionada: null
};

// ===== UTILITY FUNCTIONS =====
function showLoading(containerId) {
  const container = document.getElementById(containerId);
  if (container) {
    container.innerHTML = '<div class="loading"><div class="spinner"></div><p class="mt-3">Cargando...</p></div>';
  }
}

function getStarIcon(count) { return '⭐'.repeat(count); }
function getPriceIcon(level) { return '€'.repeat(level); }

// ===== API CALLS =====
async function fetchRestaurantes() {
  try {
    const response = await fetch('/api/restaurantes');
    const data = await response.json();
    state.restaurantes = data.restaurantes || [];
    state.filteredRestaurantes = [...state.restaurantes];
    return state.restaurantes;
  } catch (error) {
    console.error('Error:', error);
    return [];
  }
}

async function fetchPlatosRestaurante(idRestaurante, alergia = null) {
  try {
    let url = `/api/restaurantes/${idRestaurante}/platos`;
    if (alergia) {
      url += `?alergia=${encodeURIComponent(alergia)}`;
    }
    const response = await fetch(url);
    const data = await response.json();
    return data.platos || [];
  } catch (error) {
    console.error('Error:', error);
    return [];
  }
}

async function fetchReservasCliente(idCliente) {
  try {
    const response = await fetch(`/api/reservas/${idCliente}`);
    const data = await response.json();
    return data.reservas || [];
  } catch (error) {
    console.error('Error:', error);
    return [];
  }
}

async function crearReserva(reservaData) {
  try {
    const response = await fetch('/api/reservas', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reservaData)
    });
    return await response.json();
  } catch (error) {
    console.error('Error:', error);
    return { mensaje: 'Error al crear la reserva' };
  }
}

// ===== RENDER FUNCTIONS =====
function renderRestauranteCard(restaurante) {
  const stars = restaurante.estrellas > 0 ? `<span class="badge badge-michelin">${getStarIcon(restaurante.estrellas)} Michelin</span>` : '';
  const price = `<span class="badge badge-presupuesto">${getPriceIcon(restaurante.presupuesto)}</span>`;
  
  return `
    <div class="col">
      <div class="card card-restaurant h-100">
        <div class="card-body">
          <h5 class="restaurant-name">${restaurante.nombre}</h5>
          <p class="text-muted-custom mb-2"><small>${restaurante.ciudad}, ${restaurante.ccaa}</small></p>
          <p class="mb-2">
            <span class="badge bg-secondary">${restaurante.tipo_comida}</span>
            ${price} ${stars}
          </p>
          ${restaurante.cadena ? `<p class="text-muted-custom"><small>Cadena: ${restaurante.cadena}</small></p>` : ''}
        </div>
        <div class="card-footer bg-transparent border-0 pb-3">
          <button class="btn btn-primary btn-sm w-100" onclick="showMenu('${restaurante.id}', '${restaurante.nombre}')">Ver Menú</button>
          <button class="btn btn-outline-primary btn-sm w-100 mt-2" onclick="reservar('${restaurante.id}', '${restaurante.nombre}')">Reservar</button>
        </div>
      </div>
    </div>
  `;
}

function renderPlatos(platos, restauranteNombre, alergiaFiltro = null) {
  if (!platos || platos.length === 0) return '<p class="text-muted-custom">No hay platos disponibles</p>';
  
  const grouped = { ENTRANTE: [], PRINCIPAL: [], POSTRE: [], BEBIDA: [] };
  platos.forEach(plato => { if (grouped[plato.tipo]) grouped[plato.tipo].push(plato); });
  
  const icons = { ENTRANTE: '🥗', PRINCIPAL: '🍽️', POSTRE: '🍰', BEBIDA: '🥤' };
  let html = `<div class="modal fade" id="menuModal" tabindex="-1">
    <div class="modal-dialog modal-lg modal-dialog-scrollable">
      <div class="modal-content" style="background: var(--glass-bg); backdrop-filter: blur(20px);">
        <div class="modal-header border-0">
          <h5 class="modal-title" style="color: var(--primary); font-weight: 700;">Menú - ${restauranteNombre}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">`;
  
  if (alergiaFiltro) {
    html += `<div class="alert alert-info mb-3" style="background: rgba(13, 202, 240, 0.1); border-color: #0dcaf0;">
      <strong>🚫 Filtro de alergia activo:</strong> ${alergiaFiltro}<br>
      <small>Los platos en <span style="background: #d4edda; padding: 2px 6px; border-radius: 3px;">verde claro</span> NO contienen este alérgeno.</small>
    </div>`;
  }
  
  Object.keys(grouped).forEach(tipo => {
    if (grouped[tipo].length > 0) {
      html += `<div class="mb-4"><h6 class="fw-bold text-primary">${icons[tipo]} ${tipo}</h6><div class="list-group">`;
      grouped[tipo].forEach(plato => {
        const sinAlergeno = plato.sin_alergeno === true;
        const bgColor = sinAlergeno ? 'rgba(212, 237, 218, 0.8)' : 'rgba(255,255,255,0.6)';
        const icon = sinAlergeno ? '✅ ' : '';
        html += `<div class="list-group-item d-flex justify-content-between align-items-center" style="background: ${bgColor}; border: 1px solid var(--glass-border);">
          <span>${icon}${plato.nombre}</span><span class="badge bg-primary rounded-pill">${plato.precio.toFixed(2)}€</span>
        </div>`;
      });
      html += `</div></div>`;
    }
  });
  
  html += `</div><div class="modal-footer border-0"><button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button></div></div></div></div>`;
  return html;
}

// ===== EVENT HANDLERS =====
async function showMenu(idRestaurante, nombre) {
  const existingModal = document.getElementById('menuModal');
  if (existingModal) existingModal.remove();
  
  document.body.insertAdjacentHTML('beforeend', `<div class="modal fade show" id="menuModal" style="display: block;" tabindex="-1">
    <div class="modal-dialog modal-lg"><div class="modal-content" style="background: var(--glass-bg);">
      <div class="modal-body"><div class="loading"><div class="spinner"></div><p class="mt-3">Cargando menú...</p></div></div>
    </div></div></div>`);
  document.body.classList.add('modal-open');
  
  // Pasar alergia si hay filtro activo
  const alergia = state.alergiaSeleccionada || null;
  const platos = await fetchPlatosRestaurante(idRestaurante, alergia);
  document.getElementById('menuModal').remove();
  document.body.insertAdjacentHTML('beforeend', renderPlatos(platos, nombre, alergia));
  const modal = new bootstrap.Modal(document.getElementById('menuModal'));
  modal.show();
  
  document.getElementById('menuModal').addEventListener('hidden.bs.modal', function() {
    this.remove();
    document.body.classList.remove('modal-open');
  });
}

function reservar(idRestaurante, nombre) {
  sessionStorage.setItem('selectedRestaurant', JSON.stringify({ id: idRestaurante, nombre: nombre }));
  window.location.href = '/book';
}

// ===== FILTER FUNCTIONS =====
async function applyFilters() {
  const searchTerm = document.getElementById('search')?.value.toLowerCase() || '';
  const estrellas = document.getElementById('filterEstrellas')?.value || '';
  const presupuesto = document.getElementById('filterPresupuesto')?.value || '';
  const tipoComida = document.getElementById('filterTipoComida')?.value || '';
  const alergia = document.getElementById('filterAlergia')?.value || '';
  
  // Si hay filtro de alergia, hacer fetch con parámetro
  if (alergia) {
    const response = await fetch(`/api/restaurantes?alergia=${encodeURIComponent(alergia)}`);
    const data = await response.json();
    state.restaurantes = data.restaurantes;
    state.filteredRestaurantes = state.restaurantes;
  } else {
    // Aplicar filtros locales
    state.filteredRestaurantes = state.restaurantes.filter(rest => {
      const matchSearch = rest.nombre.toLowerCase().includes(searchTerm) || 
                         rest.tipo_comida.toLowerCase().includes(searchTerm) ||
                         rest.ciudad.toLowerCase().includes(searchTerm);
      const matchEstrellas = !estrellas || rest.estrellas.toString() === estrellas;
      const matchPresupuesto = !presupuesto || rest.presupuesto.toString() === presupuesto;
      const matchTipo = !tipoComida || rest.tipo_comida === tipoComida;
      return matchSearch && matchEstrellas && matchPresupuesto && matchTipo;
    });
  }
  
  // Guardar alergia seleccionada en state
  state.alergiaSeleccionada = alergia;
  
  renderRestaurantes();
}

function renderRestaurantes() {
  const container = document.getElementById('restaurants-list');
  if (!container) return;
  
  if (state.filteredRestaurantes.length === 0) {
    container.innerHTML = '<div class="col-12"><div class="alert alert-info" style="background: var(--glass-bg);">No se encontraron restaurantes.</div></div>';
    return;
  }
  
  container.innerHTML = state.filteredRestaurantes.map(renderRestauranteCard).join('');
}

// ===== PAGE INITIALIZATION =====
document.addEventListener('DOMContentLoaded', async function() {
  
  // RESTAURANTS PAGE
  if (document.getElementById('restaurants-list')) {
    showLoading('restaurants-list');
    await fetchRestaurantes();
    
    // Populate tipo comida filter
    const tipoSelect = document.getElementById('filterTipoComida');
    if (tipoSelect) {
      const tipos = [...new Set(state.restaurantes.map(r => r.tipo_comida))];
      tipos.sort();
      tipoSelect.innerHTML = '<option value="">Todos los tipos</option>' + 
        tipos.map(tipo => `<option value="${tipo}">${tipo}</option>`).join('');
    }
    
    // Populate alergia filter
    const alergiaSelect = document.getElementById('filterAlergia');
    if (alergiaSelect) {
      try {
        const response = await fetch('/api/alergenos');
        const data = await response.json();
        alergiaSelect.innerHTML = '<option value="">Sin filtro</option>' + 
          data.alergenos.map(a => `<option value="${a.nombre}">${a.nombre}</option>`).join('');
      } catch (error) {
        console.error('Error cargando alérgenos:', error);
      }
    }
    
    renderRestaurantes();
    
    const searchInput = document.getElementById('search');
    if (searchInput) searchInput.addEventListener('input', applyFilters);
    
    ['filterEstrellas', 'filterPresupuesto', 'filterTipoComida', 'filterAlergia'].forEach(id => {
      const element = document.getElementById(id);
      if (element) element.addEventListener('change', applyFilters);
    });
  }
  
  // HOME PAGE - FEATURED
  if (document.getElementById('featured')) {
    showLoading('featured');
    const restaurantes = await fetchRestaurantes();
    const featured = restaurantes.filter(r => r.estrellas >= 2).slice(0, 3);
    document.getElementById('featured').innerHTML = featured.map(renderRestauranteCard).join('');
  }
  
  // RESERVATIONS PAGE
  if (document.getElementById('reservations-list')) {
    showLoading('reservations-list');
    const reservas = await fetchReservasCliente(state.currentClientId);
    const container = document.getElementById('reservations-list');
    
    if (reservas.length === 0) {
      container.innerHTML = '<div class="alert alert-info" style="background: var(--glass-bg);">No tienes reservas. <a href="/book" class="alert-link">Haz una reserva</a></div>';
    } else {
      container.innerHTML = reservas.map(reserva => `
        <div class="col">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">${reserva.restaurante_nombre}</h5>
              <p class="text-muted-custom mb-2"><small>${reserva.restaurante_ciudad}</small></p>
              <p class="mb-1"><strong>Fecha:</strong> ${reserva.fecha} a las ${reserva.hora}</p>
              <p class="mb-1"><strong>Personas:</strong> ${reserva.num_personas}</p>
              <p class="mb-0"><span class="badge ${reserva.estado === 'Confirmada' ? 'bg-success' : 'bg-warning'}">${reserva.estado}</span></p>
            </div>
          </div>
        </div>
      `).join('');
    }
  }
  
  // CLIENT AREA PAGE
  // Check if client is already logged in
  const loggedClientArea = sessionStorage.getItem('currentClient');
  if (loggedClientArea && window.location.pathname === '/clients') {
    const cliente = JSON.parse(loggedClientArea);
    await mostrarDatosCliente(cliente);
    // Hide login form
    const searchCard = document.getElementById('clientSearchForm')?.closest('.card');
    if (searchCard) searchCard.style.display = 'none';
  }

  const clientSearchForm = document.getElementById('clientSearchForm');
  if (clientSearchForm) {
    clientSearchForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const id = document.getElementById('clientId').value.trim();
      
      if (!id) {
        alert('Por favor ingresa tu ID de cliente');
        return;
      }
      
      try {
        const response = await fetch(`/api/clientes/buscar?id=${encodeURIComponent(id)}`);
        const data = await response.json();
        
        if (data.clientes && data.clientes.length > 0) {
          const cliente = data.clientes[0];
          await mostrarDatosCliente(cliente);
          // Hide login form after successful login
          const searchCard = clientSearchForm.closest('.card');
          if (searchCard) searchCard.style.display = 'none';
        } else {
          document.getElementById('clientResults').style.display = 'none';
          document.getElementById('noResults').style.display = 'block';
        }
      } catch (error) {
        console.error('Error:', error);
        alert('Error al buscar cliente');
      }
    });
  }
  
  async function mostrarDatosCliente(cliente) {
    // Guardar cliente actual en sessionStorage
    sessionStorage.setItem('currentClient', JSON.stringify(cliente));
    
    // Show client info
    document.getElementById('clientInfo').innerHTML = `
      <div class="row">
        <div class="col-md-6">
          <p class="mb-2"><strong>Nombre:</strong> ${cliente.nombre}</p>
          <p class="mb-2"><strong>ID:</strong> ${cliente.id}</p>
          <p class="mb-2"><strong>Email:</strong> ${cliente.email || 'No disponible'}</p>
        </div>
        <div class="col-md-6">
          <p class="mb-2"><strong>Teléfono:</strong> ${cliente.telefono}</p>
          <p class="mb-2"><strong>Edad:</strong> ${cliente.edad} años</p>
          <p class="mb-2"><strong>Estudios:</strong> ${cliente.estudios}</p>
        </div>
      </div>
    `;
    
    // Fetch reservas
    const reservasResponse = await fetch(`/api/reservas/${cliente.id}`);
    const reservasData = await reservasResponse.json();
    const reservas = reservasData.reservas || [];
    
    // Fetch facturas
    const facturasResponse = await fetch(`/api/facturas/${cliente.id}`);
    const facturasData = await facturasResponse.json();
    const facturas = facturasData.facturas || [];
    
    // Crear un mapa de facturas por ID_RESERVA
    const facturasMap = {};
    facturas.forEach(f => {
      if (f.id_reserva) {
        facturasMap[f.id_reserva] = f;
      }
    });
    
    // Fetch reseñas del cliente
    const resenasResponse = await fetch(`/api/resenas/${cliente.id}`);
    const resenasData = await resenasResponse.json();
    const resenas = resenasData.resenas || [];
    
    console.log('Reseñas obtenidas:', resenas);
    
    // Crear un mapa de reseñas por restaurante
    const resenasMap = {};
    resenas.forEach(r => {
      // Usar directamente el id_restaurante de la reseña
      resenasMap[r.id_restaurante] = r;
    });
    
    console.log('Mapa de reseñas:', resenasMap);
    console.log('Mapa de facturas:', facturasMap);
    
    // Update stats
    document.getElementById('totalReservas').textContent = reservas.length;
    document.getElementById('totalFacturas').textContent = facturas.length;
    const totalGastado = facturas.reduce((sum, f) => sum + f.precio, 0);
    document.getElementById('totalGastado').textContent = totalGastado.toFixed(2) + '€';
    
    // Render reservas
    const reservasContainer = document.getElementById('clientReservas');
    if (reservas.length === 0) {
      reservasContainer.innerHTML = '<div class="col-12"><p class="text-muted-custom">No hay reservas registradas.</p></div>';
    } else {
      const hoy = new Date();
      hoy.setHours(0, 0, 0, 0);
      
      reservasContainer.innerHTML = reservas.map(reserva => {
        // Normalizar formato de fecha - eliminar posibles horas si vienen en el string
        let fechaStr = reserva.fecha;
        if (fechaStr && fechaStr.includes(' ')) {
          fechaStr = fechaStr.split(' ')[0]; // Tomar solo la parte de la fecha
        }
        
        const fechaReserva = new Date(fechaStr + 'T00:00:00');
        const esFechaPasada = fechaReserva < hoy;
        const resenaExistente = resenasMap[reserva.id_restaurante];
        const facturaExistente = facturasMap[reserva.id_reserva];
        
        // Verificar si la factura tiene valoración
        const tieneValoracion = facturaExistente && facturaExistente.valoracion !== null && facturaExistente.valoracion !== undefined;
        
        console.log(`Reserva: ${reserva.restaurante_nombre}, Fecha original: "${reserva.fecha}", Fecha normalizada: "${fechaStr}", Fecha parseada: ${fechaReserva}, Hoy: ${hoy}, Es pasada: ${esFechaPasada}, Tiene factura:`, facturaExistente, 'Tiene valoración:', tieneValoracion);
        
        return `
          <div class="col">
            <div class="card h-100" style="background: var(--glass-bg); border: 1px solid var(--glass-border);">
              <div class="card-body">
                <h5 class="card-title">${reserva.restaurante_nombre}</h5>
                <p class="text-muted-custom mb-2"><small>${reserva.restaurante_ciudad}</small></p>
                <p class="mb-1"><strong>Fecha:</strong> ${reserva.fecha} - ${reserva.hora}</p>
                <p class="mb-1"><strong>Personas:</strong> ${reserva.num_personas}</p>
                <p class="mb-2">
                  <span class="badge ${reserva.estado === 'CONFIRMADA' || reserva.estado === 'Confirmada' ? 'bg-success' : reserva.estado === 'CANCELADA' || reserva.estado === 'Cancelada' ? 'bg-danger' : 'bg-warning'}">
                    ${reserva.estado}
                  </span>
                  ${esFechaPasada ? '<span class="badge bg-secondary ms-2">Pasada</span>' : ''}
                  ${facturaExistente ? '<span class="badge bg-info ms-2">Con Factura</span>' : ''}
                </p>
                ${!esFechaPasada ? `
                  <button class="btn btn-sm btn-primary w-100" onclick="abrirModalEditar('${reserva.id_reserva}', '${reserva.restaurante_nombre}', '${reserva.fecha}', '${reserva.hora}', ${reserva.num_personas})">
                    ✏️ Modificar Reserva
                  </button>
                ` : `
                  <div class="d-grid gap-2">
                    ${!facturaExistente ? `
                      <button class="btn btn-sm btn-info" onclick="pedirFacturaFicticio()">
                        📄 Pedir Factura
                      </button>
                    ` : tieneValoracion ? `
                      <div class="alert alert-success mb-0 py-2">
                        <small><strong>✅ Ya valorado:</strong></small><br>
                        <span style="font-size: 1.2rem;">${'⭐'.repeat(Math.round(facturaExistente.valoracion))}</span>
                        <small class="d-block mt-1">${facturaExistente.tipo_visita || 'N/A'}</small>
                      </div>
                    ` : `
                      <button class="btn btn-sm btn-warning" onclick="abrirModalValorarFactura('${facturaExistente.id_factura}', '${reserva.id_reserva}', '${reserva.id_restaurante}', '${reserva.restaurante_nombre}')">
                        ⭐ Valorar Restaurante
                      </button>
                    `}
                  </div>
                `}
              </div>
            </div>
          </div>
        `;
      }).join('');
    }
    
    // Render facturas
    const facturasContainer = document.getElementById('clientFacturas');
    if (facturas.length === 0) {
      facturasContainer.innerHTML = '<p class="text-muted-custom">No hay facturas registradas.</p>';
    } else {
      facturasContainer.innerHTML = `
        <div class="table-responsive">
          <table class="table table-hover" style="background: var(--glass-bg);">
            <thead>
              <tr>
                <th>ID Factura</th>
                <th>Restaurante</th>
                <th>Fecha</th>
                <th>Tipo Visita</th>
                <th>Precio</th>
                <th>Valoración</th>
              </tr>
            </thead>
            <tbody>
              ${facturas.map(f => {
                const tieneValoracion = f.valoracion !== null && f.valoracion !== undefined;
                const stars = tieneValoracion ? '⭐'.repeat(Math.round(f.valoracion)) : '';
                const botonValorar = !tieneValoracion ? 
                  `<button class="btn btn-sm btn-warning" onclick="abrirModalValorarFactura('${f.id_factura}', '${f.id_reserva}', '${f.id_restaurante}', '${f.restaurante_nombre}')">⭐ Valorar</button>` 
                  : stars;
                
                return `
                  <tr>
                    <td><code>${f.id_factura}</code></td>
                    <td>${f.restaurante_nombre}<br><small class="text-muted-custom">${f.restaurante_ciudad}</small></td>
                    <td>${f.fecha}</td>
                    <td><span class="badge bg-secondary">${f.tipo_visita || 'N/A'}</span></td>
                    <td><strong>${f.precio.toFixed(2)}€</strong></td>
                    <td>${botonValorar}</td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      `;
    }
    
    document.getElementById('clientResults').style.display = 'block';
    document.getElementById('noResults').style.display = 'none';
  }
  
  // BOOKING PAGE - CLIENT VALIDATION & REGISTRATION
  // Check if client is already logged in
  const loggedClient = sessionStorage.getItem('currentClient');
  if (loggedClient && window.location.pathname === '/book') {
    const cliente = JSON.parse(loggedClient);
    state.currentClientId = cliente.id;
    // Skip to step 2 directly if elements exist
    if (document.getElementById('step1') && document.getElementById('step2')) {
      setTimeout(() => goToStep2WithClient(cliente), 100);
    }
  }

  const validateClientForm = document.getElementById('validateClientForm');
  const clientRegisterForm = document.getElementById('clientRegisterForm');
  const bookingForm = document.getElementById('bookingForm');
  
  // Show/hide register form
  window.showRegisterForm = function() {
    document.getElementById('registerForm').style.display = 'block';
  };
  
  window.hideRegisterForm = function() {
    document.getElementById('registerForm').style.display = 'none';
    if (clientRegisterForm) clientRegisterForm.reset();
  };
  
  // Back to step 1
  window.backToStep1 = function() {
    document.getElementById('step1').style.display = 'block';
    document.getElementById('step2').style.display = 'none';
    document.querySelector('.step-item:nth-child(1) .step-number').classList.add('active');
    document.querySelector('.step-item:nth-child(2) .step-number').classList.remove('active');
    state.currentClientId = null;
  };

  // Function to go to step 2 with logged client
  window.goToStep2WithClient = function(cliente) {
    state.currentClientId = cliente.id;
    
    const clientInfoDiv = document.getElementById('clientInfo');
    if (clientInfoDiv) {
      clientInfoDiv.innerHTML = `
        <strong>${cliente.nombre}</strong> (${cliente.id})<br>
        Ya tienes sesión iniciada. 
        <button class="btn btn-sm btn-link p-0" onclick="cerrarSesionYVolver()">Cambiar cliente</button>
      `;
    }
    
    // Show step 2
    document.getElementById('step1').style.display = 'none';
    document.getElementById('step2').style.display = 'block';
    document.querySelector('.step-item:nth-child(1) .step-number').classList.remove('active');
    document.querySelector('.step-item:nth-child(2) .step-number').classList.add('active');
  };

  // Logout function for booking page
  window.cerrarSesionYVolver = function() {
    if (confirm('¿Cerrar sesión y cambiar de cliente?')) {
      sessionStorage.removeItem('currentClient');
      window.location.reload();
    }
  };

  // FUNCIONES PARA EDITAR/CANCELAR RESERVAS
  window.abrirModalEditar = function(idReserva, restaurante, fecha, hora, personas) {
    // Validar que la fecha no sea pasada
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    const fechaReserva = new Date(fecha + 'T00:00:00');
    
    if (fechaReserva < hoy) {
      alert('⚠️ No se pueden modificar reservas con fecha anterior a hoy.\n\nSolo puedes modificar reservas futuras.');
      return;
    }
    
    document.getElementById('editReservaId').value = idReserva;
    document.getElementById('editRestaurante').textContent = restaurante;
    document.getElementById('editFecha').value = fecha;
    document.getElementById('editHora').value = hora;
    document.getElementById('editPersonas').value = personas;
    
    // Establecer la fecha mínima como hoy
    const inputFecha = document.getElementById('editFecha');
    inputFecha.min = hoy.toISOString().split('T')[0];
    
    const modal = new bootstrap.Modal(document.getElementById('editReservaModal'));
    modal.show();
  };

  window.cancelarReserva = async function() {
    if (!confirm('¿Estás seguro de que deseas cancelar esta reserva?')) {
      return;
    }
    
    const idReserva = document.getElementById('editReservaId').value;
    
    try {
      const response = await fetch(`/api/reservas/cancel/${idReserva}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (response.ok) {
        alert('Reserva cancelada exitosamente');
        const modal = bootstrap.Modal.getInstance(document.getElementById('editReservaModal'));
        modal.hide();
        // Recargar solo los datos del cliente actual
        const clienteActual = JSON.parse(sessionStorage.getItem('currentClient'));
        if (clienteActual) {
          await mostrarDatosCliente(clienteActual);
        }
      } else {
        alert('Error: ' + data.mensaje);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error al cancelar la reserva');
    }
  };

  // Handler para el formulario de edición
  const editReservaForm = document.getElementById('editReservaForm');
  if (editReservaForm) {
    editReservaForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      const fechaSeleccionada = document.getElementById('editFecha').value;
      const hoy = new Date();
      hoy.setHours(0, 0, 0, 0);
      const fechaReserva = new Date(fechaSeleccionada + 'T00:00:00');
      
      if (fechaReserva < hoy) {
        alert('La fecha de la reserva no puede ser anterior a hoy');
        return;
      }
      
      const idReserva = document.getElementById('editReservaId').value;
      const reservaData = {
        fecha: fechaSeleccionada,
        hora: document.getElementById('editHora').value,
        num_personas: parseInt(document.getElementById('editPersonas').value)
      };
      
      try {
        const response = await fetch(`/api/reservas/update/${idReserva}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(reservaData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
          alert('Reserva actualizada exitosamente');
          const modal = bootstrap.Modal.getInstance(document.getElementById('editReservaModal'));
          modal.hide();
          // Recargar solo los datos del cliente actual
          const clienteActual = JSON.parse(sessionStorage.getItem('currentClient'));
          if (clienteActual) {
            await mostrarDatosCliente(clienteActual);
          }
        } else {
          alert('Error: ' + data.mensaje);
        }
      } catch (error) {
        console.error('Error:', error);
        alert('Error al actualizar la reserva');
      }
    });
  }
  
  // Validate existing client
  if (validateClientForm) {
    validateClientForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const clientId = document.getElementById('clientId').value.trim();
      
      if (!clientId) {
        return;
      }
      
      try {
        const response = await fetch(`/api/clientes/buscar?id=${clientId}`);
        const data = await response.json();
        
        if (data.clientes && data.clientes.length > 0) {
          const cliente = data.clientes[0];
          state.currentClientId = cliente.id;
          
          // Show client info and move to step 2
          document.getElementById('clientInfo').innerHTML = `
            <strong>Cliente:</strong> ${cliente.nombre} (${cliente.id})<br>
            <strong>Email:</strong> ${cliente.email} | <strong>Teléfono:</strong> ${cliente.telefono}
          `;
          
          document.getElementById('step1').style.display = 'none';
          document.getElementById('step2').style.display = 'block';
          document.querySelector('.step-item:nth-child(1) .step-number').classList.remove('active');
          document.querySelector('.step-item:nth-child(2) .step-number').classList.add('active');
        } else {
          // Cliente no existe, mostrar formulario de registro automáticamente
          showRegisterForm();
          // Pre-rellenar el ID en el formulario de registro
          document.getElementById('regClientId').value = clientId;
        }
      } catch (error) {
        console.error('Error:', error);
      }
    });
  }
  
  // Register new client
  if (clientRegisterForm) {
    clientRegisterForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      const clientData = {
        ID_CLIENTE: document.getElementById('regClientId').value.trim(),
        N_CLIENTE: document.getElementById('regNombre').value.trim(),
        NUM_TELEFONO: document.getElementById('regTelefono').value.trim(),
        EMAIL: document.getElementById('regEmail').value.trim(),
        EDAD: parseInt(document.getElementById('regEdad').value),
        SEXO: document.getElementById('regSexo').value,
        ESTUDIOS: document.getElementById('regEstudios').value
      };
      
      const submitBtn = clientRegisterForm.querySelector('button[type="submit"]');
      submitBtn.disabled = true;
      submitBtn.textContent = 'Registrando...';
      
      try {
        console.log('Enviando datos:', clientData);
        const response = await fetch('/clientes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(clientData)
        });
        
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        
        const data = await response.json();
        console.log('Response data:', data);
        
        // Si la respuesta es OK (status 200), consideramos que fue exitoso
        if (response.ok && response.status === 200) {
          state.currentClientId = clientData.ID_CLIENTE;
          
          // Show client info and move to step 2
          document.getElementById('clientInfo').innerHTML = `
            <strong>Cliente:</strong> ${clientData.N_CLIENTE} (${clientData.ID_CLIENTE})<br>
            <strong>Email:</strong> ${clientData.EMAIL} | <strong>Teléfono:</strong> ${clientData.NUM_TELEFONO}
          `;
          
          document.getElementById('step1').style.display = 'none';
          document.getElementById('step2').style.display = 'block';
          document.querySelector('.step-item:nth-child(1) .step-number').classList.remove('active');
          document.querySelector('.step-item:nth-child(2) .step-number').classList.add('active');
          hideRegisterForm();
        } else {
          console.error('Error en respuesta:', data);
          alert('Error: ' + (data.mensaje || 'No se pudo registrar el cliente'));
        }
      } catch (error) {
        console.error('Error catch:', error);
        alert('Error al registrar cliente: ' + error.message);
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Registrar y Continuar';
      }
    });
  }
  
  // BOOKING FORM - Step 2
  if (bookingForm) {
    const selectedRest = sessionStorage.getItem('selectedRestaurant');
    const restaurantes = await fetchRestaurantes();
    const select = document.getElementById('restaurante');
    
    if (select) {
      if (selectedRest) {
        const rest = JSON.parse(selectedRest);
        select.innerHTML = restaurantes.map(r => `<option value="${r.id}" ${r.id === rest.id ? 'selected' : ''}>${r.nombre}</option>`).join('');
        sessionStorage.removeItem('selectedRestaurant');
      } else {
        select.innerHTML = '<option value="">Seleccione un restaurante</option>' + restaurantes.map(r => `<option value="${r.id}">${r.nombre}</option>`).join('');
      }
    }
    
    bookingForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      if (!state.currentClientId) {
        alert('Error: No hay cliente validado');
        backToStep1();
        return;
      }
      
      const formData = {
        id_cliente: state.currentClientId,
        id_restaurante: document.getElementById('restaurante').value,
        num_personas: parseInt(document.getElementById('personas').value),
        fecha: document.getElementById('fecha').value,
        hora: document.getElementById('hora').value
      };
      
      const submitBtn = bookingForm.querySelector('button[type="submit"]');
      submitBtn.disabled = true;
      submitBtn.textContent = 'Procesando...';
      
      const result = await crearReserva(formData);
      submitBtn.disabled = false;
      submitBtn.textContent = 'Confirmar Reserva';
      
      if (result.id_reserva) {
        alert('¡Reserva confirmada exitosamente!\n\nSerás redirigido a tu área personal.');
        // Redirigir al área de cliente
        window.location.href = '/clients';
      } else {
        alert('Error: ' + result.mensaje);
      }
    });
  }

  // FUNCIONES PARA VALORAR RESTAURANTE
  let ratingSelected = 0;

  window.setRating = function(stars) {
    ratingSelected = stars;
    document.getElementById('valoracion').value = stars;
    
    // Update star display
    const starElements = document.querySelectorAll('#starRating .star');
    starElements.forEach((star, index) => {
      if (index < stars) {
        star.textContent = '⭐';
        star.style.color = '#FFD700';
        star.style.textShadow = '0 0 5px rgba(255,215,0,0.5)';
      } else {
        star.textContent = '☆';
        star.style.color = '#FFD700';
        star.style.textShadow = '0 0 3px rgba(0,0,0,0.3)';
      }
    });
  };

  window.abrirModalValorar = function(idReserva, idRestaurante, nombreRestaurante) {
    document.getElementById('valorarReservaId').value = idReserva;
    document.getElementById('valorarRestauranteId').value = idRestaurante;
    document.getElementById('valorarRestaurante').textContent = nombreRestaurante;
    
    // Reset rating
    ratingSelected = 0;
    document.getElementById('valoracion').value = '';
    document.getElementById('tipoVisita').value = 'PAREJA';
    const starElements = document.querySelectorAll('#starRating .star');
    starElements.forEach(star => {
      star.textContent = '☆';
      star.style.color = '#FFD700';
      star.style.textShadow = '0 0 3px rgba(0,0,0,0.3)';
    });
    
    const modal = new bootstrap.Modal(document.getElementById('valorarModal'));
    modal.show();
  };

  // Función para valorar desde la tabla de facturas
  window.abrirModalValorarFactura = function(idFactura, idReserva, idRestaurante, nombreRestaurante) {
    document.getElementById('valorarReservaId').value = idReserva || '';
    document.getElementById('valorarRestauranteId').value = idRestaurante;
    document.getElementById('valorarRestaurante').textContent = nombreRestaurante;
    
    // Guardar el ID de factura para actualización directa
    document.getElementById('valorarForm').dataset.facturaId = idFactura;
    
    // Reset rating
    ratingSelected = 0;
    document.getElementById('valoracion').value = '';
    document.getElementById('tipoVisita').value = 'PAREJA';
    const starElements = document.querySelectorAll('#starRating .star');
    starElements.forEach(star => {
      star.textContent = '☆';
      star.style.color = '#FFD700';
      star.style.textShadow = '0 0 3px rgba(0,0,0,0.3)';
    });
    
    const modal = new bootstrap.Modal(document.getElementById('valorarModal'));
    modal.show();
  };

  const valorarForm = document.getElementById('valorarForm');
  if (valorarForm) {
    valorarForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      if (!ratingSelected || ratingSelected < 1) {
        alert('Por favor selecciona una valoración (estrellas)');
        return;
      }
      
      const clienteActual = JSON.parse(sessionStorage.getItem('currentClient'));
      if (!clienteActual) {
        alert('Error: No se encontró el cliente');
        return;
      }
      
      const valoracionData = {
        id_cliente: clienteActual.id,
        id_restaurante: document.getElementById('valorarRestauranteId').value,
        valoracion: ratingSelected,
        tipo_visita: document.getElementById('tipoVisita').value
      };
      
      try {
        const response = await fetch('/api/resenas', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(valoracionData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
          alert('¡Valoración enviada exitosamente! Gracias por tu opinión.');
          const modal = bootstrap.Modal.getInstance(document.getElementById('valorarModal'));
          modal.hide();
          // Recargar datos del cliente para mostrar la valoración
          if (clienteActual) {
            await mostrarDatosCliente(clienteActual);
          }
        } else {
          alert('Error: ' + data.mensaje);
        }
      } catch (error) {
        console.error('Error:', error);
        alert('Error al enviar la valoración');
      }
    });
  }

  // Editar Cliente Form
  const editClienteForm = document.getElementById('editClienteForm');
  if (editClienteForm) {
    editClienteForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      const clienteId = document.getElementById('editClienteId').value;
      const clienteData = {
        nombre: document.getElementById('editClienteNombre').value,
        email: document.getElementById('editClienteEmail').value,
        telefono: document.getElementById('editClienteTelefono').value,
        edad: parseInt(document.getElementById('editClienteEdad').value),
        estudios: document.getElementById('editClienteEstudios').value
      };
      
      try {
        const response = await fetch(`/api/clientes/${clienteId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(clienteData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
          alert('Datos actualizados correctamente');
          const modal = bootstrap.Modal.getInstance(document.getElementById('editClienteModal'));
          modal.hide();
          // Recargar datos del cliente
          const clienteActualizado = {
            id: clienteId,
            nombre: clienteData.nombre,
            email: clienteData.email,
            telefono: clienteData.telefono,
            edad: clienteData.edad,
            estudios: clienteData.estudios
          };
          await mostrarDatosCliente(clienteActualizado);
        } else {
          alert('Error: ' + data.mensaje);
        }
      } catch (error) {
        console.error('Error:', error);
        alert('Error al actualizar los datos');
      }
    });
  }
});

// Función para abrir modal de editar cliente
function abrirModalEditarCliente() {
  const clienteActual = JSON.parse(sessionStorage.getItem('currentClient'));
  if (!clienteActual) {
    alert('Error: No se encontró el cliente');
    return;
  }
  
  document.getElementById('editClienteId').value = clienteActual.id;
  document.getElementById('editClienteNombre').value = clienteActual.nombre;
  document.getElementById('editClienteEmail').value = clienteActual.email || '';
  document.getElementById('editClienteTelefono').value = clienteActual.telefono;
  document.getElementById('editClienteEdad').value = clienteActual.edad;
  document.getElementById('editClienteEstudios').value = clienteActual.estudios;
  
  const modal = new bootstrap.Modal(document.getElementById('editClienteModal'));
  modal.show();
}

// Función para cerrar sesión
window.cerrarSesion = function() {
  if (confirm('¿Estás seguro de que quieres cerrar sesión?')) {
    sessionStorage.removeItem('currentClient');
    window.location.reload();
  }
};

// Función para eliminar cliente
async function eliminarCliente() {
  const clienteActual = JSON.parse(sessionStorage.getItem('currentClient'));
  if (!clienteActual) {
    alert('Error: No se encontró el cliente');
    return;
  }
  
  // Primera confirmación
  const confirmacion = confirm(
    `⚠️ ADVERTENCIA: ¿Estás seguro de que quieres eliminar tu cuenta?\n\n` +
    `Esta acción eliminará:\n` +
    `✗ Tu información personal\n` +
    `✗ Todas tus reservas\n` +
    `✗ Todas tus facturas\n` +
    `✗ Todas tus reseñas\n\n` +
    `⚠️ ESTA ACCIÓN NO SE PUEDE DESHACER ⚠️`
  );
  
  if (!confirmacion) {
    return;
  }
  
  // Segunda confirmación con validación de texto
  const textoConfirmacion = prompt(
    `Para confirmar la eliminación de la cuenta de:\n${clienteActual.nombre} (${clienteActual.id})\n\n` +
    `Por favor escribe exactamente: ELIMINAR`
  );
  
  if (textoConfirmacion === 'ELIMINAR') {
    try {
      const response = await fetch(`/api/clientes/${clienteActual.id}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (response.ok) {
        alert('Cuenta eliminada correctamente');
        sessionStorage.removeItem('currentClient');
        // Recargar la página para volver al formulario de búsqueda
        window.location.reload();
      } else {
        alert('Error: ' + data.mensaje);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error al eliminar la cuenta');
    }
  }
}

// Función para pedir factura de una reserva
// Función ficticia para pedir factura (solo aviso)
window.pedirFacturaFicticio = function() {
  alert('📄 Tu solicitud de factura ha sido enviada.\n\nRecibirás la factura por email en las próximas 24-48 horas.');
};

async function pedirFactura(idReserva) {
  const clienteActual = JSON.parse(sessionStorage.getItem('currentClient'));
  if (!clienteActual) {
    alert('Error: No se encontró el cliente');
    return;
  }
  
  const confirmacion = confirm('¿Deseas solicitar la factura para esta reserva?');
  if (!confirmacion) {
    return;
  }
  
  try {
    const response = await fetch(`/api/reservas/${idReserva}/factura`, {
      method: 'POST'
    });
    
    const data = await response.json();
    
    if (response.ok) {
      alert(`Factura generada correctamente!\n\nID Factura: ${data.id_factura}\nImporte: ${data.precio}€`);
      // Recargar datos del cliente para mostrar la factura
      await mostrarDatosCliente(clienteActual);
    } else {
      alert('Error: ' + data.mensaje);
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Error al generar la factura');
  }
}
