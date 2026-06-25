import { body, data, token, onPageReady } from "../main.js";

const API_URL = "http://api.fi-track.manavkashyap.com";

// ─── DOM References ───────────────────────────────────────────────────────────
const nextPageBtn        = document.getElementById("budget-next-page");
const prevPageBtn        = document.getElementById("budget-prev-page");
const searchBtn          = document.getElementById("budget-search-btn");
const searchInputEl      = document.getElementById("budget-search-input");
const filterToggleBtns   = document.querySelectorAll(".budget-filter-toggle");
const filterOptionsEl    = document.getElementById("budget-filter-options");
const lowerAmountEl      = document.getElementById("budget-lower-amount");
const greaterAmountEl    = document.getElementById("budget-greater-amount");
const exactAmountEl      = document.getElementById("budget-exact-amount");
const startDateFilterEl  = document.getElementById("budget-start-date-filter");
const endDateFilterEl    = document.getElementById("budget-end-date-filter");

const budgetAddForm      = document.getElementById("budget-addition-form");
const budgetEditForm     = document.getElementById("budget-edit-form");
const deleteBudgetBtn    = document.getElementById("delete-budget-btn");
const refreshStatusBtn   = document.getElementById("refresh-budget-status");

const budgetListGrid     = document.getElementById("budget-list-grid");
const budgetEmptyState   = document.getElementById("budget-empty-state");
const addErrorEl         = document.getElementById("budget-add-error");
const editErrorEl        = document.getElementById("budget-edit-error");
const budgetStatusPanel  = document.getElementById("budget-status-panel");

// ─── Helpers ─────────────────────────────────────────────────────────────────
function parseFilterNumber(value) {
  if (value === null || value === undefined || value === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function formatMoney(amount) {
  return `₹${Number(amount).toLocaleString("en-IN")}`;
}

function formatDate(dateStr) {
  if (!dateStr) return "—";
  const d = new Date(dateStr);
  return `${d.getDate()}-${d.getMonth() + 1}-${d.getFullYear()}`;
}

function showError(el, message) {
  if (!el) return;
  el.textContent = message;
  el.classList.remove("hidden");
}

function clearError(el) {
  if (!el) return;
  el.textContent = "";
  el.classList.add("hidden");
}

// ─── Search State ─────────────────────────────────────────────────────────────
function getBudgetSearchState() {
  const input          = searchInputEl?.value?.trim() ?? "";
  const lower          = parseFilterNumber(lowerAmountEl?.value);
  const greater        = parseFilterNumber(greaterAmountEl?.value);
  const exact          = parseFilterNumber(exactAmountEl?.value);
  const start_date     = startDateFilterEl?.value || null;
  const end_date       = endDateFilterEl?.value || null;
  const category_name  = input || null;

  // Sync back to rivets data model
  data.budget.search.input                = input;
  data.budget.search.lower_budget_amount  = lower;
  data.budget.search.greater_budget_amount= greater;
  data.budget.search.exact_budget_amount  = exact;
  data.budget.search.start_date           = start_date;
  data.budget.search.end_date             = end_date;

  return { category_name, lower_budget_amount: lower, greater_budget_amount: greater, exact_budget_amount: exact, start_date, end_date };
}

// ─── Payload Builder ──────────────────────────────────────────────────────────
function buildBudgetPayload({ amount, start_date, end_date, category_name }) {
  return {
    amount: parseInt(amount, 10) || 0,
    start_date: start_date || null,
    end_date: end_date || null,
    category_name: category_name || "",
  };
}

// ─── Overlay Helpers ──────────────────────────────────────────────────────────
function showAddOverlay() {
  const overlay = document.getElementById("budget-addition-screen");
  if (overlay) {
    overlay.classList.remove("hidden");
    overlay.style.display = "flex";
  }
}

function hideAddOverlay() {
  const overlay = document.getElementById("budget-addition-screen");
  if (overlay) {
    overlay.classList.add("hidden");
    overlay.style.display = "none";
  }
}

function showEditOverlay() {
  const overlay = document.getElementById("budget-edit-screen");
  if (overlay) {
    overlay.classList.remove("hidden");
    overlay.style.display = "flex";
  }
}

function hideEditOverlay() {
  const overlay = document.getElementById("budget-edit-screen");
  if (overlay) {
    overlay.classList.add("hidden");
    overlay.style.display = "none";
  }
  budgetStatusPanel?.classList.add("hidden");
}

// ─── Card Renderer ────────────────────────────────────────────────────────────
function renderBudgetCards(list) {
  if (!budgetListGrid) return;

  if (!list || list.length === 0) {
    budgetListGrid.innerHTML = "";
    budgetEmptyState?.classList.remove("hidden");
    return;
  }

  budgetEmptyState?.classList.add("hidden");

  budgetListGrid.innerHTML = list
    .map((b) => {
      return `
        <div class="overview-card relative flex flex-col gap-3">
          <!-- Header -->
          <div class="flex items-start justify-between gap-2">
            <div>
              <span class="text-8xl absolute -z-10 text-black/10 dark:text-white/10 right-5 -bottom-5 font-bold">
                ₹
              </span>
              <p class="font-semibold text-lg capitalize leading-tight">${b.category_name || "Uncategorized"}</p>
              <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
                ${formatDate(b.start_date)} → ${formatDate(b.end_date)}
              </p>
            </div>
            <button
              type="button"
              data-budget-id="${b.id}"
              class="open-budget-editor flex items-center gap-1 bg-gray-200 dark:bg-gray-700 px-2 py-1.5 rounded-md cursor-pointer text-xs font-medium shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                stroke="currentColor" class="size-3.5 pointer-events-none">
                <path stroke-linecap="round" stroke-linejoin="round"
                  d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
              </svg>
              Edit
            </button>
          </div>

          <!-- Amount -->
          <div class="flex items-center gap-2 font-bold text-2xl">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
              stroke="currentColor" class="size-7">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M15 8.25H9m6 3H9m3 6-3-3h1.5a3 3 0 1 0 0-6M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
            </svg>
            <span>${Number(b.amount).toLocaleString("en-IN")}</span>
          </div>

          <!-- Category ID badge -->
          <div class="flex items-center justify-between text-xs text-gray-400 dark:text-gray-500">
            <span>Category ID: ${b.category_id}</span>
            <button
              type="button"
              data-budget-id="${b.id}"
              class="check-budget-status text-blue-500 hover:underline cursor-pointer font-medium">
              Check Status →
            </button>
          </div>
        </div>
      `;
    })
    .join("");
}

// ─── Open Editor ─────────────────────────────────────────────────────────────
function openBudgetEditor(budgetId) {
  const list = data.budget.list;
  const b = list.find((item) => Number(item.id) === Number(budgetId));
  if (!b) return;

  const startStr = b.start_date ? new Date(b.start_date).toISOString().slice(0, 10) : "";
  const endStr   = b.end_date   ? new Date(b.end_date).toISOString().slice(0, 10)   : "";

  data.budget.budgetToEdit = {
    id: b.id,
    category_name: b.category_name || "",
    amount: b.amount,
    start_date: startStr,
    end_date: endStr,
    category_id: b.category_id,
  };

  // Manually set form values (rivets may or may not be bound at edit time)
  const nameEl  = document.getElementById("budget_category_name_edit");
  const amtEl   = document.getElementById("budget_amount_edit");
  const startEl = document.getElementById("budget_start_date_edit");
  const endEl   = document.getElementById("budget_end_date_edit");

  if (nameEl)  nameEl.value  = data.budget.budgetToEdit.category_name;
  if (amtEl)   amtEl.value   = data.budget.budgetToEdit.amount;
  if (startEl) startEl.value = data.budget.budgetToEdit.start_date;
  if (endEl)   endEl.value   = data.budget.budgetToEdit.end_date;

  if (deleteBudgetBtn) deleteBudgetBtn.setAttribute("data-budget-id", b.id);

  budgetStatusPanel?.classList.add("hidden");
  clearError(editErrorEl);
  showEditOverlay();
}

// ─── Budget Status ────────────────────────────────────────────────────────────
async function loadBudgetStatus(budgetId) {
  if (!budgetId) return;
  try {
    const response = await fetch(`${API_URL}/api/v1/budget/budget-status/${budgetId}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });
    if (!response.ok) throw new Error("Failed to fetch budget status");
    const result = await response.json();

    const { spent, budget, remaining, status } = result;
    const pct = budget > 0 ? Math.min(Math.round((spent / budget) * 100), 100) : 0;

    document.getElementById("status-budget-amount").textContent   = formatMoney(budget);
    document.getElementById("status-spent-amount").textContent    = formatMoney(spent);
    document.getElementById("status-remaining-amount").textContent= formatMoney(remaining);

    const bar = document.getElementById("status-progress-bar");
    if (bar) {
      bar.style.width = `${pct}%`;
      bar.className = `h-2 rounded-full transition-all duration-500 ${status === "over" ? "bg-red-500" : pct >= 80 ? "bg-yellow-400" : "bg-green-500"}`;
    }

    const pctLabel = document.getElementById("status-percent-label");
    if (pctLabel) pctLabel.textContent = `${pct}% used`;

    const badge = document.getElementById("status-badge");
    if (badge) {
      badge.textContent  = status === "over" ? "Over Budget" : "Under Budget";
      badge.className    = `px-2 py-0.5 rounded-full text-xs font-semibold ${status === "over" ? "bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400" : "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"}`;
    }

    budgetStatusPanel?.classList.remove("hidden");
  } catch (err) {
    console.error("Error loading budget status:", err);
  }
}

// ─── API: Get Budgets ─────────────────────────────────────────────────────────
async function getBudgets({
  page                = 1,
  limit               = 10,
  category_name       = null,
  lower_budget_amount = null,
  greater_budget_amount = null,
  exact_budget_amount = null,
  start_date          = null,
  end_date            = null,
} = {}) {
  data.budget.loading = true;
  data.budget.error   = null;

  const params = new URLSearchParams();
  params.append("page",  String(page));
  params.append("limit", String(limit));
  if (category_name)        params.append("category_name",        category_name);
  if (lower_budget_amount   != null) params.append("lower_budget_amount",   String(lower_budget_amount));
  if (greater_budget_amount != null) params.append("greater_budget_amount", String(greater_budget_amount));
  if (exact_budget_amount   != null) params.append("exact_budget_amount",   String(exact_budget_amount));
  if (start_date)           params.append("start_date", start_date);
  if (end_date)             params.append("end_date",   end_date);

  try {
    const response = await fetch(`${API_URL}/api/v1/budget/?${params.toString()}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });
    if (!response.ok) throw new Error("Failed to fetch budgets");
    const result = await response.json();

    // The backend returns a plain list (List[budgetResponse]), not paginated
    const list = Array.isArray(result) ? result : (result.budgets ?? []);
    data.budget.list.splice(0, data.budget.list.length, ...list);

    // Handle pagination — backend may return total_pages; fall back to 1
    data.budget.page.total_pages   = result.total_pages   ?? 1;
    data.budget.page.current_page  = result.current_page  ?? page;
    data.budget.page.total_budgets = result.total_budgets ?? list.length;

    renderBudgetCards(list);
  } catch (err) {
    console.error("Error fetching budgets:", err);
    data.budget.error = err.message;
    renderBudgetCards([]);
  } finally {
    data.budget.loading = false;
  }
}

// ─── API: Add Budget ──────────────────────────────────────────────────────────
async function addBudget(payload) {
  data.budget.loading = true;
  data.budget.error   = null;
  clearError(addErrorEl);
  try {
    const response = await fetch(`${API_URL}/api/v1/budget/create`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
      body: JSON.stringify(payload),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(result.detail || result.message || `Failed to add budget: ${response.status}`);
    }
    if (budgetAddForm) budgetAddForm.reset();
    hideAddOverlay();
    await getBudgets({ page: data.budget.page.current_page, ...getBudgetSearchState() });
  } catch (err) {
    console.error("Error adding budget:", err);
    showError(addErrorEl, err.message || "Failed to add budget.");
  } finally {
    data.budget.loading = false;
  }
}

// ─── API: Edit Budget ─────────────────────────────────────────────────────────
async function editBudget({ budgetId, payload } = {}) {
  if (!budgetId) return;
  data.budget.loading = true;
  data.budget.error   = null;
  clearError(editErrorEl);
  try {
    const response = await fetch(`${API_URL}/api/v1/budget/update/${budgetId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
      body: JSON.stringify(payload),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(result.detail || result.message || "Failed to update budget");
    }
    hideEditOverlay();
    await getBudgets({ page: data.budget.page.current_page, ...getBudgetSearchState() });
  } catch (err) {
    console.error("Error editing budget:", err);
    showError(editErrorEl, err.message || "Failed to update budget.");
  } finally {
    data.budget.loading = false;
  }
}

// ─── API: Delete Budget ───────────────────────────────────────────────────────
async function deleteBudget(budgetId) {
  if (!budgetId) return;
  data.budget.loading = true;
  data.budget.error   = null;
  try {
    const response = await fetch(`${API_URL}/api/v1/budget/delete/${budgetId}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });
    if (!response.ok) throw new Error("Failed to delete budget");

    // Optimistic removal
    const kept = data.budget.list.filter((b) => Number(b.id) !== Number(budgetId));
    data.budget.list.splice(0, data.budget.list.length, ...kept);
    renderBudgetCards(data.budget.list);
    hideEditOverlay();
  } catch (err) {
    console.error("Error deleting budget:", err);
    data.budget.error = err.message;
  } finally {
    data.budget.loading = false;
  }
}

// ─── Form Submit: Add ─────────────────────────────────────────────────────────
if (budgetAddForm) {
  budgetAddForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError(addErrorEl);

    const category_name = document.getElementById("budget_category_name")?.value?.trim();
    const amount        = document.getElementById("budget_amount")?.value;
    const start_date    = document.getElementById("budget_start_date")?.value;
    const end_date      = document.getElementById("budget_end_date")?.value;

    if (!category_name) {
      showError(addErrorEl, "Please enter a category name.");
      return;
    }
    if (!amount || parseInt(amount, 10) <= 0) {
      showError(addErrorEl, "Please enter a valid amount greater than 0.");
      return;
    }
    if (!start_date || !end_date) {
      showError(addErrorEl, "Please select both start and end dates.");
      return;
    }
    if (new Date(start_date) >= new Date(end_date)) {
      showError(addErrorEl, "Start date must be before end date.");
      return;
    }

    const payload = buildBudgetPayload({ amount, start_date, end_date, category_name });
    await addBudget(payload);
  });
}

// ─── Form Submit: Edit ────────────────────────────────────────────────────────
if (budgetEditForm) {
  budgetEditForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError(editErrorEl);

    const id = data.budget.budgetToEdit?.id;
    if (!id) return;

    const category_name = document.getElementById("budget_category_name_edit")?.value?.trim()  ?? data.budget.budgetToEdit.category_name;
    const amount        = document.getElementById("budget_amount_edit")?.value                  ?? data.budget.budgetToEdit.amount;
    const start_date    = document.getElementById("budget_start_date_edit")?.value              ?? data.budget.budgetToEdit.start_date;
    const end_date      = document.getElementById("budget_end_date_edit")?.value                ?? data.budget.budgetToEdit.end_date;

    if (!amount || parseInt(amount, 10) <= 0) {
      showError(editErrorEl, "Please enter a valid amount greater than 0.");
      return;
    }
    if (start_date && end_date && new Date(start_date) >= new Date(end_date)) {
      showError(editErrorEl, "Start date must be before end date.");
      return;
    }

    const payload = buildBudgetPayload({ amount, start_date, end_date, category_name });
    await editBudget({ budgetId: id, payload });
  });
}

// ─── Delete Button ────────────────────────────────────────────────────────────
if (deleteBudgetBtn) {
  deleteBudgetBtn.addEventListener("click", () => {
    const id = deleteBudgetBtn.getAttribute("data-budget-id");
    if (id) deleteBudget(id);
  });
}

// ─── Refresh Status Button ────────────────────────────────────────────────────
if (refreshStatusBtn) {
  refreshStatusBtn.addEventListener("click", () => {
    const id = data.budget.budgetToEdit?.id;
    if (id) loadBudgetStatus(id);
  });
}

// ─── Pagination ───────────────────────────────────────────────────────────────
if (nextPageBtn) {
  nextPageBtn.addEventListener("click", () => {
    const next = Math.min(data.budget.page.current_page + 1, data.budget.page.total_pages);
    getBudgets({ page: next, ...getBudgetSearchState() });
  });
}

if (prevPageBtn) {
  prevPageBtn.addEventListener("click", () => {
    const prev = Math.max(1, data.budget.page.current_page - 1);
    getBudgets({ page: prev, ...getBudgetSearchState() });
  });
}

// ─── Search ───────────────────────────────────────────────────────────────────
if (searchBtn) {
  searchBtn.addEventListener("click", () => {
    getBudgets({ page: 1, ...getBudgetSearchState() });
  });
}

if (searchInputEl) {
  searchInputEl.addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;
    e.preventDefault();
    getBudgets({ page: 1, ...getBudgetSearchState() });
  });
}

[lowerAmountEl, greaterAmountEl, exactAmountEl].forEach((input) => {
  if (!input) return;
  input.addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;
    e.preventDefault();
    getBudgets({ page: 1, ...getBudgetSearchState() });
  });
});

// ─── Filter Toggle ────────────────────────────────────────────────────────────
if (filterToggleBtns?.length && filterOptionsEl) {
  filterToggleBtns.forEach((btn) => {
    btn.addEventListener("click", () => filterOptionsEl.classList.toggle("hidden"));
  });
}

// ─── Body Click Delegation ────────────────────────────────────────────────────
body.addEventListener("click", (e) => {
  const target = e.target;

  // Open add overlay
  if (
    target.closest?.(".budget-screen-toggle") &&
    !target.closest?.("#budget-addition-screen")
  ) {
    showAddOverlay();
    return;
  }

  // Close add overlay from inside
  if (
    target.closest?.(".budget-screen-toggle") &&
    target.closest?.("#budget-addition-screen")
  ) {
    hideAddOverlay();
    return;
  }

  // Close edit overlay
  if (target.classList.contains("budget-edit-screen-toggle")) {
    hideEditOverlay();
    return;
  }

  // Open editor from card button
  if (target.classList.contains("open-budget-editor") || target.closest?.(".open-budget-editor")) {
    const btn = target.classList.contains("open-budget-editor") ? target : target.closest(".open-budget-editor");
    const id  = btn?.getAttribute("data-budget-id");
    if (id) openBudgetEditor(id);
    return;
  }

  // Check status from card
  if (target.classList.contains("check-budget-status")) {
    const id = target.getAttribute("data-budget-id");
    if (id) {
      openBudgetEditor(id);
      // Load status after overlay is shown
      setTimeout(() => loadBudgetStatus(id), 100);
    }
    return;
  }
});

// ─── Init ─────────────────────────────────────────────────────────────────────
onPageReady(() => {
  // Seed the budget namespace in data if main.js hasn't already added it
  if (!data.budget) {
    data.budget = {
      list: [],
      loading: false,
      error: null,
      page: { total_pages: 1, current_page: 1, total_budgets: 0 },
      search: {
        input: "",
        lower_budget_amount: null,
        greater_budget_amount: null,
        exact_budget_amount: null,
        start_date: null,
        end_date: null,
      },
      budgetToEdit: {
        id: null,
        category_name: "",
        amount: "",
        start_date: "",
        end_date: "",
        category_id: null,
      },
    };
  }

  getBudgets({ page: data.budget.page.current_page });
});