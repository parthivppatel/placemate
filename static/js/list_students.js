document.addEventListener('DOMContentLoaded', function() {
    let currentPage = 1;
    let recordsPerPage = 10;
    let studentToDelete = null;
    
    const tableBody = document.getElementById('studentsTableBody');
    const pagination = document.getElementById('pagination');
    const recordsPerPageSelect = document.getElementById('recordsPerPage');
    const startRecordSpan = document.getElementById('startRecord');
    const endRecordSpan = document.getElementById('endRecord');
    const totalRecordsSpan = document.getElementById('totalRecords');
    const deleteModal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const markAllReadBtn = document.getElementById('markAllReadBtn');
    
    // Initialize with data
    renderTable();
    renderPagination();
    updateRecordInfo();
    
    // Event listeners
    recordsPerPageSelect.addEventListener('change', function() {
        recordsPerPage = parseInt(this.value);
        currentPage = 1; // Reset to first page when changing records per page
        renderTable();
        renderPagination();
        updateRecordInfo();
    });
    
    // Handle confirm delete button
    confirmDeleteBtn.addEventListener('click', function() {
        if (studentToDelete !== null) {
            // Find the index of the student to delete
            const index = students.findIndex(student => student.id === studentToDelete);
            
            // Remove the student if found
            if (index !== -1) {
                students.splice(index, 1);
                
                // Recalculate current page if necessary
                const totalPages = Math.ceil(students.length / recordsPerPage);
                if (currentPage > totalPages && totalPages > 0) {
                    currentPage = totalPages;
                }
                
                // Re-render the table and pagination
                renderTable();
                renderPagination();
                updateRecordInfo();
            }
            
            // Reset studentToDelete
            studentToDelete = null;
            
            // Hide the modal
            deleteModal.hide();
        }
    });
    
    // Mark all notifications as read
    markAllReadBtn.addEventListener('click', function() {
        const unreadNotifications = document.querySelectorAll('.notification-item.unread');
        unreadNotifications.forEach(notification => {
            notification.classList.remove('unread');
        });
        
        // Update notification badge
        document.querySelector('.notification-badge').style.display = 'none';
    });
    
    // Functions
    function renderTable() {
        tableBody.innerHTML = '';
        
        const start = (currentPage - 1) * recordsPerPage;
        const end = start + recordsPerPage;
        const paginatedStudents = students.slice(start, end);
        
        paginatedStudents.forEach((student, index) => {
            const row = document.createElement('tr');
            const serialNumber = start + index + 1; // Calculate serial number
            
            // Determine status badge class
            let statusBadgeClass = '';
            if (student.status === 'Placed') {
                statusBadgeClass = 'status-placed';
            } else if (student.status === 'Processing') {
                statusBadgeClass = 'status-processing';
            } else if (student.status === 'Not Placed') {   
                statusBadgeClass = 'status-not-placed';
            }
            row.innerHTML = `
                <td>${serialNumber}</td>
                <td>${student.name}</td>
                <td>${student.regNo}</td>
                <td>${student.batch}</td>
                <td>${student.course}</td>
                <td><span class="status-badge ${statusBadgeClass}">${student.status}</span></td>
                <td>
                    <i class="bi bi-eye-fill eye-icon" title="View Details"></i>
                    
                    <i class="bi bi-trash-fill delete-icon" title="Delete" data-id="${student.id}" data-bs-toggle="modal" data-bs-target="#deleteConfirmModal"></i>
                </td>
            `;
            tableBody.appendChild(row);
        });
        // Add event listeners to delete icons
        const deleteIcons = document.querySelectorAll('.delete-icon');
        deleteIcons.forEach(icon => {
            icon.addEventListener('click', function() {
                studentToDelete = parseInt(this.getAttribute('data-id'));
            });
        });
    }
    function renderPagination() {
        pagination.innerHTML = '';
        
        const totalPages = Math.ceil(students.length / recordsPerPage);
        
        for (let i = 1; i <= totalPages; i++) {
            const pageItem = document.createElement('li');
            pageItem.className = 'page-item' + (i === currentPage ? ' active' : '');
            pageItem.innerHTML = `<a class="page-link" href="#">${i}</a>`;
            
            pageItem.addEventListener('click', function(event) {
                event.preventDefault();
                currentPage = i;
                renderTable();
                renderPagination();
                updateRecordInfo();
            });
            
            pagination.appendChild(pageItem);
        }
    }
    function updateRecordInfo() {
        const totalRecords = students.length;
        const start = (currentPage - 1) * recordsPerPage + 1;
        const end = Math.min(currentPage * recordsPerPage, totalRecords);
        
        startRecordSpan.innerText = start;
        endRecordSpan.innerText = end;
        totalRecordsSpan.innerText = totalRecords;
    }
});