function mudarEstado() {
    const toggle = document.getElementById('controleRele');
    const estado = toggle.checked ? 'on' : 'off';
    
    fetch('/controle', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `estado=${estado}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Atualiza visualmente após mudança bem-sucedida
            atualizarStatusRele(toggle.checked ? 'ligado' : 'desligado');
        } else {
            toggle.checked = !toggle.checked; // Reverte se houver erro
            alert('Erro ao alterar estado do relé');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        toggle.checked = !toggle.checked;
    });
}

// Função para atualizar periodicamente o estado (opcional)
function atualizarEstado() {
    fetch('/estado')
        .then(response => response.json())
        .then(data => {
            const toggle = document.getElementById('controleRele');
            // Só atualiza se o usuário não estiver interagindo
            if (document.activeElement !== toggle) {
                toggle.checked = data.rele === 'ligado';
            }
        });
}

function atualizarStatusRele(estado) {
    const statusElement = document.getElementById('statusRele');
    
    if (estado === 'ligado') {
        statusElement.textContent = 'Ligado';
        statusElement.className = 'badge bg-success'; // Verde
    } else {
        statusElement.textContent = 'Desligado';
        statusElement.className = 'badge bg-danger';  // Vermelho
    }
}
function verificarEstadoRele() {
    fetch('/estado')
        .then(response => response.json())
        .then(data => {
            const toggle = document.getElementById('controleRele');

            // Atualiza o toggle switch
            if (document.activeElement !== toggle) {
                toggle.checked = data.rele === 'ligado';
            }

            // Atualiza o status visual
            atualizarStatusRele(data.rele);
        })
        .catch(error => console.error('Erro:', error));
}

// Chama ao carregar a página
document.addEventListener('DOMContentLoaded', verificarEstadoRele);

// Atualiza periodicamente (a cada 3 segundos)
setInterval(verificarEstadoRele, 3000);
