/* TaskFlow — progressive enhancement. No external dependencies. */
(function () {
  "use strict";

  /* ---------------------------------------------------------- Theme */
  var root = document.documentElement;
  try {
    var saved = localStorage.getItem("taskflow-theme");
    if (saved) root.setAttribute("data-theme", saved);
  } catch (e) {}

  function toggleTheme() {
    var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try { localStorage.setItem("taskflow-theme", next); } catch (e) {}
  }

  /* ----------------------------------------------------- Count-up */
  function animateCount(el) {
    var target = parseFloat(el.getAttribute("data-count")) || 0;
    var suffix = el.getAttribute("data-suffix") || "";
    var duration = 900;
    var start = null;

    function step(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased) + suffix;
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = target + suffix;
    }
    requestAnimationFrame(step);
  }

  /* ------------------------------------------------- Bars / donuts */
  function fillBar(el) {
    var v = el.getAttribute("data-value") || "0";
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { el.style.width = v + "%"; });
    });
  }
  function fillDonut(el) {
    var v = parseFloat(el.getAttribute("data-value")) || 0;
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { el.style.setProperty("--pct", v); });
    });
  }

  /* --------------------------------------------------- On ready */
  function onReady() {
    var toggle = document.querySelector("[data-theme-toggle]");
    if (toggle) toggle.addEventListener("click", toggleTheme);

    var navToggle = document.querySelector("[data-nav-toggle]");
    var nav = document.querySelector("[data-nav]");
    if (navToggle && nav) {
      navToggle.addEventListener("click", function () { nav.classList.toggle("is-open"); });
    }

    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* Reveal on scroll + trigger inner animations when visible */
    var reveals = document.querySelectorAll(".reveal");
    function activate(el) {
      el.classList.add("is-visible");
      el.querySelectorAll("[data-count]").forEach(animateCount);
      el.querySelectorAll(".bar__fill").forEach(fillBar);
      el.querySelectorAll(".progress-line__fill").forEach(fillBar);
      el.querySelectorAll(".donut").forEach(fillDonut);
    }

    if (reduce || !("IntersectionObserver" in window)) {
      reveals.forEach(activate);
      document.querySelectorAll("[data-count]").forEach(animateCount);
      document.querySelectorAll(".bar__fill, .progress-line__fill").forEach(fillBar);
      document.querySelectorAll(".donut").forEach(fillDonut);
    } else {
      var io = new IntersectionObserver(function (entries, obs) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) { activate(entry.target); obs.unobserve(entry.target); }
        });
      }, { threshold: 0.15 });
      reveals.forEach(function (el) { io.observe(el); });

      /* Elements not wrapped in .reveal still animate immediately */
      document.querySelectorAll(".bar__fill").forEach(function (el) {
        if (!el.closest(".reveal")) fillBar(el);
      });
      document.querySelectorAll(".donut").forEach(function (el) {
        if (!el.closest(".reveal")) fillDonut(el);
      });
      document.querySelectorAll("[data-count]").forEach(function (el) {
        if (!el.closest(".reveal")) animateCount(el);
      });
    }

    /* Auto-dismiss toasts */
    document.querySelectorAll(".toast").forEach(function (toast, i) {
      setTimeout(function () {
        toast.style.transition = "opacity .4s ease, transform .4s ease";
        toast.style.opacity = "0";
        toast.style.transform = "translateX(30px)";
        setTimeout(function () { toast.remove(); }, 400);
      }, 4200 + i * 400);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", onReady);
  } else {
    onReady();
  }
})();
