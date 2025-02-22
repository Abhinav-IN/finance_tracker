const menu_panel = document.getElementById("menu_panel");
const menu_toggle = document.querySelectorAll(".menu_toggle");

menu_toggle.forEach((element) => {
  element.addEventListener("click", menuToggle);
});

function menuToggle() {
  menu_panel.classList.toggle("-translate-x-full");
}
