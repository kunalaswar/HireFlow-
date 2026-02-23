document.addEventListener("DOMContentLoaded", function () {

    const logoutBtn = document.getElementById("logoutConfirmBtn");
    const popup = document.getElementById("logoutPopup");
    const yesBtn = document.getElementById("logoutYes");
    const noBtn = document.getElementById("logoutNo");

    if (logoutBtn) {
        logoutBtn.addEventListener("click", function (e) {
            e.preventDefault();
            popup.style.display = "flex";
        });
    }

    if (noBtn) {
        noBtn.addEventListener("click", function () {
            popup.style.display = "none";
        });
    }

    if (yesBtn) {
        yesBtn.addEventListener("click", function () {
            window.location.href = "/logout/";
        });
    }

});