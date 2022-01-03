const topNavBar = document.querySelector(".top-nav-bar")
const navToggle = document.querySelector(".mobile-nav-toggle")
const header = document.querySelector(".header")

navToggle.addEventListener("click", () => {
	if (topNavBar.dataset.visible === "false") {
		document.body.classList.add("overflow-hidden")
		header.classList.add("menu-expanded")
		topNavBar.dataset.visible = "true"
		navToggle.setAttribute("aria-expanded", "true")
	} else if (topNavBar.dataset.visible === "true") {
		header.classList.remove("menu-expanded")
		document.body.classList.remove("overflow-hidden")
		topNavBar.dataset.visible = "false"
		navToggle.setAttribute("aria-expanded", "false")
	}
})
