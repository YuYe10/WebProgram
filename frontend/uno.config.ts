import { defineConfig, presetUno, presetIcons, presetTypography } from 'unocss'
import transformerDirectives from '@unocss/transformer-directives'
import transformerVariantGroup from '@unocss/transformer-variant-group'

export default defineConfig({
  presets: [
    presetUno(),
    presetIcons({
      scale: 1.2,
      extraProperties: {
        'display': 'inline-block',
        'vertical-align': 'middle',
      },
    }),
    presetTypography(),
  ],
  transformers: [
    transformerDirectives(),
    transformerVariantGroup(),
  ],
  theme: {
    colors: {
      brand: {
        50: '#eef2ff',
        100: '#e0e7ff',
        200: '#c7d2fe',
        300: '#a5b4fc',
        400: '#818cf8',
        500: '#6366f1',
        600: '#4f46e5',
        700: '#4338ca',
        800: '#3730a3',
        900: '#312e81',
      },
    },
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      mono: ['JetBrains Mono', 'monospace'],
    },
  },
  shortcuts: {
    'glass': 'bg-white/70 dark:bg-gray-900/70 backdrop-blur-xl border border-white/20 dark:border-gray-800/30',
    'glass-card': 'glass rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300',
    'btn': 'inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed',
    'btn-primary': 'btn bg-brand-500 text-white hover:bg-brand-600 shadow-sm hover:shadow-md',
    'btn-secondary': 'btn bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700',
    'btn-ghost': 'btn text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800',
    'btn-danger': 'btn bg-red-500 text-white hover:bg-red-600',
    'input': 'w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all duration-200 outline-none',
    'page-transition': 'transition-all duration-200 ease-out',
  },
})
