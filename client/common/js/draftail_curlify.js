import * as curlify from './curlify'

(function (draftail, DraftJS) {
	const HANDLED = 'handled'
	const NOT_HANDLED = 'not-handled'

	const EditorState = DraftJS.EditorState
	const Modifier = DraftJS.Modifier
	const ContentState = DraftJS.ContentState
	const BlockMapBuilder = DraftJS.BlockMapBuilder
	const convertFromHTML = DraftJS.convertFromHTML

	const DQUOTE_START = '“'
	const DQUOTE_END = '”'
	const SQUOTE_START = '‘'
	const SQUOTE_END = '’'

	const curlifyPlugin = {
		type: 'curlify',

		handlePastedText(text, html, editorState, { setEditorState }) {
			try {
				if (html) {
					let newHTML = curlify.html(html)
					const { contentBlocks, entityMap } = convertFromHTML(newHTML)
					let htmlMap = BlockMapBuilder.createFromArray(contentBlocks)
					let newContent = Modifier.replaceWithFragment(
						editorState.getCurrentContent(),
						editorState.getSelection(),
						htmlMap,
					)
					setEditorState(
						EditorState.push(
							editorState,
							newContent.set('entityMap', entityMap),
							'insert-fragment',
						)
					)

					return HANDLED
				} else if (text) {
					const straightQuotes = /['"]/
					if (!(straightQuotes.test(text))) {
						// If the pasted text does not include straight single
						// or double quotes, then we have nothing to do, so
						// defer to Draft.js.
						return NOT_HANDLED
					}

					const newText = curlify.plainText(text)

					// Convert new text string into format needed by Draft.JS
					const blocks = ContentState.createFromText(newText).getBlocksAsArray()
					const transformedContentState = ContentState.createFromBlockArray(blocks)
					const pushContentState = Modifier.replaceWithFragment(
						editorState.getCurrentContent(),
						editorState.getSelection(),
						transformedContentState.getBlockMap()
					)

					const newEditorState = EditorState.push(
						editorState,
						pushContentState,
						'insert-fragment',
					)

					// Update the editor
					setEditorState(newEditorState)
					return HANDLED
				}
			} catch (error) {
				console.error(error)
				return NOT_HANDLED
			}
			return NOT_HANDLED
		},

		handleBeforeInput(str, editorState, { setEditorState }) {
			if (str === '"' || str == '\'') {
				const selection = editorState.getSelection()
				const content = editorState.getCurrentContent()
				const currentBlock = content.getBlockForKey(selection.getStartKey())
				const textContent = currentBlock.getText()
				const textLength = textContent.length

				console.log("curlifying")

				function replaceCharacter(newCharacter) {
					setEditorState(
						EditorState.push(
							editorState,
							Modifier.insertText(content, selection, newCharacter),
							'transpose-characters',
						)
					)
				}
				if (!selection.isCollapsed()) {
					setEditorState(EditorState.push(
						editorState,
						Modifier.replaceText(
							editorState.getCurrentContent(),
							selection,
							str === '"' ? DQUOTE_START : SQUOTE_START
						),
						'insert-characters',
					))
					return HANDLED
				} else if (selection.getAnchorOffset() === 0) {
					replaceCharacter(str === '"' ? DQUOTE_START : SQUOTE_START)
					return HANDLED
				} else if (textLength > 0) {
					const lastCharacter = textContent[textLength - 1]
					if (lastCharacter !== ' ') {
						replaceCharacter(str === '"' ? DQUOTE_END : SQUOTE_END)
					} else {
						replaceCharacter(str === '"' ? DQUOTE_START : SQUOTE_START)
					}
					return HANDLED
				}

			}
			return NOT_HANDLED
		},
	};
	draftail.registerPlugin(curlifyPlugin, 'plugins')
})(window.draftail, window.DraftJS)
