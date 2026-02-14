document.addEventListener("DOMContentLoaded", () => {
    const logoutBtn = document.getElementById("logoutConfirmBtn");
    const logoutOverlay = document.getElementById("logoutOverlay");
    const logoutNo = document.getElementById("logoutNo");

    if (logoutBtn) {
        logoutBtn.addEventListener("click", (e) => {
            e.preventDefault();
            logoutOverlay.classList.remove("hidden");
        });
    }

    if (logoutNo) {
        logoutNo.addEventListener("click", () => {
            logoutOverlay.classList.add("hidden");
        });
    }
});
