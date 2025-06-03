// Función para copiar la tabla al portapapeles
function copyTable() {
    const table = document.getElementById('dataTable');
    const range = document.createRange();
    range.selectNode(table);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);
    
    try {
        document.execCommand('copy');
        showNotification('Tabla copiada al portapapeles', 'success');
    } catch (err) {
        showNotification('Error al copiar la tabla', 'error');
    }
    
    window.getSelection().removeAllRanges();
}

// Función para descargar la tabla como CSV
function downloadCSV() {
    const table = document.getElementById('dataTable');
    const rows = table.querySelectorAll('tr');
    let csvContent = '';
    
    // Recorrer todas las filas
    rows.forEach((row, index) => {
        const cells = row.querySelectorAll('th, td');
        const rowData = [];
        
        cells.forEach((cell, cellIndex) => {
            // Excluir la última columna (botón Ver) del CSV
            if (cellIndex < cells.length - 1) {
                let cellText = cell.textContent.trim();
                // Escapar comillas dobles
                cellText = cellText.replace(/"/g, '""');
                // Envolver en comillas si contiene comas o saltos de línea
                if (cellText.includes(',') || cellText.includes('\n') || cellText.includes('"')) {
                    cellText = `"${cellText}"`;
                }
                rowData.push(cellText);
            }
        });
        
        csvContent += rowData.join(',') + '\n';
    });
    
    // Crear el archivo y descargarlo
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', 'tramites.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showNotification('CSV descargado exitosamente', 'success');
}

// Función para imprimir la tabla
function printTable() {
    const table = document.getElementById('dataTable').cloneNode(true);
    
    // Remover la columna de acciones (Ver) de la tabla clonada
    const headerRow = table.querySelector('thead tr');
    const lastHeaderCell = headerRow.lastElementChild;
    if (lastHeaderCell) {
        lastHeaderCell.remove();
    }
    
    const bodyRows = table.querySelectorAll('tbody tr');
    bodyRows.forEach(row => {
        const lastCell = row.lastElementChild;
        if (lastCell) {
            lastCell.remove();
        }
    });
    
    // Crear ventana de impresión
    const printWindow = window.open('', '_blank');
    const clasificacionNombre = document.querySelector('h1').textContent;
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Trámites - ${clasificacionNombre}</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    color: #333;
                }
                h1 {
                    text-align: center;
                    color: #2d3748;
                    margin-bottom: 20px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                    font-size: 12px;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #f7fafc;
                    font-weight: bold;
                    color: #2d3748;
                }
                .status-badge {
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: bold;
                }
                .status-active {
                    background-color: #c6f6d5;
                    color: #22543d;
                }
                .status-inactive {
                    background-color: #fed7d7;
                    color: #742a2a;
                }
                @media print {
                    body { margin: 0; }
                    table { font-size: 10px; }
                }
            </style>
        </head>
        <body>
            <h1>Trámites - ${clasificacionNombre}</h1>
            ${table.outerHTML}
            <p style="margin-top: 20px; font-size: 10px; color: #666;">
                Impreso el: ${new Date().toLocaleString('es-MX')}
            </p>
        </body>
        </html>
    `);
    
    printWindow.document.close();
    
    // Esperar a que se cargue el contenido antes de imprimir
    setTimeout(() => {
        printWindow.print();
        printWindow.close();
    }, 500);
}

// Función para filtrar la tabla (búsqueda)
function filterTable() {
    const searchInput = document.getElementById('search');
    const searchTerm = searchInput.value.toLowerCase();
    const tableBody = document.getElementById('tableBody');
    const rows = tableBody.querySelectorAll('tr');
    let visibleRows = 0;
    
    rows.forEach(row => {
        // Evitar filtrar la fila de "no hay trámites"
        if (row.cells.length === 1 && row.cells[0].getAttribute('colspan')) {
            return;
        }
        
        const cells = row.querySelectorAll('td');
        let found = false;
        
        // Buscar en todas las celdas excepto la última (botón Ver)
        for (let i = 0; i < cells.length - 1; i++) {
            if (cells[i].textContent.toLowerCase().includes(searchTerm)) {
                found = true;
                break;
            }
        }
        
        if (found) {
            row.style.display = '';
            visibleRows++;
            // Actualizar el número de fila
            row.querySelector('.row-number').textContent = visibleRows;
        } else {
            row.style.display = 'none';
        }
    });
    
    updatePaginationInfo(visibleRows);
}

// Función para ordenar la tabla
function sortTable(columnIndex) {
    const table = document.getElementById('dataTable');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr')).filter(row => 
        !(row.cells.length === 1 && row.cells[0].getAttribute('colspan'))
    );
    
    // Determinar dirección de ordenamiento
    const header = table.querySelectorAll('th')[columnIndex];
    const sortIcon = header.querySelector('.sort-icon');
    const isAscending = sortIcon.textContent === '↕' || sortIcon.textContent === '↓';
    
    // Resetear todos los iconos
    table.querySelectorAll('.sort-icon').forEach(icon => icon.textContent = '↕');
    
    // Establecer icono de la columna actual
    sortIcon.textContent = isAscending ? '↑' : '↓';
    
    // Ordenar filas
    rows.sort((a, b) => {
        let aValue = a.cells[columnIndex].textContent.trim();
        let bValue = b.cells[columnIndex].textContent.trim();
        
        // Ordenamiento numérico para la primera columna
        if (columnIndex === 0) {
            aValue = parseInt(aValue);
            bValue = parseInt(bValue);
        }
        
        if (aValue < bValue) return isAscending ? -1 : 1;
        if (aValue > bValue) return isAscending ? 1 : -1;
        return 0;
    });
    
    // Reordenar filas en el DOM
    rows.forEach(row => tbody.appendChild(row));
    
    // Actualizar números de fila
    rows.forEach((row, index) => {
        row.querySelector('.row-number').textContent = index + 1;
    });
}

// Función para mostrar notificaciones
function showNotification(message, type = 'info') {
    // Remover notificación existente
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Estilos para la notificación
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 6px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
        max-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    
    // Colores según el tipo
    switch (type) {
        case 'success':
            notification.style.backgroundColor = '#48bb78';
            break;
        case 'error':
            notification.style.backgroundColor = '#f56565';
            break;
        default:
            notification.style.backgroundColor = '#4299e1';
    }
    
    document.body.appendChild(notification);
    
    // Mostrar notificación
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Ocultar después de 3 segundos
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Función para actualizar información de paginación
function updatePaginationInfo(visibleRows) {
    const paginationInfo = document.querySelector('.pagination-info');
    if (paginationInfo) {
        const clasificacionNombre = document.querySelector('h1').textContent;
        const plural = visibleRows !== 1 ? 's' : '';
        paginationInfo.textContent = `Mostrando ${visibleRows} trámite${plural} de ${clasificacionNombre}`;
    }
}

// Funciones de paginación (placeholders para futura implementación)
function previousPage() {
    console.log('Página anterior');
}

function nextPage() {
    console.log('Página siguiente');
}

// Inicialización cuando se carga el DOM
document.addEventListener('DOMContentLoaded', function() {
    // Agregar event listeners adicionales si es necesario
    const searchInput = document.getElementById('search');
    if (searchInput) {
        // Limpiar búsqueda con Escape
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                this.value = '';
                filterTable();
            }
        });
    }
});