import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import * as parserVue from 'vue-eslint-parser'
import * as parserTs from '@typescript-eslint/parser'
import pluginTs from '@typescript-eslint/eslint-plugin'

export default [
  js.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  {
    files: ['**/*.{ts,vue}'],
    languageOptions: {
      parser: parserVue,
      parserOptions: {
        parser: parserTs,
        ecmaVersion: 2020,
        sourceType: 'module'
      },
      globals: {
        localStorage: 'readonly',
        window: 'readonly',
        setTimeout: 'readonly',
        fetch: 'readonly'
      }
    },
    plugins: {
      '@typescript-eslint': pluginTs
    },
    rules: {
      'vue/multi-word-component-names': 'off',
      'vue/max-attributes-per-line': 'off',
      'vue/singleline-html-element-content-newline': 'off',
      'vue/html-self-closing': 'off',
      'vue/html-closing-bracket-newline': 'off',
      'vue/html-indent': 'off',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      'no-unused-vars': 'off',
      'no-undef': 'off'
    }
  }
]
