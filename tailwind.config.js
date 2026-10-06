/**
 * Static Tailwind build configuration for lietuva.chat.
 * Regenerate with: npx -y tailwindcss@3 -c tailwind.config.js -i tailwind.input.css -o static/tw.css --minify
 */
module.exports = {
  content: [
    'main.py',
    'components/**/*.py',
    'pages/**/*.py',
    'chat/**/*.py',
    'admin/**/*.py',
    'static/**/*.js',
    'static/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        accent: 'var(--accent)',
        'accent-soft': 'var(--accent-soft)',
        ink: {
          DEFAULT: 'var(--ink)',
          2: 'var(--ink-2)',
          3: 'var(--ink-3)',
        },
        line: 'var(--line)',
        'bg-alt': 'var(--bg-alt)',
        surface: 'var(--surface)',
      },
      fontFamily: {
        display: ['Geist', 'system-ui', 'sans-serif'],
        sans: ['Geist', 'system-ui', 'sans-serif'],
        mono: ['"Geist Mono"', 'ui-monospace', 'monospace'],
      },
    },
  },
};
