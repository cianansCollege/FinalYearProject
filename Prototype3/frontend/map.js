// Province card highlight helpers for displaying the predicted label.

export function updateMap(label) {
  const cards = document.querySelectorAll(".province-card");

  cards.forEach((card) => {
    card.classList.remove("active");

    if (card.dataset.province === label) {
      card.classList.add("active");
    }
  });
}

export function clearMapHighlight() {
  const cards = document.querySelectorAll(".province-card");
  cards.forEach((card) => card.classList.remove("active"));
}
