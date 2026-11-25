// Gráficos do dashboard. Os dados chegam da view via json_script.
(function () {
    function lerDados(id) {
        const el = document.getElementById(id);
        return el ? JSON.parse(el.textContent) : [];
    }

    // Se o Chart.js não carregou (sem internet, CDN bloqueado), a página segue funcionando.
    if (typeof Chart === 'undefined') {
        return;
    }

    const porMes = lerDados('dados-mes');
    const canvasMes = document.getElementById('grafico-mes');
    if (canvasMes && porMes.length) {
        new Chart(canvasMes, {
            type: 'bar',
            data: {
                labels: porMes.map(d => d.mes),
                datasets: [{
                    label: 'Livros cadastrados',
                    data: porMes.map(d => d.total),
                    backgroundColor: '#2c3e50'
                }]
            },
            options: {
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }
            }
        });
    }

    const porCategoria = lerDados('dados-categoria');
    const canvasCategoria = document.getElementById('grafico-categoria');
    if (canvasCategoria && porCategoria.length) {
        new Chart(canvasCategoria, {
            type: 'bar',
            data: {
                labels: porCategoria.map(d => d.rotulo),
                datasets: [{
                    label: 'Livros',
                    data: porCategoria.map(d => d.total),
                    backgroundColor: '#3b6ea5'
                }]
            },
            options: {
                indexAxis: 'y',
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { x: { beginAtZero: true, ticks: { precision: 0 } } }
            }
        });
    }
})();
