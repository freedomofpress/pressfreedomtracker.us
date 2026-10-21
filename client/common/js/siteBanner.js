const banner = document.querySelector(".site-banner");
const dismissButton = banner?.querySelector(".site-banner__dismiss");

if (dismissButton) {
	dismissButton.hidden = false;
	dismissButton.addEventListener("click", () => {
		banner.hidden = true;
		try {
			localStorage.setItem("dismissedBanner", banner.dataset.bannerKey);
		} catch {
			// Storage can be unavailable (e.g. blocked cookies); the banner just returns on the next page.
		}
	});
}
