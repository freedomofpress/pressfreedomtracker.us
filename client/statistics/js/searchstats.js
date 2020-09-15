const React = window.React
const Modifier = window.DraftJS.Modifier
const EditorState = window.DraftJS.EditorState
const TooltipEntity = window.draftail.TooltipEntity
const Icon = window.wagtail.components.Icon

class SearchStatSource extends React.Component {
	componentDidMount() {
		const { editorState, entityType, onComplete } = this.props

		const content = editorState.getCurrentContent()
		const selection = editorState.getSelection()

		const search = window.prompt("Enter a url.")
		const count = Math.floor(Math.random() * 150)

		let nextState
		if (search) {
			const url = new URL(search);

			let params = {}

			for (let [key, value] of url.searchParams.entries()) {
				params[`param_${key}`] = value
			}

			const contentWithEntity = content.createEntity(entityType.type, 'IMMUTABLE', {
				count: count,
				search: search,
				...params,
			})

			const entityKey = contentWithEntity.getLastCreatedEntityKey()
			const text = `${count}`

			const newContent = Modifier.replaceText(content, selection, text, null, entityKey);
			nextState = EditorState.push(editorState, newContent, 'insert-characters')
		}
		onComplete(nextState)
	}

	render() {
		return null
	}
}

const getStatAttributes = (data) => {
	const count = data.count || null
	const searchUrl = data.search || null
	const icon = <Icon name="cog" />

	const url = searchUrl
	let label = "Incident Count:"

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
			<TooltipEntity {...props} {...getStatAttributes(data)}>
			{contentState.getEntity(entityKey).getData().count}
			</TooltipEntity>
	)
}

window.draftail.registerPlugin(
	{
		type: 'SEARCHSTAT',
		source: SearchStatSource,
		decorator: SearchStat,
	}
)
