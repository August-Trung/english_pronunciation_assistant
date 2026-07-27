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
    background: '#F8FAFC',  // Slate 50 ultra-soft clean background
    surface: '#FFFFFF',
    primary: '#0284C7',     // Sky Blue 600
    secondary: '#0F172A',   // Slate 900
    success: '#10B981',     // Emerald 500
    warning: '#F59E0B',     // Amber 500
    error: '#F43F5E',       // Rose 500
    info: '#6366F1',        // Indigo 500
    accent: '#8B5CF6',      // Purple 500
  },
}

export default createVuetify({
  theme: {
    defaultTheme: 'lightTheme',
    themes: {
      lightTheme,
    },
  },
  defaults: {
    VCard: {
      rounded: 'lg',
      elevation: 0,
    },
    VBtn: {
      rounded: 'lg',
      elevation: 0,
    },
    VChip: {
      rounded: 'md',
    },
    VTextField: {
      rounded: 'lg',
    },
    VSelect: {
      rounded: 'lg',
    },
    VDialog: {
      rounded: 'lg',
    },
  },
})
