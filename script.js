document.querySelector("#year").textContent = new Date().getFullYear();

const rotatingWord = document.querySelector(".rotating-word");
const words = ["lab.", "studio.", "stage.", "school."];
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

if (rotatingWord && !reduceMotion.matches) {
  let wordIndex = 0;

  window.setInterval(() => {
    rotatingWord.classList.add("is-changing");

    window.setTimeout(() => {
      wordIndex = (wordIndex + 1) % words.length;
      rotatingWord.textContent = words[wordIndex];
      rotatingWord.classList.remove("is-changing");
    }, 180);
  }, 2800);
}
