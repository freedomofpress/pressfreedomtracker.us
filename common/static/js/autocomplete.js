import React, { PureComponent } from 'react'
import { render } from 'react-dom'
import axios from axios


class Autocomplete extends Component {
	componentDidMount() {
	}

	render() {
		return <div>hi</div>
	}
}


window.renderAutocompleteWidget = (id) => {
	render(
		<Autocomplete />,
		document.getElementById(id)
	)
}
