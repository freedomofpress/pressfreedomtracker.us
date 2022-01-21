import React from 'react'
import ReactDOM from 'react-dom'

export function Tooltip({ wrapper, content, x, y }) {
  const offsetX = 10
  const offletY = 60
  if (wrapper) {
    return ReactDOM.createPortal(
      <div
        style={{
          position: 'fixed',
          top: `${y - offletY}px`,
          left: `${x + offsetX}px`,
          backgroundColor: 'white',
          border: '5px solid black',
          pointerEvents: 'none',
          padding: 12,
        }}
      >
        {content}
      </div>,
      wrapper
    )
  } else return null
}
