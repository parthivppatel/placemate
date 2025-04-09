// Sample data for demonstration
const students = [
    { id: 1, name: "Parthiv Patel", regNo: "202412069", batch: "2024-2026", course: "M.Sc. IT", status: "Placed" },
    { id: 2, name: "Rahul Sharma", regNo: "21CS102", batch: "2021-2025", course: "B.Tech CSE", status: "Placed" },
    { id: 3, name: "Priya Singh", regNo: "21CS103", batch: "2021-2025", course: "B.Tech CSE", status: "Processing" },
    { id: 4, name: "Arjun Nair", regNo: "21EC101", batch: "2021-2025", course: "B.Tech ECE", status: "Placed" },
    { id: 5, name: "Sneha Gupta", regNo: "21EC102", batch: "2021-2025", course: "B.Tech ECE", status: "Not Placed" },
    { id: 6, name: "Vikram Reddy", regNo: "21ME101", batch: "2021-2025", course: "B.Tech Mech", status: "Processing" },
    { id: 7, name: "Neha Kapoor", regNo: "21EE101", batch: "2021-2025", course: "B.Tech EEE", status: "Placed" },
    { id: 8, name: "Rajesh Kumar", regNo: "22CS101", batch: "2022-2026", course: "B.Tech CSE", status: "Not Placed" },
    { id: 9, name: "Meera Iyer", regNo: "22CS102", batch: "2022-2026", course: "B.Tech CSE", status: "Processing" },
    { id: 10, name: "Sameer Joshi", regNo: "22EC101", batch: "2022-2026", course: "B.Tech ECE", status: "Not Placed" },
    { id: 11, name: "Anjali Menon", regNo: "22MCA101", batch: "2022-2024", course: "MCA", status: "Processing" },
    { id: 12, name: "Rohan Das", regNo: "22MCA102", batch: "2022-2024", course: "MCA", status: "Placed" },
    { id: 13, name: "Kiran Shah", regNo: "21MBA101", batch: "2021-2023", course: "MBA", status: "Placed" },
    { id: 14, name: "Divya Krishnan", regNo: "21MBA102", batch: "2021-2023", course: "MBA", status: "Placed" },
    { id: 15, name: "Aditi Verma", regNo: "20CS101", batch: "2020-2024", course: "B.Tech CSE", status: "Placed" },
    { id: 16, name: "Varun Malhotra", regNo: "20CS102", batch: "2020-2024", course: "B.Tech CSE", status: "Placed" },
    { id: 17, name: "Pallavi Desai", regNo: "20EC101", batch: "2020-2024", course: "B.Tech ECE", status: "Not Placed" },
    { id: 18, name: "Akash Patel", regNo: "20ME101", batch: "2020-2024", course: "B.Tech Mech", status: "Processing" },
    { id: 19, name: "Kavya Rajan", regNo: "22MBA101", batch: "2022-2024", course: "MBA", status: "Not Placed" },
    { id: 20, name: "Siddharth Iyer", regNo: "22MBA102", batch: "2022-2024", course: "MBA", status: "Processing" }
];

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