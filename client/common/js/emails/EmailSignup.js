import React, { PureComponent } from 'react'
import axios from 'axios'
import classNames from 'classnames'
import { HorizontalLoader } from '~/filtering/Loader'


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
			`email_address=${encodeURIComponent(this.state.emailAddress)}`
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

		const {
			signupPrompt,
			successText,
		} = this.props

		if (state === ALREADY_SIGNED_UP) {
			return (
				<div className="emails-signup__message emails-signup__message--already-signed-up">
					<p className="emails-signup__text">This email address is already signed up.</p>
				</div>
			)
		}

		if (state === SUCCESS) {
			return (
				<div className="emails-signup__message emails-signup__message--success">
					<p className="emails-signup__text">{successText}</p>
				</div>
			)
		}

		const hasError = errorMessage !== ''

		return (
			<form
				onSubmit={this.handleSubmit}
				className="emails-signup__form"
			>
				<h2 className="emails-signup__title">{signupPrompt}</h2>

				<span className="emails-signup__input-container">
					<input
						type="text"
						value={emailAddress}
						onChange={this.handleChange.bind(this, 'emailAddress')}
						disabled={state !== INPUT}
						className={classNames(
							'emails-signup__input',
							{ 'emails-signup__input--error': hasError }
						)}
						placeholder="alice@freedom.press"
					/>

					<span className="emails-signup__error">{errorMessage}</span>
				</span>

				<button
					type="submit"
					className={classNames(
						'emails-signup__button',
						{ 'emails-signup__button--loading': state === LOADING }
					)}
					disabled={state !== INPUT}
				>
					{/* extra span below necessary for some weird Safari flexbox behavior */}
					{state === LOADING ? <HorizontalLoader className="horizontal-loader--centered" /> : <span>Sign Up</span>}
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
