// The only thing that needs JS: copy the case link (with a fallback when the clipboard is not available)
document.addEventListener("click", function (ev) {
  var b = ev.target.closest("[data-copiar]");
  if (!b) return;
  var url = b.getAttribute("data-copiar"), ok = b.getAttribute("data-ok"), antes = b.textContent;
  var listo = function () { b.textContent = ok; setTimeout(function () { b.textContent = antes; }, 1800); };
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(url).then(listo, function () { window.prompt && window.prompt("", url); });
  } else { window.prompt && window.prompt("", url); }
});
