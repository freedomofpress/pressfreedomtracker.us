import classlist from 'classlist-polyfill'
import 'element-dataset'
import 'normalize-css/normalize.css'
import axios from 'axios'

axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'

import '../css/common.sass'
import '~/slidingnav'
import '~/infinitescrolling'

window.React = require('react')
window.ReactDOM = require('react-dom')
window.IncidentFiltering = require('~/IncidentFiltering')
