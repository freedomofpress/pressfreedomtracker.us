import React from 'react'
import ReactDom from 'react-dom'

import EmailSignup from '~/emails/EmailSignup'

// Instantiate email signups:
document.addEventListener('DOMContentLoaded', () => {
	const emailSignups = Array.from(document.getElementsByClassName('js-emails-signup'))
	emailSignups.forEach(el => {
		ReactDOM.render((
			<EmailSignup
				signupPrompt={el.dataset.signupPrompt}
				successText={el.dataset.successText}
			/>
		), el)
	})
})
