document.addEventListener("DOMContentLoaded", () => {
  const revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.01, rootMargin: "0px 0px -10% 0px" });
    revealEls.forEach((el) => io.observe(el));
    // Safety net: never let content stay offset if IO misses a fast/programmatic scroll.
    setTimeout(() => revealEls.forEach((el) => el.classList.add("in-view")), 2000);
  } else {
    revealEls.forEach((el) => el.classList.add("in-view"));
  }
});
