// HireFlow Admin Dashboard Enhancements

document.querySelectorAll(".dashboard-card").forEach(card => {
    card.addEventListener("mouseenter", () => {
        card.style.transform = "translateY(-2px)";
        card.style.boxShadow = "0 12px 30px rgba(0,0,0,0.08)";
    });

    card.addEventListener("mouseleave", () => {
        card.style.transform = "translateY(0)";
        card.style.boxShadow = "0 6px 18px rgba(0,0,0,0.06)";
    });
});

console.info("HireFlow Admin Dashboard loaded");


