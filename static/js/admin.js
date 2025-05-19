// Admin section specific JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin JS loaded');
    
    // Initialize any tooltips on the admin pages
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (tooltipTriggerList.length > 0 && typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Add confirmation to any delete actions
    const deleteButtons = document.querySelectorAll('.btn-delete, .btn-danger[data-confirm]');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            const message = this.getAttribute('data-confirm') || 'Are you sure you want to delete this item?';
            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });
    
    // Highlight matching rows on hover
    const matchingTable = document.querySelectorAll('.table-hover tbody tr');
    matchingTable.forEach(row => {
        row.addEventListener('mouseenter', function() {
            const requestId = this.querySelector('td:first-child')?.textContent;
            const donationId = this.querySelector('td:nth-child(5)')?.textContent;
            
            if (requestId && donationId) {
                // Add highlight class
                this.classList.add('table-active');
                
                // Update any visualization elements
                const visualElement = document.getElementById(`match-${requestId}-${donationId}`);
                if (visualElement) {
                    visualElement.classList.add('highlighted');
                }
            }
        });
        
        row.addEventListener('mouseleave', function() {
            const requestId = this.querySelector('td:first-child')?.textContent;
            const donationId = this.querySelector('td:nth-child(5)')?.textContent;
            
            if (requestId && donationId) {
                // Remove highlight class
                this.classList.remove('table-active');
                
                // Update any visualization elements
                const visualElement = document.getElementById(`match-${requestId}-${donationId}`);
                if (visualElement) {
                    visualElement.classList.remove('highlighted');
                }
            }
        });
    });
});
