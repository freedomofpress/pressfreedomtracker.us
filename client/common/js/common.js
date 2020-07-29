import classlist from 'classlist-polyfill'
import 'element-dataset'
import 'normalize-css/normalize.css'
import 'react-datepicker/dist/react-datepicker.css'
import axios from 'axios'

axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

import '../sass/common.sass'
import '~/slidingnav'
import '~/IncidentLoader'
import '~/emails'
import '~/tabs'

import React from 'react'
import ReactDOM from 'react-dom'
import IncidentFiltering from '~/filtering/IncidentFiltering'

window.React = React
window.ReactDOM = ReactDOM
window.IncidentFiltering = IncidentFiltering
