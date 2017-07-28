import React, { PureComponent } from 'react'
import axios from 'axios'


class EmailSignup extends PureComponent {
	constructor(props, ...args) {
		super(props, ...args)

		this.handleSubmit = this.handleSubmit.bind(this)

		this.state = {
			emailAddress: '',
			errorMessage: '',
			state: EmailSignup.INPUT,
		}
	}

	handleChange(field, event) {
		this.setState({ [field]: event.target.value })
	}

	handleSubmit(event) {
		event.preventDefault()

		const {
			INPUT,
			LOADING,
			ALREADY_SIGNED_UP,
			SUCCESS,
		} = EmailSignup

		this.setState({ state: LOADING })

		const handleResolve = (response) => {
			if (response.status === 200) {
				var state = SUCCESS
			} else {
				var state = INPUT
			}

			this.setState({ state })
		}

		const handleReject = (error) => {
			if (error.response.data === 'already_signed_up') {
				var state = ALREADY_SIGNED_UP
			} else {
				var state = INPUT
			}
			this.setState({
				state,
				errorMessage: error.response.data,
			})
		}

		axios.post(
			'/emails/create/',
			`email_address=${this.state.emailAddress}`
		).then(handleResolve, handleReject)
	}

	render() {
		const {
			INPUT,
			LOADING,
			ALREADY_SIGNED_UP,
			SUCCESS,
		} = EmailSignup

		const {
			state,
			emailAddress,
			errorMessage,
		} = this.state

		if (state === ALREADY_SIGNED_UP) {
			return (
				<div className="email-signup email-signup--already-signed-up">
					<p>This email address is already signed up.</p>
				</div>
			)
		}

		if (state === SUCCESS) {
			return (
				<div className="email-signup email-signup--success">
					<p>Success!</p>
				</div>
			)
		}

		const hasError = errorMessage !== ''

		return (
			<form onSubmit={this.handleSubmit}>
				<span>
					<input
						type="text"
						value={emailAddress}
						onChange={this.handleChange.bind(this, 'emailAddress')}
						disabled={state !== INPUT}
					/>

					{hasError && (
						<span>{errorMessage}</span>
					)}
				</span>

				<button
					type="submit"
					disabled={state !== INPUT}
				>
					Signup
				</button>
			</form>
		)
	}
}


EmailSignup.INPUT = 'input'


EmailSignup.LOADING = 'loading'


EmailSignup.ALREADY_SIGNED_UP = 'already_signed_up'


EmailSignup.SUCCESS = 'success'


export default EmailSignup
