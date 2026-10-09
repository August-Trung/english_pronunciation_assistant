/**
 * plugins/vuetify.js
 *
 * Framework documentation: https://vuetifyjs.com
 */

// Composables
import { createVuetify } from 'vuetify'

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

const lightTheme = {
  dark: false,
  colors: {
    background: '#F4F6F9',
    surface: '#FFFFFF',
    primary: '#03A9F4',     // Sky Blue for student friendly environment
    secondary: '#1976D2',   // Trustworthy Deep Blue
    success: '#4CAF50',     // Bright encouraging Green
    warning: '#FF9800',     // Warm Amber/Orange
    error: '#FF5252',       // Cheerful Coral/Red
    info: '#9C27B0',        // Cheerful Purple
  },
}

export default createVuetify({
  theme: {
    defaultTheme: 'lightTheme',
    themes: {
      lightTheme,
    },
  },
})
