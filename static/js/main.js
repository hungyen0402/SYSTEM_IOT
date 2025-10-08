// Main JavaScript for IoT System

// Global variables
let socket;
let isConnected = false;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    initializeEventListeners();
    updateConnectionStatus();
});

// Initialize Socket.IO connection
function initializeSocket() {
    socket = io();
    
    socket.on('connect', function() {
        isConnected = true;
        updateConnectionStatus();
        console.log('Connected to server');
        showNotification('Đã kết nối đến server', 'success');
    });
    
    socket.on('disconnect', function() {
        isConnected = false;
        updateConnectionStatus();
        console.log('Disconnected from server');
        showNotification('Mất kết nối đến server', 'error');
    });
    
    socket.on('sensor_data_update', function(data) {
        updateSensorDisplay(data);
    });
    
    socket.on('device_status_update', function(data) {
        updateDeviceStatus(data);
        updateActionHistory(data);
    });
    
    socket.on('status', function(data) {
        console.log('Server status:', data.msg);
    });
}

// Initialize event listeners
function initializeEventListeners() {
    // Search functionality
    const searchInputs = document.querySelectorAll('input[type="text"]');
    searchInputs.forEach(input => {
        if (input.placeholder && input.placeholder.includes('Tìm kiếm')) {
            input.addEventListener('input', handleSearch);
        }
    });
    
    // Device control toggles
    const toggles = document.querySelectorAll('input[type="checkbox"]');
    toggles.forEach(toggle => {
        if (toggle.id.includes('toggle')) {
            toggle.addEventListener('change', function() {
                const deviceType = this.id.replace('-toggle', '');
                toggleDevice(deviceType, this.checked);
            });
        }
    });
    
    // Filter dropdowns
    const filterSelects = document.querySelectorAll('select');
    filterSelects.forEach(select => {
        select.addEventListener('change', handleFilter);
    });
    
    // Pagination
    const paginationLinks = document.querySelectorAll('.pagination a');
    paginationLinks.forEach(link => {
        link.addEventListener('click', handlePagination);
    });
}

// Handle search functionality
function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase();
    const table = event.target.closest('.card').querySelector('table');
    
    if (table) {
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    }
}

// Handle filter functionality
function handleFilter(event) {
    const filterValue = event.target.value;
    const table = event.target.closest('.card').querySelector('table');
    
    if (table && filterValue) {
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            if (filterValue === '') {
                row.style.display = '';
            } else {
                // Check if row contains the filter value
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filterValue.toLowerCase()) ? '' : 'none';
            }
        });
    }
}

// Handle pagination
function handlePagination(event) {
    event.preventDefault();
    const url = event.target.href;
    window.location.href = url;
}

// Toggle device control
function toggleDevice(deviceType, status) {
    const button = document.getElementById(`${deviceType}-toggle`);
    if (button) {
        button.disabled = true;
        button.classList.add('loading');
    }
    
    fetch(`/api/control/${deviceType}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(`${deviceType} ${status ? 'turned on' : 'turned off'}`);
            showNotification(`${getDeviceName(deviceType)} đã ${status ? 'bật' : 'tắt'}`, 'success');
        } else {
            console.error('Failed to control device');
            // Revert toggle state
            if (button) {
                button.checked = !status;
            }
            showNotification('Không thể điều khiển thiết bị', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Revert toggle state
        if (button) {
            button.checked = !status;
        }
        showNotification('Lỗi kết nối', 'error');
    })
    .finally(() => {
        if (button) {
            button.disabled = false;
            button.classList.remove('loading');
        }
    });
}

// Get device name in Vietnamese
function getDeviceName(deviceType) {
    const names = {
        'led': 'Tất cả LED',
        'led1': 'LED 1',
        'led2': 'LED 2', 
        'led3': 'LED 3',
        'internal_led': 'LED tích hợp'
    };
    return names[deviceType] || deviceType;
}

// Update sensor display
function updateSensorDisplay(data) {
    if (data.temperature !== undefined) {
        const tempElement = document.getElementById('temperature-value');
        if (tempElement) {
            tempElement.textContent = data.temperature + '°C';
            tempElement.classList.add('sensor-value');
        }
    }
    
    if (data.humidity !== undefined) {
        const humidityElement = document.getElementById('humidity-value');
        if (humidityElement) {
            humidityElement.textContent = data.humidity + '%';
            humidityElement.classList.add('sensor-value');
        }
    }
    
    if (data.light !== undefined) {
        const lightElement = document.getElementById('light-value');
        if (lightElement) {
            lightElement.textContent = data.light + ' Lux';
            lightElement.classList.add('sensor-value');
        }
    }
}

// Update device status
function updateDeviceStatus(data) {
    const toggle = document.getElementById(`${data.device}-toggle`);
    if (toggle) {
        toggle.checked = data.status;
    }
}

// Update action history
function updateActionHistory(data) {
    const tbody = document.getElementById('actions-table');
    if (tbody) {
        const newRow = document.createElement('tr');
        const now = new Date();
        const timeString = now.toLocaleTimeString('vi-VN') + ' ' + now.toLocaleDateString('vi-VN');
        const actionText = data.status ? 'Bật' : 'Tắt';
        const deviceName = getDeviceName(data.device);
        
        newRow.innerHTML = `
            <td>${tbody.children.length + 1}</td>
            <td>${deviceName}</td>
            <td><span class="badge bg-primary">${actionText}</span></td>
            <td>${timeString}</td>
        `;
        
        tbody.insertBefore(newRow, tbody.firstChild);
        
        // Remove last row if too many rows
        if (tbody.children.length > 10) {
            tbody.removeChild(tbody.lastChild);
        }
    }
}

// Update connection status
function updateConnectionStatus() {
    const statusElement = document.getElementById('connection-status');
    if (statusElement) {
        if (isConnected) {
            statusElement.className = 'status-connected';
            statusElement.textContent = 'Đã kết nối';
        } else {
            statusElement.className = 'status-disconnected';
            statusElement.textContent = 'Mất kết nối';
        }
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Add to container
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    container.appendChild(toast);
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Request sensor data
function requestSensorData() {
    if (socket && isConnected) {
        socket.emit('request_sensor_data');
    }
}

// Auto-refresh sensor data every 30 seconds
setInterval(requestSensorData, 30000);

// Utility functions
function formatDateTime(date) {
    return date.toLocaleString('vi-VN');
}

function formatTime(date) {
    return date.toLocaleTimeString('vi-VN');
}

function formatDate(date) {
    return date.toLocaleDateString('vi-VN');
}

// Export functions for global use
window.toggleDevice = toggleDevice;
window.requestSensorData = requestSensorData;
window.showNotification = showNotification;
