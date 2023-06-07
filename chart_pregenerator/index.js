const express = require('express')
const { renderToString } = require('react-dom/server')
const Test = require('./Test')
const React = require('react')

const app = express()

app.get('/', (req, res) => {
	const renderedComponent = renderToString(Test)
	res.send(renderedComponent)
})

app.listen(3000)
