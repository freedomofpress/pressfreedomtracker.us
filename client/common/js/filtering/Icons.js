import React from 'react'


export function SettingsIcon() {
	return (
		<svg
			width="16"
			height="16"
			viewBox="0 0 16 16"
			xmlns="http://www.w3.org/2000/svg"
			className="filters__icon"
		>
			<path d="M4 7H3V2h1v5zm-1 7h1v-3H3v3zm5 0h1V8H8v6zm5 0h1v-2h-1v2zm1-12h-1v6h1V2zM9 2H8v2h1V2zM5 8H2c-.55 0-1 .45-1 1s.45 1 1 1h3c.55 0 1-.45 1-1s-.45-1-1-1zm5-3H7c-.55 0-1 .45-1 1s.45 1 1 1h3c.55 0 1-.45 1-1s-.45-1-1-1zm5 4h-3c-.55 0-1 .45-1 1s.45 1 1 1h3c.55 0 1-.45 1-1s-.45-1-1-1z" fill="currentColor" fillRule="evenodd"/>
		</svg>
	)
}


export function ExpandIcon() {
	return (
		<svg 
			width="12"
			height="16"
			viewBox="0 0 12 16"
			xmlns="http://www.w3.org/2000/svg"
			className="expand__icon"
		>
			<title>Expand</title>
			<path d="M12 9H7v5H5V9H0V7h5V2h2v5h5" fill="currentColor" fillRule="evenodd"/>
		</svg>
	)
}


export function CollapseIcon() {
	return (
		<svg
			width="8"
			height="16"
			viewBox="0 0 8 16"
			xmlns="http://www.w3.org/2000/svg"
			className="collapse__icon"
		>
		  <title>Collapse</title>
		  <path d="M0 7v2h8V7" fill="currentColor" fillRule="evenodd"/>
		</svg>
	)
}
