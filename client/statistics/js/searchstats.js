import '../sass/statistics.sass'
import ReactModal from "react-modal";

const React = window.React
const Modifier = window.DraftJS.Modifier
const EditorState = window.DraftJS.EditorState
const TooltipEntity = window.draftail.TooltipEntity
const Icon = window.wagtail.components.Icon

ReactModal.setAppElement("#wagtail")

class SearchStatSource extends React.Component {
	constructor(props) {
        super(props)

        this.inputRef = React.createRef()

		const { entityKey, editorState } = props
		let state
		if (entityKey) {
			const contentState = editorState.getCurrentContent()
			const { search, dataset } = contentState.getEntity(entityKey).getData()
			state = {
				url: search,
				dataset: dataset || "TOTAL",
			}
		} else {
			state = {
				url: "",
				dataset: "TOTAL",
			}
		}

		this.onAfterOpen = this.onAfterOpen.bind(this)
		this.onChangeUrl = this.onChangeUrl.bind(this)
		this.onChangeDataset = this.onChangeDataset.bind(this)
		this.onConfirm = this.onConfirm.bind(this)
		this.onRequestClose = this.onRequestClose.bind(this)
		this.state = state
	}

	onAfterOpen() {
		const input = this.inputRef.current

		if (input) {
			input.focus()
			input.select()
		}
	}

	onChangeDataset(e) {
		if (e.target instanceof HTMLInputElement) {
			const dataset = e.target.value
			this.setState({ dataset })
		}
	}

	onChangeUrl(e) {
		if (e.target instanceof HTMLInputElement) {
			const url = e.target.value
			this.setState({ url })
		}
	}

	onRequestClose(e) {
		const { onClose } = this.props
		e.preventDefault()

		onClose()
	}

	onConfirm(e) {
		e.preventDefault()

		const { editorState, entityType, onComplete } = this.props
		const content = editorState.getCurrentContent()
		const selection = editorState.getSelection()
		let nextState
		const { url, dataset } = this.state

		const summaryUrl = new URL(url)
		summaryUrl.pathname = '/all-incidents/summary/'

		fetch(summaryUrl.href)
			.then(response => response.json())
			.then(data => {
				let params = {}
				let count
				if (dataset == 'TOTAL') {
					count = data.total
				} else if (dataset == 'INSTITUTIONS') {
					count = data.institutions
				} else if (dataset == 'JOURNALISTS') {
					count = data.journalists
				} else {
					count = 0
				}

				for (let [key, value] of summaryUrl.searchParams.entries()) {
					params[`param_${key}`] = value
				}

				const contentWithEntity = content.createEntity(entityType.type, 'IMMUTABLE', {
					count: count,
					search: url,
					dataset: dataset,
					...params,
				})

				const entityKey = contentWithEntity.getLastCreatedEntityKey()
				const text = `${count}`

				const newContent = Modifier.replaceText(content, selection, text, null, entityKey);
				nextState = EditorState.push(editorState, newContent, 'insert-characters')
			})
			.catch((error) => {
				window.alert("Error while constructing statistics. Please check that the URL is correct.")
				console.error(error)
			})
			.finally(() => { onComplete(nextState) })

	}

	render() {
		const { url } = this.state;
		const datasets = ['Total', 'Journalists', 'Institutions'];
		return (
			<ReactModal
				isOpen
				onAfterOpen={this.onAfterOpen}
				onRequestClose={this.onRequestClose}
				contentLabel="Stats Link Chooser"
				className="admin-modal"
				overlayClassName="admin-overlay"
			>
				<form onSubmit={this.onConfirm}>
					<fieldset>
						<legend className="admin-modal__legend">Select dataset for statistic:</legend>
						{datasets.map((dataset, index) =>
							<p class="admin-modal__dataset_field">
								<label className="admin-modal__label" key={index}>
									<input
										className="admin-modal__dataset_radio"
										value={dataset.toUpperCase()}
										checked={this.state.dataset === dataset.toUpperCase()}
										onChange={this.onChangeDataset}
										type="radio" />
									{dataset}
								</label>
							</p>
						)}
					</fieldset>

					<p>
						<label className="admin-modal__label" for="url">Enter a URL:</label>
						<input
							ref={this.inputRef}
							type="url"
							onChange={this.onChangeUrl}
							value={url}
							placeholder="https://pressfreedomtracker.us/equipment_damage/?categories=4&equipment_broken=2"
							pattern="https?://.*"
							size="100"
							required
						/>
					</p>
					<p>
						Perform a search on the <a href="https://pressfreedomtracker.us/">main site</a> for incidents to include in this statistic and copy the URL here.
					</p>
					<button className="button button-secondary no" onClick={this.onRequestClose}>Cancel</button>
					<button className="button" type="submit">Save</button>
				</form>
			</ReactModal>
		)
	}
}

const getStatAttributes = (data) => {
	const searchUrl = data.search || null
	const dataset = data.dataset
	const icon = <Icon name="cog" />

	const url = searchUrl
	let label
	if (dataset == 'TOTAL') {
		label = "Incident count"
	} else if (dataset == 'INSTITUTIONS') {
		label = "Institutions affected"
	} else if (dataset == 'JOURNALISTS') {
		label = "Journalists affected"
	} else {
		label = ""
	}

	for (let [key, value] of Object.entries(data)) {
		if (key.startsWith('param_')) {
			label += ` ${key.replace('param_', '')}="${value}"`
		}
	}

	return {
		url,
		icon,
		label,
	}
}

const SearchStat = (props) => {
	const { entityKey, contentState } = props

	const data = contentState.getEntity(entityKey).getData()

	return (
		<TooltipEntity {...props} {...getStatAttributes(data)} />
	)
}

window.draftail.registerPlugin(
	{
		type: 'SEARCHSTAT',
		source: SearchStatSource,
		decorator: SearchStat,
	}
)
