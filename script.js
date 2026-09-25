document.querySelector('#year').textContent = new Date().getFullYear()

const rotatingWord = document.querySelector('.rotating-word')
const words = ['stage.', 'studio.', 'school.', 'lab.']
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)')
const themeToggle = document.querySelector('.theme-toggle')
const darkTheme = window.matchMedia('(prefers-color-scheme: dark)')
const logoMark = document.querySelector('.logo-mark')

const isDarkTheme = () =>
  document.documentElement.dataset.theme
    ? document.documentElement.dataset.theme === 'dark'
    : darkTheme.matches

const updateThemeToggle = () => {
  const isDark = isDarkTheme()

  if (logoMark) logoMark.src = isDark ? 'site-logo-dark.svg' : 'site-logo.svg'
  themeToggle.setAttribute('aria-pressed', String(isDark))
  themeToggle.setAttribute('aria-label', `Switch to ${isDark ? 'light' : 'dark'}`)
  themeToggle.innerHTML = isDark
    ? '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>'
    : '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 3a9 9 0 1 0 9 9c-5 1-9-3-9-9Z"/></svg>'
}

if (themeToggle) {
  updateThemeToggle()

  themeToggle.addEventListener('click', () => {
    const isDark = isDarkTheme()

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
