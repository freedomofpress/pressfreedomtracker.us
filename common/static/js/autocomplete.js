import React, { PureComponent } from 'react'
import { render } from 'react-dom'
import axios from 'axios'


class Autocomplete extends PureComponent {
	constructor(props, ...args) {
		super(props, ...args)
		this.state = {
			value: props.value,
		}
	}

	render() {
		const { name } = this.props
		const { value } = this.state

		return (
			<span>
				<input
					type="hidden"
					value={value}
					name={name}
				/>
				{value.map(page =>
					<div key={page.id}>{page.title}</div>
				)}
			</span>
		)
	}
}


window.renderAutocompleteWidget = (id, name, value) => {
	render(
		<Autocomplete
			name={name}
			value={value}
		/>,
		document.getElementById(id)
	)
}
