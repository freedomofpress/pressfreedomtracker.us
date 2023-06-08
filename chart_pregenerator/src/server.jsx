import React from 'react'
import ReactDOMServer from 'react-dom/server'
import express from 'express'

const PORT = process.env.PORT || 3000
const app = express()

app.get('/', (req, res) => {
	return res.send(ReactDOMServer.renderToString(<h1>ok</h1>))
})

app.get('/bar-chart.svg', (req, res) => {
	return res.send(ReactDOMServer.renderToString(<svg />))
})

app.get('/bar-chart.svg', (req, res) => {
	return res.send(ReactDOMServer.renderToString(<svg />))
})

app.get('/bar-chart.svg', (req, res) => {
	return res.send(ReactDOMServer.renderToString(<svg />))
})

app.get('/image.png', (req, res) => {
	return res.send(ReactDOMServer.renderToString(<svg />))
})

app.listen(PORT, () => {
	console.log(`Server is listening on port ${PORT}`)
})
