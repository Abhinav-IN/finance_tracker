import { body, data, token, syncRivets, onPageReady, replaceList } from "../main.js";
import { renderTransactionRows } from "./lib/table-render.js";

API_URL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const nextPageBtn = document.getElementById("next-page");
const prevPageBtn = document.getElementById("prev-page");
const searchBtn = document.getElementById("search-btn");
const filterToggleBtn = document.querySelectorAll(".filter-toggle");
const filterOption = document.getElementById("filter-options");

const expenseForm = document.getElementById("expense-addition-form");
const expenseEditingForm = document.getElementById("edit-expense-form");
const searchInputEl = document.getElementById("search-input");
const lowerPriceEl = document.getElementById("lower-price");
const greaterPriceEl = document.getElementById("greater-price");
const exactPriceEl = document.getElementById("exact-price");
const listTableBody = document.getElementById("transaction-list-body");

function paintExpenseTable() {
  renderTransactionRows(listTableBody, data.expense.list, { editorClass: "open-expense-editor" });
}

function syncExpenseListEmpty() {
  data.expense.listEmpty = data.expense.list.length === 0;
}

function parseFilterNumber(value) {
  if (value === null || value === undefined || value === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function getExpenseSearchState() {
  const input = typeof data.expense.search.input === "string" ? data.expense.search.input.trim() : "";
  const lower = parseFilterNumber(data.expense.search.lower_price);
  const greater = parseFilterNumber(data.expense.search.greater_price);
  const exact = parseFilterNumber(data.expense.search.exact_price);

  data.expense.search.input = input;
  data.expense.search.lower_price = lower;
  data.expense.search.greater_price = greater;
  data.expense.search.exact_price = exact;

  return { search: input, lower_amount: lower, greater_amount: greater, exact_amount: exact };
}

function buildTransactionCreatePayload({ title, date, amount, category_name, payment_mode_name, description }) {
  const dateObj = date ? new Date(date) : new Date();
  return {
    title: title || "",
    date: dateObj.toISOString(),
    amount: parseFloat(amount) || 0,
    direction: "EXPENSE",
    transaction_type_name: "Nill",
    category_name: category_name || "",
    payment_mode_name: payment_mode_name || "",
    account_name: null,
    description: description || null,
  };
}

if (expenseForm) {
  expenseForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const title = document.getElementById("expense_name").value.trim();
    const amount = document.getElementById("expense_price").value;
    const date = document.getElementById("expense_date").value;
    const category_name = document.getElementById("expense_category").value;
    const payment_mode_name = document.getElementById("expense_payment_mode").value;
    const description = document.getElementById("expense_note").value.trim() || null;

    if (!title || !amount || parseFloat(amount) <= 0) {
      data.expense.error = "Please enter a name and a valid amount.";
      return;
    }
    data.expense.error = null;

    const payload = buildTransactionCreatePayload({
      title,
      date: date || new Date().toISOString().slice(0, 10),
      amount,
      category_name,
      payment_mode_name,
      description,
    });

    await addExpense(payload);
  });
}

if (expenseEditingForm) {
  expenseEditingForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = data.expense.expenseToEdit.id;
    if (!id) return;
    const payload = buildTransactionCreatePayload({
      title: document.getElementById("edit_expense_name")?.value?.trim() ?? data.expense.expenseToEdit.title,
      date: document.getElementById("edit_expense_date")?.value ?? data.expense.expenseToEdit.date,
      amount: document.getElementById("edit_expense_price")?.value ?? data.expense.expenseToEdit.amount,
      category_name: document.getElementById("edit_expense_category")?.value ?? data.expense.expenseToEdit.category_name,
      payment_mode_name: document.getElementById("edit_payment_mode_name")?.value ?? data.expense.expenseToEdit.payment_mode_name,
      description: document.getElementById("edit_expense_note")?.value?.trim() || null,
    });
    await editExpense({ transactionId: id, payload });
  });
}

export function createPayload() {
  const title = document.getElementById("expense_name")?.value?.trim();
  const amount = document.getElementById("expense_price")?.value;
  const date = document.getElementById("expense_date")?.value;
  const category_name = document.getElementById("expense_category")?.value;
  const payment_mode_name = document.getElementById("expense_payment_mode")?.value;
  const description = document.getElementById("expense_note")?.value?.trim() || null;
  return buildTransactionCreatePayload({
    title,
    date,
    amount,
    category_name,
    payment_mode_name,
    description,
  });
}

export async function addExpense(payload) {
  data.expense.loading = true;
  data.expense.error = null;
  try {
    const response = await fetch(`${API_URL}/api/v1/transaction/create`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
      body: JSON.stringify(payload),
    });

    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(result.detail || result.message || `Failed to add expense: ${response.status}`);
    }

    if (expenseForm) expenseForm.reset();
    hideExpenseOverlay();
    data.expense.error = null;
    await Promise.all([expenseOverview(), getExpense({ page: data.expense.page.current_page })]);
  } catch (error) {
    console.error("Error adding expense:", error);
    data.expense.error = error.message || "Failed to add expense.";
    hideExpenseOverlay();
  } finally {
    data.expense.loading = false;
  }
}

async function expenseOverview() {
  try {
    const response = await fetch(`${API_URL}/api/v1/transaction/expense_overview`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });
    if (!response.ok) throw new Error("Failed to fetch expense overview");
    const result = await response.json();
    Object.assign(data.expense.overview, result);
    syncRivets();
  } catch (error) {
    console.error("Error fetching expense overview:", error);
    data.expense.error = error.message;
    syncRivets();
  }
}

async function getExpense({
  page = 1,
  limit = 20,
  id = null,
  exact_amount = null,
  greater_amount = null,
  lower_amount = null,
  date = null,
  search = null,
} = {}) {
  data.expense.loading = true;
  data.expense.error = null;
  const params = new URLSearchParams();
  params.append("direction", "EXPENSE");
  params.append("page", String(page));
  params.append("limit", String(limit));
  if (id != null) params.append("id", String(id));
  if (exact_amount != null) params.append("exact_amount", String(exact_amount));
  if (greater_amount != null) params.append("greater_amount", String(greater_amount));
  if (lower_amount != null) params.append("lower_amount", String(lower_amount));
  if (date) params.append("date", date);
  const searchVal = search !== undefined ? search : data.expense.search.input;
  if (searchVal) params.append("search", searchVal);

  try {
    const response = await fetch(`${API_URL}/api/v1/transaction/?${params.toString()}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });
    if (!response.ok) throw new Error("Failed to fetch expense list");
    const result = await response.json().catch(() => ({}));
    const list = Array.isArray(result?.transactions) ? result.transactions : [];
    replaceList(data.expense.list, list);
    data.expense.page.total_pages = result.total_pages ?? 1;
    data.expense.page.current_page = result.current_page ?? 1;
    data.expense.page.total_transactions = result.total_transactions ?? 0;
    syncExpenseListEmpty();
    paintExpenseTable();
    syncRivets();
  } catch (error) {
    console.error("Error fetching expense list:", error);
    data.expense.error = error.message;
    syncRivets();
  } finally {
    data.expense.loading = false;
    syncRivets();
  }
}

async function editExpense({ transactionId, payload } = {}) {
  if (!transactionId) return;
  data.expense.loading = true;
  data.expense.error = null;
  try {
    const response = await fetch(`${API_URL}/api/v1/transaction/update/${transactionId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
      body: JSON.stringify(payload),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.detail || result.message || "Failed to update expense");

    toggleElement(document.getElementById("expense-edit-screen"));
    await Promise.all([expenseOverview(), getExpense({ page: data.expense.page.current_page })]);
  } catch (error) {
    console.error("Error editing expense:", error);
    data.expense.error = error.message;
  } finally {
    data.expense.loading = false;
  }
}

async function deleteExpense({ transactionId } = {}) {
  if (!transactionId) return;
  data.expense.loading = true;
  data.expense.error = null;
  try {
    const response = await fetch(`${API_URL}/api/v1/transaction/delete/${transactionId}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });
    if (!response.ok) throw new Error("Failed to delete expense");

    const kept = data.expense.list.filter((t) => Number(t.id) !== Number(transactionId));
    replaceList(data.expense.list, kept);
    syncExpenseListEmpty();
    paintExpenseTable();
    await expenseOverview();
    toggleElement(document.getElementById("expense-edit-screen"));
  } catch (error) {
    console.error("Error deleting expense:", error);
    data.expense.error = error.message;
  } finally {
    data.expense.loading = false;
  }
}

function openExpenseEditor({ transactionId = null, expenseList = [] } = {}) {
  if (transactionId == null || !expenseList?.length) return;
  const tx = expenseList.find((t) => Number(t.id) === Number(transactionId));
  if (!tx) return;
  const dateStr = tx.date ? new Date(tx.date).toISOString().slice(0, 10) : "";
  data.expense.expenseToEdit = {
    id: tx.id,
    title: tx.title,
    date: dateStr,
    amount: tx.amount,
    transaction_type_name: "Nill",
    category_name: tx.category_name || "",
    payment_mode_name: tx.payment_mode_name || "",
    account_name: null,
    description: tx.description || "",
  };
}

if (searchBtn) {
  searchBtn.addEventListener("click", () => {
    getExpense({ page: 1, ...getExpenseSearchState() });
  });
}

if (nextPageBtn) {
  nextPageBtn.addEventListener("click", () => {
    const next = Math.min(data.expense.page.current_page + 1, data.expense.page.total_pages);
    getExpense({ page: next, ...getExpenseSearchState() });
  });
}

if (prevPageBtn) {
  prevPageBtn.addEventListener("click", () => {
    const prev = Math.max(1, data.expense.page.current_page - 1);
    getExpense({ page: prev, ...getExpenseSearchState() });
  });
}

if (filterToggleBtn?.length && filterOption) {
  filterToggleBtn.forEach((btn) => {
    btn.addEventListener("click", () => filterOption.classList.toggle("hidden"));
  });
}

function showAddExpenseOverlay() {
  const overlay = document.getElementById("overlay-screen");
  if (overlay && document.getElementById("expense-addition-form")) {
    overlay.classList.remove("hidden");
    overlay.style.display = "flex";
  }
}

function hideExpenseOverlay() {
  const overlay = document.getElementById("overlay-screen");
  if (overlay) {
    overlay.classList.add("hidden");
    overlay.style.display = "none";
  }
}

onPageReady(async () => {
  await Promise.all([
    expenseOverview(),
    getExpense({ page: data.expense.page.current_page, ...getExpenseSearchState() }),
  ]);
  syncRivets();

  if (searchInputEl) {
    searchInputEl.addEventListener("keydown", (event) => {
      if (event.key !== "Enter") return;
      event.preventDefault();
      getExpense({ page: 1, ...getExpenseSearchState() });
    });
  }

  [lowerPriceEl, greaterPriceEl, exactPriceEl].forEach((input) => {
    if (!input) return;
    input.addEventListener("keydown", (event) => {
      if (event.key !== "Enter") return;
      event.preventDefault();
      getExpense({ page: 1, ...getExpenseSearchState() });
    });
  });

  document.querySelectorAll("button.open-add-expense-form").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      showAddExpenseOverlay();
    });
  });
});

body.addEventListener("click", (e) => {
  const target = e.target;
  if (target.closest && target.closest(".open-add-expense-form")) {
    showAddExpenseOverlay();
  }
  const openExpenseBtn = target.closest?.(".open-expense-editor");
  if (openExpenseBtn) {
    const id = openExpenseBtn.getAttribute("data-transaction-id");
    openExpenseEditor({ transactionId: id, expenseList: data.expense.list });
    toggleElement(document.getElementById("expense-edit-screen"));
  }
  if (target.closest?.(".edit-screen-toggle")?.closest?.("#expense-edit-screen")) {
    toggleElement(document.getElementById("expense-edit-screen"));
  }
  if (target.closest && target.closest(".screen-toggle") && target.closest("#overlay-screen")) {
    hideExpenseOverlay();
  }
  const deleteExpenseBtn = target.closest?.(".delete-expense");
  if (deleteExpenseBtn) {
    const id = deleteExpenseBtn.getAttribute("data-transaction-id");
    deleteExpense({ transactionId: id });
  }
});

function toggleElement(element) {
  if (element) element.classList.toggle("hidden");
}
