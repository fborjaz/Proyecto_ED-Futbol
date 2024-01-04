document.getElementById('nombre_equipo').addEventListener('change', function (event) {
    event.preventDefault();  // Evitar que el formulario se envíe automáticamente

    var selectedTeam = this.value;

    // Realizar solicitud AJAX para obtener información de jugadores
    fetch('/obtener_info_jugadores', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'nombre_equipo': selectedTeam })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('No se pudo obtener la información de los jugadores');
            }
            return response.json();
        })
        .then(data => {
            actualizarJugadores(data.jugadores);
        })
        .catch(error => {
            console.error('Error:', error.message);
        });
});

function actualizarJugadores(jugadores) {
    var playersContainer = document.getElementById('jugadores-container');
    var playersHTML = '';

    jugadores.forEach(jugador => {
        playersHTML += `<div class="form-group">
                            <h4>${jugador.nombre} (Camiseta ${jugador.numero_camiseta}, Posición: ${jugador.posicion})</h4>
                            <label for="goles_${jugador.numero_camiseta}">Goles</label>
                            <input type="number" class="form-control" id="goles_${jugador.numero_camiseta}" name="goles_${jugador.numero_camiseta}" placeholder="Goles">
                            <label for="remates_al_arco_${jugador.numero_camiseta}">Remates al arco</label>
                            <input type="number" class="form-control" id="remates_al_arco_${jugador.numero_camiseta}" name="remates_al_arco_${jugador.numero_camiseta}" placeholder="Remates al arco">
                            <label for="asistencias_${jugador.numero_camiseta}">Asistencias</label>
                            <input type="number" class="form-control" id="asistencias_${jugador.numero_camiseta}" name="asistencias_${jugador.numero_camiseta}" placeholder="Asistencias">
                            <label for="tarjetas_amarillas_${jugador.numero_camiseta}">Tarjetas amarillas</label>
                            <input type="number" class="form-control" id="tarjetas_amarillas_${jugador.numero_camiseta}" name="tarjetas_amarillas_${jugador.numero_camiseta}" placeholder="Tarjetas amarillas">
                            <label for="tarjetas_rojas_${jugador.numero_camiseta}">Tarjetas rojas</label>
                            <input type="number" class="form-control" id="tarjetas_rojas_${jugador.numero_camiseta}" name="tarjetas_rojas_${jugador.numero_camiseta}" placeholder="Tarjetas rojas">
                        </div>`;
    });

    // Actualizar el contenido de jugadores-container
    playersContainer.innerHTML = playersHTML;
}
