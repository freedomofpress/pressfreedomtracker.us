import classNames from 'classnames'
import React from 'react'
import PropTypes from 'prop-types'

export const categorySymbolMap = {
	'Arrest / Criminal Charge': 'arrest',
	'Border Stop': 'border_stop',
	'Denial of Access': 'denial_of_access',
	'Equipment Search or Seizure': 'equipment_search',
	Assault: 'assault',
	'Leak Case': 'leak_case',
	'Subpoena / Legal Order': 'subpoena',
	'Equipment Damage': 'equipment_damage',
	'Prior Restraint': 'prior_restraint',
	'Chilling Statement': 'chilling_statement',
	'Other Incident': 'other_incident',
}

export default function CategoryIcon({ category }) {
	return (<div className={classNames('category', `category-${categorySymbolMap[category] || category}`)} />)
}

CategoryIcon.propTypes = {
	category: PropTypes.string,
}

CategoryIcon.defaultProps = {
	category: '',
}
