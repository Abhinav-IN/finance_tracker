import { body, data, token, syncRivets, onPageReady, replaceList } from "../main.js";
import { renderTransactionRows } from "./lib/table-render.js";

const API_URL = "https://api-fi-track.manavkashyap.com";

const nextPageBtn = document.getElementById("next-page");
const prevPageBtn = document.getElementById("prev-page");
const searchBtn = document.getElementById("search-btn");
const filterToggleBtn = document.querySelectorAll(".filter-toggle");
const filterOption = document.getElementById("filter-options");

const incomeForm = document.getElementById("income-addition-form");
const editIncomeForm = document.getElementById("edit-income-form");
const searchInputEl = document.getElementById("search-input");
const lowerPriceEl = document.getElementById("lower-price");
const greaterPriceEl = document.getElementById("greater-price");
const exactPriceEl = document.getElementById("exact-price");
const listTableBody = document.getElementById("transaction-list-body");

function paintIncomeTable() {
  renderTransactionRows(listTableBody, data.income.list, { editorClass: "open-income-editor" });
}

function syncIncomeListEmpty() {
  data.income.listEmpty = data.income.list.length === 0;
}

function parseFilterNumber(value) {
  if (value === null || value === undefined || value === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function getIncomeSearchState() {
  const input = typeof data.income.search.input === "string" ? data.income.search.input.trim() : "";
  const lower = parseFilterNumber(data.income.search.lower_price);
  const greater = parseFilterNumber(data.income.search.greater_price);
  const exact = parseFilterNumber(data.income.search.exact_price);

  data.income.search.input = input;
  data.income.search.lower_price = lower;
  data.income.search.greater_price = greater;
  data.income.search.exact_price = exact;

  return { search: input, lower_amount: lower, greater_amount: greater, exact_amount: exact };
}

function buildTransactionCreatePayload({ title, date, amount, category_name, payment_mode_name, description }) {
  const dateObj = date ? new Date(date) : new Date();
  return {
    title: title || "",
    date: dateObj.toISOString(),
    amount: parseFloat(amount) || 0,
    direction: "INCOME",
    transaction_type_name: "Nill",
    category_name: category_name || "",
    payment_mode_name: payment_mode_name || "",
    account_name: null,
    description: description || null,
  };
}

if (incomeForm) {
  incomeForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const title = document.getElementById("income_name").value.trim();
    const amount = document.getElementById("income_amount").value;
    const date = document.getElementById("income_date").value;
    const category_name = document.getElementById("income_category").value;
    const payment_mode_name = document.getElementById("payment_mode_name").value;
    const description = document.getElementById("income_note").value.trim() || null;

    if (!title || !amount || parseFloat(amount) <= 0) {
      data.income.error = "Please enter a name and a valid amount.";
      return;
    }
    data.income.error = null;

    const payload = buildTransactionCreatePayload({
      title,
      date: date || new Date().toISOString().slice(0, 10),
      amount,
      category_name,
      payment_mode_name,
      description,
    });

    await addIncome(payload);
  });
}

if (editIncomeForm) {
  editIncomeForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = data.income.incomeToEdit.id;
    if (!id) return;
    const payload = buildTransactionCreatePayload({
      title: document.getElementById("edit_income_name")?.value?.trim() ?? data.income.incomeToEdit.title,
      date: document.getElementById("edit_recieved_date")?.value ?? data.income.incomeToEdit.date,
      amount: document.getElementById("edit_income_amount")?.value ?? data.income.incomeToEdit.amount,
      category_name: document.getElementById("edit_income_category")?.value ?? data.income.incomeToEdit.category_name,
      payment_mode_name: document.getElementById("edit_payment_mode_name")?.value ?? data.income.incomeToEdit.payment_mode_name,
      description: document.getElementById("edit_income_note")?.value?.trim() || null,
    });
    await editIncome({ transactionId: id, payload });
  });
}

async function addIncome(payload) {
  data.income.loading = true;
  data.income.error = null;
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
      throw new Error(result.detail || result.message || `Failed to add income: ${response.status}`);
    }

    if (incomeForm) incomeForm.reset();
    hideOverlay();
    data.income.error = null;
    await Promise.all([incomeOverview(), getIncome({ page: data.income.page.current_page })]);
  } catch (error) {
    console.error("Error adding income:", error);
    data.income.error = error.message || "Failed to add income.";
    hideOverlay();
  } finally {
    data.income.loading = false;
  }
}

async function incomeOverview() {
  try {
    const response = await fetch(`${API_URL}/api/v1/transaction/income_overview`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });
    if (!response.ok) throw new Error("Failed to fetch income overview");
    const result = await response.json();
    Object.assign(data.income.overview, result);
    syncRivets();
  } catch (error) {
    console.error("Error fetching income overview:", error);
    data.income.error = error.message;
    syncRivets();
  }
}

async function getIncome({
  page = 1,
  limit = 20,
  id = null,
  exact_amount = null,
  greater_amount = null,
  lower_amount = null,
  date = null,
  search = null,
} = {}) {
  data.income.loading = true;
  data.income.error = null;
  const params = new URLSearchParams();
  params.append("direction", "INCOME");
  params.append("page", String(page));
  params.append("limit", String(limit));
  if (id != null) params.append("id", String(id));
  if (exact_amount != null) params.append("exact_amount", String(exact_amount));
  if (greater_amount != null) params.append("greater_amount", String(greater_amount));
  if (lower_amount != null) params.append("lower_amount", String(lower_amount));
  if (date) params.append("date", date);
  const searchVal = search !== undefined ? search : data.income.search.input;
  if (searchVal) params.append("search", searchVal);

  try {
    const response = await fetch(`${API_URL}/api/v1/transaction/?${params.toString()}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });
    if (!response.ok) throw new Error("Failed to fetch income list");
    const result = await response.json().catch(() => ({}));
    const list = Array.isArray(result?.transactions) ? result.transactions : [];
    replaceList(data.income.list, list);
    data.income.page.total_pages = result.total_pages ?? 1;
    data.income.page.current_page = result.current_page ?? 1;
    data.income.page.total_transactions = result.total_transactions ?? 0;
    syncIncomeListEmpty();
    paintIncomeTable();
    syncRivets();
  } catch (error) {
    console.error("Error fetching income list:", error);
    data.income.error = error.message;
    syncRivets();
  } finally {
    data.income.loading = false;
    syncRivets();
  }
}

async function editIncome({ transactionId, payload } = {}) {
  if (!transactionId) return;
  data.income.loading = true;
  data.income.error = null;
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
    if (!response.ok) throw new Error(result.detail || result.message || "Failed to update income");

    toggleElement(document.getElementById("income-edit-screen"));
    await Promise.all([incomeOverview(), getIncome({ page: data.income.page.current_page })]);
  } catch (error) {
    console.error("Error editing income:", error);
    data.income.error = error.message;
  } finally {
    data.income.loading = false;
  }
}

async function deleteIncome({ transactionId } = {}) {
  if (!transactionId) return;
  data.income.loading = true;
  data.income.error = null;
  try {
    const response = await fetch(`${API_URL}/api/v1/transaction/delete/${transactionId}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });
    if (!response.ok) throw new Error("Failed to delete income");

    const kept = data.income.list.filter((t) => Number(t.id) !== Number(transactionId));
    replaceList(data.income.list, kept);
    syncIncomeListEmpty();
    paintIncomeTable();
    await incomeOverview();
    toggleElement(document.getElementById("income-edit-screen"));
  } catch (error) {
    console.error("Error deleting income:", error);
    data.income.error = error.message;
  } finally {
    data.income.loading = false;
  }
}

function openIncomeEditor({ transactionId = null, incomeList = [] } = {}) {
  if (transactionId == null || !incomeList?.length) {
    return;
  }
  const tx = incomeList.find((t) => Number(t.id) === Number(transactionId));
  if (!tx) return;
  const dateStr = tx.date ? new Date(tx.date).toISOString().slice(0, 10) : "";
  data.income.incomeToEdit = {
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
    getIncome({ page: 1, ...getIncomeSearchState() });
  });
}

if (nextPageBtn) {
  nextPageBtn.addEventListener("click", () => {
    const next = Math.min(data.income.page.current_page + 1, data.income.page.total_pages);
    getIncome({ page: next, ...getIncomeSearchState() });
  });
}

if (prevPageBtn) {
  prevPageBtn.addEventListener("click", () => {
    const prev = Math.max(1, data.income.page.current_page - 1);
    getIncome({ page: prev, ...getIncomeSearchState() });
  });
}

if (filterToggleBtn?.length && filterOption) {
  filterToggleBtn.forEach((btn) => {
    btn.addEventListener("click", () => filterOption.classList.toggle("hidden"));
  });
}

function showAddIncomeOverlay() {
  const overlay = document.getElementById("overlay-screen");
  if (overlay && document.getElementById("income-addition-form")) {
    overlay.classList.remove("hidden");
    overlay.style.display = "flex";
  }
}

function hideOverlay() {
  const overlay = document.getElementById("overlay-screen");
  if (overlay) {
    overlay.classList.add("hidden");
    overlay.style.display = "none";
  }
}

onPageReady(async () => {
  await Promise.all([
    incomeOverview(),
    getIncome({ page: data.income.page.current_page, ...getIncomeSearchState() }),
  ]);
  syncRivets();

  if (searchInputEl) {
    searchInputEl.addEventListener("keydown", (event) => {
      if (event.key !== "Enter") return;
      event.preventDefault();
      getIncome({ page: 1, ...getIncomeSearchState() });
    });
  }

  [lowerPriceEl, greaterPriceEl, exactPriceEl].forEach((input) => {
    if (!input) return;
    input.addEventListener("keydown", (event) => {
      if (event.key !== "Enter") return;
      event.preventDefault();
      getIncome({ page: 1, ...getIncomeSearchState() });
    });
  });

  document.querySelectorAll("button.open-add-income-form").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      showAddIncomeOverlay();
    });
  });
});

body.addEventListener("click", (e) => {
  const target = e.target;
  if (target.closest && target.closest(".open-add-income-form")) {
    showAddIncomeOverlay();
  }
  const openIncomeBtn = target.closest?.(".open-income-editor");
  if (openIncomeBtn) {
    const id = openIncomeBtn.getAttribute("data-transaction-id");
    openIncomeEditor({ transactionId: id, incomeList: data.income.list });
    toggleElement(document.getElementById("income-edit-screen"));
  }
  if (target.closest?.(".edit-screen-toggle")?.closest?.("#income-edit-screen")) {
    toggleElement(document.getElementById("income-edit-screen"));
  }
  if (target.closest && target.closest(".screen-toggle") && target.closest("#overlay-screen")) {
    hideOverlay();
  }
  const deleteIncomeBtn = target.closest?.(".delete-income");
  if (deleteIncomeBtn) {
    const id = deleteIncomeBtn.getAttribute("data-transaction-id");
    deleteIncome({ transactionId: id });
  }
});

function toggleElement(element) {
  if (element) element.classList.toggle("hidden");
}
