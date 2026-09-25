document.querySelector('#year').textContent = new Date().getFullYear()

const rotatingWord = document.querySelector('.rotating-word')
const typedWord = document.querySelector('.typed-word')
const words = ['stage.', 'studio.', 'school.', 'lab.']
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
    : '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>'
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

const wait = (ms) => new Promise((resolve) => window.setTimeout(resolve, ms))

// Runs even when motion is reduced: CSS hides it and shows the static word list instead
const typeWords = async () => {
  let wordIndex = 0

  while (true) {
    await wait(2200)
    rotatingWord.classList.add('is-typing')

    const word = words[wordIndex]
    for (let i = word.length - 1; i >= 0; i--) {
      typedWord.textContent = word.slice(0, i)
      await wait(55)
    }

    wordIndex = (wordIndex + 1) % words.length
    const nextWord = words[wordIndex]
    await wait(250)

    for (let i = 1; i <= nextWord.length; i++) {
      typedWord.textContent = nextWord.slice(0, i)
      await wait(95)
    }

    rotatingWord.classList.remove('is-typing')
  }
}

if (rotatingWord && typedWord) typeWords()
