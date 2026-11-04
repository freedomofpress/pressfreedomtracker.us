class SiteBanner extends HTMLElement {
	connectedCallback() {
		const dismissButton = this.querySelector(".site-banner__dismiss");
		dismissButton.addEventListener("click", () => {
			this.hidden = true;
			try {
				localStorage.setItem("siteBannerDismissedAt", Date.now());
			} catch {
				// if localStorage is unavailable the banner returns on the next page.
			}
		});
	}
}

customElements.define("site-banner", SiteBanner);
