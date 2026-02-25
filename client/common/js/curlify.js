import { string } from 'smartquotes'

// Regular expressions borrowed from the smartquotes repo.  These are
// being used so that we can write additional replacers using similar
// baseline constants to what's already being used in `smartquotes`.
const pL = 'a-zA-ZáàâäãåçéèêëíìîïñóòôöõúùûüýÿæœÁÀÂÄÃÅÇÉÈÊËÍÌÎÏÑÓÒÔÖÕÚÙÛÜÝŸÆŒ'
const word = `[${pL}_0-9]`
const nonWord = `[^${pL}_0-9]`

// Borrowed from the `smartquotes` repo.  This is required for
// `handleElement` to work correctly.
const TEXT_NODE = typeof Element !== 'undefined' && Element.TEXT_NODE || 3

// Additional replacements that are applied to strings prior to
// processing them using the `smartquotes` library.
const replacers = [
	{
		// Handle the case where a beginning double quote is followed
		// by a non-word character such as ' or [.
		matcher: new RegExp(`(${nonWord}|^)"(${word}|'|\\\[)`, 'g'),
		replacement: '$1\u201c$2',
	}
]

// given a string of HTML, returns a single DOM node with its
// child(ren) the contents of that string.
function htmlToNode(html) {
	const template = document.createElement('template')
	template.innerHTML = html
	return template.content
}

// code copied from the `smartquotes` repo.  This function replaces
// quotes in an HTML element extracting text content and processing
// that text.  We have copied this whole function so we can use our
// own `plainText` function, which applies our additional `replacers`
// (defined above) prior to using `string` from the `smartquotes`
// library.
function handleElement(el) {
	if (['CODE', 'PRE', 'SCRIPT', 'STYLE'].indexOf(el.nodeName.toUpperCase()) !== -1) {
		return
	}

	let i, node, nodeInfo
	let text = ''
	const childNodes = el.childNodes
	const textNodes = []

	// compile all text first so we handle working around child nodes
	for (i = 0; i < childNodes.length; i++) {
		node = childNodes[i]

		if (node.nodeType === TEXT_NODE || node.nodeName === '#text') {
			textNodes.push([node, text.length])
			text += node.nodeValue || node.value
		} else if (node.childNodes && node.childNodes.length) {
			text += handleElement(node)
		}
	}
	text = plainText(text, { retainLength: true })
	for (i in textNodes) {
		nodeInfo = textNodes[i]
		if (nodeInfo[0].nodeValue) {
			nodeInfo[0].nodeValue = removeInvisibleSeparators(text, nodeInfo[0].nodeValue, nodeInfo[1])
		} else if (nodeInfo[0].value) {
			nodeInfo[0].value = removeInvisibleSeparators(text, nodeInfo[0].value, nodeInfo[1])
		}
	}
	return text
}

// Helper function copied from `smartquotes` repo, but with more
// descriptive name and using a non-deprecated string method.
function removeInvisibleSeparators(text, value, position) {
	return text.slice(position, position + value.length).replace('\u2063', '')
}

// replaces ASCII quotes with curly quotes in plainText using our set
// of `replacers` (defined above) prior to using the `smartquotes`
// library.  `options` is required for compatibility with the `string`
// function of `smartquotes` and anything given is passed directly to
// that function.
export function plainText(text, options = {}) {
	let result = text
	replacers.forEach(({matcher, replacement}) => {
		result = result.replace(matcher, replacement)
	})
	return string(result, options)
}

// replaces ASCII quotes with curly quotes in an HTML string.  We must
// convert it to a node because our `smartquotes` code handles quote
// replacement within nodes, but Draft.JS receives pasted HTML as a
// string.  So we receive a string, convert it to a node, process it,
// then re-convert it to a string so Draft.JS can use it.
export function html(htmlString) {
	let newHTML = ''
	let node = htmlToNode(htmlString)
	handleElement(node)
	node.childNodes.forEach(node => {
		newHTML += (node.outerHTML || node.nodeValue)
	})
	return newHTML
}
