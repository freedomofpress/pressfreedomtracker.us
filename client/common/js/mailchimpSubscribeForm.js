function submit(event) {
	event.preventDefault()

	const form = event.currentTarget;
	const formData = new FormData(form);
	const plainFormData = Object.fromEntries(formData.entries());
	delete plainFormData.csrfmiddlewaretoken
	const formDataJsonString = JSON.stringify(plainFormData);

	const url = form.action;
	const csrfUrl = form.dataset.csrfEndpoint;

	if (form.classList.contains("submitting")) {
		return
	}
	form.classList.add("submitting")

	fetch(csrfUrl).then((response) => {
		return response.text()
	}).then(csrfToken => {
		return fetch(url, {
			method: 'post',
			headers: {
				'Accept': 'application/json',
				'Content-Type': 'application/json',
				'X-Requested-With': 'XMLHttpRequest', //Necessary to work with request.is_ajax()
				'X-CSRFToken': csrfToken,
			},
			body: formDataJsonString,
		})
	}).then(response => {
		if (response.status >= 200 && response.status <= 299) {
			return response.json()
		} else {
			throw Error(response.statusText);
		}
	}).then(jsonResponse => {
		if (jsonResponse.success) {
			form.classList.remove("submitting")
			let thanks = document.getElementById('mc-subscribe-thanks')
			let formSignup = document.getElementById('mc-mailing-list-signup')
			thanks.style.display = ''
			formSignup.style.display = 'none'
		} else {
			throw Error(jsonResponse.message)
		}
	}).catch(error => {
		form.classList.remove("submitting")
		let statusBar = form.querySelector('[role="status"]')
		statusBar.style.display = ''
		statusBar.textContent = 'An internal error occurred.'
		console.error(error)
	})
}

document.addEventListener('DOMContentLoaded', () => {
	const form = document.getElementById('mc-embedded-subscribe-form')
	if (!form) {
		return
	}
	form.onsubmit = submit
})
