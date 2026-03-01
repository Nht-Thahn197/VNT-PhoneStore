(() => {
    const bankSection = document.querySelector(".bank-qr");
    if (!bankSection) {
        return;
    }

    const img = bankSection.querySelector("img");
    const qrUrl = bankSection.dataset.qrUrl;
    const fallbackUrl = bankSection.dataset.fallbackUrl;

    const updateVisibility = () => {
        const selected = document.querySelector("input[name=\"payment_method\"]:checked");
        const isBank = selected && selected.value === "bank";
        bankSection.classList.toggle("is-active", Boolean(isBank));
        if (isBank && img) {
            img.src = qrUrl || fallbackUrl || img.src;
        }
    };

    document.querySelectorAll("input[name=\"payment_method\"]")
        .forEach((input) => input.addEventListener("change", updateVisibility));

    updateVisibility();
})();
