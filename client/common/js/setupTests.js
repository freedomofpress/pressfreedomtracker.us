import '@testing-library/jest-dom'

// jsdom has no ResizeObserver, which ParentSize uses to measure the charts.
globalThis.ResizeObserver = class ResizeObserver {
	observe() {}

	unobserve() {}

	disconnect() {}
}

// Chart components fetch their dataset on mount; jsdom has no fetch, and tests
// shouldn't reach the network.
globalThis.fetch = () => Promise.resolve({
	ok: true,
	status: 200,
	text: () => Promise.resolve(''),
	json: () => Promise.resolve([]),
})
