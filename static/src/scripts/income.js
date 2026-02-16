import { body, data, token } from "../main.js";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const nextPageBtn = document.getElementById("next-page");
const prevPageBtn = document.getElementById("prev-page");
const searchBtn = document.getElementById("search-btn");
const filterToggleBtn = document.querySelectorAll(".filter-toggle");
const filterOption = document.getElementById("filter-options");

const incomeForm = document.getElementById("income-addition-form");
const editIncomeForm = document.getElementById("edit-income-form");

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
    toggleElement(document.getElementById("overlay-screen"));
    await Promise.all([incomeOverview(), getIncome({ page: data.income.page.current_page })]);
  } catch (error) {
    console.error("Error adding income:", error);
    data.income.error = error.message || "Failed to add income.";
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
    data.income.overview = result;
  } catch (error) {
    console.error("Error fetching income overview:", error);
    data.income.error = error.message;
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
    const result = await response.json();
    data.income.list = result.transactions || [];
    data.income.page.total_pages = result.total_pages ?? 1;
    data.income.page.current_page = result.current_page ?? 1;
    data.income.page.total_transactions = result.total_transactions ?? 0;
  } catch (error) {
    console.error("Error fetching income list:", error);
    data.income.error = error.message;
  } finally {
    data.income.loading = false;
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

    data.income.list = data.income.list.filter((t) => Number(t.id) !== Number(transactionId));
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
    getIncome({
      page: 1,
      search: data.income.search.input,
      greater_amount: data.income.search.greater_price,
      lower_amount: data.income.search.lower_price,
      exact_amount: data.income.search.exact_price,
    });
  });
}

if (nextPageBtn) {
  nextPageBtn.addEventListener("click", () => {
    const next = Math.min(data.income.page.current_page + 1, data.income.page.total_pages);
    getIncome({
      page: next,
      greater_amount: data.income.search.greater_price,
      lower_amount: data.income.search.lower_price,
      exact_amount: data.income.search.exact_price,
    });
  });
}

if (prevPageBtn) {
  prevPageBtn.addEventListener("click", () => {
    const prev = Math.max(1, data.income.page.current_page - 1);
    getIncome({
      page: prev,
      greater_amount: data.income.search.greater_price,
      lower_amount: data.income.search.lower_price,
      exact_amount: data.income.search.exact_price,
    });
  });
}

if (filterToggleBtn?.length && filterOption) {
  filterToggleBtn.forEach((btn) => {
    btn.addEventListener("click", () => filterOption.classList.toggle("hidden"));
  });
}

document.addEventListener("DOMContentLoaded", () => {
  incomeOverview();
  getIncome({
    page: data.income.page.current_page,
    search: data.income.search.input,
    greater_amount: data.income.search.greater_price,
    lower_amount: data.income.search.lower_price,
    exact_amount: data.income.search.exact_price,
  });
});

body.addEventListener("click", (e) => {
  const target = e.target;
  if (target.classList.contains("open-income-editor")) {
    const id = target.getAttribute("data-transaction-id");
    openIncomeEditor({ transactionId: id, incomeList: data.income.list });
    toggleElement(document.getElementById("income-edit-screen"));
  }
  if (target.classList.contains("edit-screen-toggle")) {
    toggleElement(document.getElementById("income-edit-screen"));
  }
  if (target.classList.contains("delete-income")) {
    const id = target.getAttribute("data-transaction-id");
    deleteIncome({ transactionId: id });
  }
});

function toggleElement(element) {
  if (element) element.classList.toggle("hidden");
}
