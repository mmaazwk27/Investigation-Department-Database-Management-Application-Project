// =============================
// Navbar Active Link Highlight
// =============================
document.addEventListener("DOMContentLoaded", function () {
    let currentPath = window.location.pathname;
    let navLinks = document.querySelectorAll(".navbar-nav .nav-link");

    navLinks.forEach(link => {
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active");
        }
    });
});




// =============================
// Confirm Before Deleting Records
// =============================
function confirmDelete() {
    return confirm("Are you sure you want to delete this record?");
}

function confirmDeleteAndKey(form) {
    const key = form.querySelector('[name="security_key"]').value;
    if (!key) {
        alert("Please enter the security key.");
        return false;
    }
    return confirm("Are you sure you want to delete this account?");
}

// =============================
// Search Functionality (Client-Side)
// =============================
document.addEventListener("DOMContentLoaded", function () {
    let searchInput = document.querySelector("#searchInput");
    let searchResults = document.querySelectorAll(".searchable");

    if (searchInput) {
        searchInput.addEventListener("keyup", function () {
            let query = searchInput.value.toLowerCase();
            searchResults.forEach(item => {
                let text = item.textContent.toLowerCase();
                item.style.display = text.includes(query) ? "" : "none";
            });
        });
    }
});

// =============================
// Toast Notification System
// =============================
function showToast(message, type = "success") {
    let toastContainer = document.getElementById("toast-container");

    if (!toastContainer) {
        toastContainer = document.createElement("div");
        toastContainer.id = "toast-container";
        toastContainer.style.position = "fixed";
        toastContainer.style.top = "20px";
        toastContainer.style.right = "20px";
        toastContainer.style.zIndex = "9999";
        document.body.appendChild(toastContainer);
    }

    let toast = document.createElement("div");
    toast.className = `toast alert alert-${type}`;
    toast.textContent = message;
    toast.style.padding = "10px 20px";
    toast.style.marginTop = "10px";
    toast.style.borderRadius = "5px";
    toast.style.boxShadow = "0px 2px 10px rgba(0, 0, 0, 0.1)";
    
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// =============================
// Auto-Close Alerts after 3s
// =============================
document.addEventListener("DOMContentLoaded", function () {
    let alerts = document.querySelectorAll(".alert-auto-dismiss");
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.display = "none";
        }, 3000);
    });
});


// ============================================
// Unsaved Changes alert while editing accounts
// ============================================

function showUnsavedWarning(selectElement) {
    const form = selectElement.closest('form');
    const warning = form.querySelector('.unsaved-warning');
    if (warning) {
        warning.style.display = 'block';
    }
}

function clearWarning(formElement) {
    const warning = formElement.querySelector('.unsaved-warning');
    if (warning) {
        warning.style.display = 'none';
    }
}