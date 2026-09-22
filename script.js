document.querySelector('#year').textContent = new Date().getFullYear()

const rotatingWord = document.querySelector('.rotating-word')
const words = ['stage.', 'studio.', 'school.', 'lab.']
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)')
const themeToggle = document.querySelector('.theme-toggle')
const darkTheme = window.matchMedia('(prefers-color-scheme: dark)')

const updateThemeToggle = () => {
  const isDark = document.documentElement.dataset.theme
    ? document.documentElement.dataset.theme === 'dark'
    : darkTheme.matches

  themeToggle.setAttribute('aria-pressed', String(isDark))
  themeToggle.textContent = `Switch to ${isDark ? 'light' : 'dark'}`
}

if (themeToggle) {
  updateThemeToggle()

  themeToggle.addEventListener('click', () => {
    const isDark = document.documentElement.dataset.theme
      ? document.documentElement.dataset.theme === 'dark'
      : darkTheme.matches

    document.documentElement.dataset.theme = isDark ? 'light' : 'dark'
    updateThemeToggle()
  })

  darkTheme.addEventListener('change', () => {
    if (!document.documentElement.dataset.theme) updateThemeToggle()
  })
}

if (rotatingWord && !reduceMotion.matches) {
  let wordIndex = 0

  window.setInterval(() => {
    rotatingWord.classList.add('is-changing')

    window.setTimeout(() => {
      wordIndex = (wordIndex + 1) % words.length
      rotatingWord.textContent = words[wordIndex]
      rotatingWord.classList.remove('is-changing')
    }, 180)
  }, 2800)
}
