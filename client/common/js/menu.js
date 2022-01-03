const topNavBar = document.querySelector(".top-nav-bar")
const navToggle = document.querySelector(".mobile-nav-toggle")

navToggle.addEventListener("click", () => {
	if (topNavBar.dataset.visible === "false") {
		topNavBar.dataset.visible = "true"
		navToggle.setAttribute("aria-expanded", "true")
	} else if (topNavBar.dataset.visible === "true") {
		topNavBar.dataset.visible = "false"
		navToggle.setAttribute("aria-expanded", "false")
	}
})
