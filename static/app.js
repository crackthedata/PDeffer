(function () {
  const listEl = document.getElementById("merge-order");
  const fieldEl = document.getElementById("merge-files-sync");
  const formMerge = document.getElementById("form-merge");
  if (!listEl || !fieldEl || !formMerge) return;

  function syncField() {
    const names = [...listEl.querySelectorAll("[data-filename]")].map((el) =>
      el.getAttribute("data-filename")
    );
    fieldEl.value = names.join("\n");
  }

  function addItem(filename) {
    const li = document.createElement("li");
    li.className = "merge-order-item";
    li.setAttribute("data-filename", filename);
    li.innerHTML =
      '<span class="merge-order-name"></span>' +
      '<span class="merge-order-actions">' +
      '<button type="button" class="btn-icon merge-move-up" aria-label="Move up">↑</button>' +
      '<button type="button" class="btn-icon merge-move-down" aria-label="Move down">↓</button>' +
      '<button type="button" class="btn-icon merge-remove" aria-label="Remove">×</button>' +
      "</span>";
    li.querySelector(".merge-order-name").textContent = filename;
    listEl.appendChild(li);
    syncField();
    listEl.closest(".merge-empty-wrap")?.classList.remove("is-empty");
  }

  document.querySelectorAll(".merge-add").forEach((btn) => {
    btn.addEventListener("click", () => {
      const name = btn.getAttribute("data-file");
      if (name) addItem(name);
    });
  });

  listEl.addEventListener("click", (e) => {
    const t = e.target;
    if (!(t instanceof HTMLElement)) return;
    const li = t.closest(".merge-order-item");
    if (!li) return;
    if (t.classList.contains("merge-remove")) {
      li.remove();
      syncField();
      if (!listEl.children.length) {
        listEl.closest(".merge-empty-wrap")?.classList.add("is-empty");
      }
      return;
    }
    if (t.classList.contains("merge-move-up")) {
      const prev = li.previousElementSibling;
      if (prev) listEl.insertBefore(li, prev);
      syncField();
      return;
    }
    if (t.classList.contains("merge-move-down")) {
      const next = li.nextElementSibling;
      if (next) listEl.insertBefore(next, li);
      syncField();
    }
  });

  document.querySelector(".merge-clear")?.addEventListener("click", () => {
    listEl.innerHTML = "";
    syncField();
    listEl.closest(".merge-empty-wrap")?.classList.add("is-empty");
  });

  formMerge.addEventListener("submit", (e) => {
    syncField();
    if (!fieldEl.value.trim()) {
      e.preventDefault();
      alert("Add at least one PDF to the merge order (use the buttons below).");
    }
  });

  syncField();
})();
