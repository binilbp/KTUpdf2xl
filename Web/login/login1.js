const container = document.getElementById("container");
const overlayBtn = document.getElementById("overlayBtn");

overlayBtn.addEventListener("click", () => {
    container.classList.toggle("right_panel_active")
});