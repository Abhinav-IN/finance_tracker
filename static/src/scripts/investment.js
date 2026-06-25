import { body, data, token, syncRivets, onPageReady, replaceList } from "../main.js";
import { renderInvestmentRows } from "./lib/table-render.js";

API_URL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function formatApiErrorBody(result) {
  if (result == null || typeof result !== "object") return "";
  if (typeof result.detail === "string") return result.detail;
  if (Array.isArray(result.detail)) {
    return result.detail
      .map((d) => (typeof d === "object" && d?.msg ? d.msg : JSON.stringify(d)))
      .join("; ");
  }
  if (result.message) return String(result.message);
  try {
    return JSON.stringify(result);
  } catch {
    return "Unknown API error";
  }
}

async function readJsonBody(response, label) {
  const text = await response.text();
  if (!text) {
    if (!response.ok) {
      console.error(`[${label}] HTTP ${response.status} empty body`, response.url);
    }
    return {};
  }
  try {
    return JSON.parse(text);
  } catch (err) {
    console.error(`[${label}] invalid JSON HTTP ${response.status}`, text.slice(0, 600), err);
    throw new Error(`${label}: server returned non-JSON (HTTP ${response.status})`);
  }
}

function safeSyncRivets() {
  try {
    syncRivets();
  } catch (e) {
    console.warn("[investment] Rivets sync failed:", e);
  }
}

const nextPageBtn = document.getElementById("next-page");
const prevPageBtn = document.getElementById("prev-page");
const searchBtn = document.getElementById("search-btn");
const filterToggleBtn = document.querySelectorAll(".filter-toggle");
const filterOption = document.getElementById("filter-options");

const investmentForm = document.getElementById("investment-addition-form");
const editInvestmentForm = document.getElementById("edit-investment-form");
const searchInputEl = document.getElementById("search-input");
const lowerPriceEl = document.getElementById("lower-price");
const greaterPriceEl = document.getElementById("greater-price");
const exactPriceEl = document.getElementById("exact-price");
const statusE1 = document.getElementById("status");
const listTableBody = document.getElementById("investment-list-body");

function paintInvestmentTable() {
  renderInvestmentRows(listTableBody, data.investment.list);
}

function syncInvestmentListEmpty() {
  data.investment.listEmpty = data.investment.list.length === 0;
}

function parseFilterNumber(value) {
  if (value === null || value === undefined || value === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function getInvestmentSearchState() {
  const input = typeof data.investment.search.input === "string" ? data.investment.search.input.trim() : "";
  const lower = parseFilterNumber(data.investment.search.lower_price);
  const greater = parseFilterNumber(data.investment.search.greater_price);
  const exact = parseFilterNumber(data.investment.search.exact_price);
  const status =
    data.investment.search.status != null && data.investment.search.status !== ""
      ? String(data.investment.search.status).trim()
      : "";
  const date = typeof data.investment.search.date === "string" ? data.investment.search.date.trim() : "";

  data.investment.search.input = input;
  data.investment.search.lower_price = lower;
  data.investment.search.greater_price = greater;
  data.investment.search.exact_price = exact;
  data.investment.search.status = status;
  data.investment.search.date = date;

  return { search: input, lower_amount: lower, greater_amount: greater, exact_amount: exact, status: status, date: date };
}

function buildInvestmentCreatePayload({ name, investment_type, platform, amount, units, buy_price, date, description, status }) {
  const dateObj = date ? new Date(date) : new Date();
  return {
    name: name || "",
    date: dateObj.toISOString(),
    amount: parseFloat(amount) || 0.0,
    investment_type: investment_type,
    platform: platform,
    units: units || 0.0,
    buy_price: buy_price || 0.0,
    description: description || null,
    status: status || "ACTIVE",
  };
}

if (investmentForm) {
  investmentForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const name = document.getElementById("investment_name").value.trim();
    const amount = document.getElementById("investment_amount").value;
    const date = document.getElementById("investment_date").value;
    const investment_type = document.getElementById("investment_type").value;
    const platform = document.getElementById("investment_platform").value.trim();
    const units = document.getElementById("units").value;
    const buy_price = document.getElementById("buy_price").value;
    const description = document.getElementById("investment_note").value.trim() || null;
    const status = "ACTIVE";

    if (!name || !amount || parseFloat(amount) <= 0) {
      data.investment.error = "Please enter a name and a valid amount.";
      safeSyncRivets();
      return;
    }
    if (!investment_type || !platform){
      data.investment.error = "Please enter a investment type name and platoform name";
      safeSyncRivets();
      return;
    }
    const unitsNum = parseFloat(units);
    const buyPriceNum = parseFloat(buy_price);
    if (!Number.isFinite(unitsNum) || unitsNum <= 0 || !Number.isFinite(buyPriceNum) || buyPriceNum <= 0) {
      data.investment.error = "Please enter valid units and buy price";
      safeSyncRivets();
      return;
    }
    data.investment.error = null;

    const payload = buildInvestmentCreatePayload({
      name,
      investment_type,
      platform,
      amount,
      units,
      buy_price,
      date: date || new Date().toISOString().slice(0, 10),
      description,
      status,
    });

    await addInvestment(payload);
  });
}

if (editInvestmentForm) {
  editInvestmentForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = data.investment.investmentToEdit.id;
    if (!id) return;
    const payload = buildInvestmentCreatePayload({
      name: document.getElementById("edit_investment_name")?.value?.trim() ?? data.investment.investmentToEdit.name,
      investment_type: document.getElementById("edit_investment_type")?.value?.trim() ?? data.investment.investmentToEdit.type,
      platform: document.getElementById("edit_investment_platform")?.value?.trim() ?? data.investment.investmentToEdit.platform,
      amount: document.getElementById("edit_investment_amount")?.value ?? data.investment.investmentToEdit.amount,
      units: document.getElementById("edit_units")?.value ?? data.investment.investmentToEdit.units,
      buy_price: document.getElementById("edit_buy_price")?.value ?? data.investment.investmentToEdit.buy_price,
      date: document.getElementById("edit_investment_date")?.value ?? data.investment.investmentToEdit.date,
      description: document.getElementById("edit_investment_note")?.value?.trim() || null,
      status: document.getElementById("edit_investment_status")?.value ?? data.investment.investmentToEdit.status,
    });
    await editInvestment({ investmentId: id, payload });
  });
}

async function addInvestment(payload) {
  data.investment.loading = true;
  data.investment.error = null;
  try {
    const response = await fetch(`${API_URL}/api/v1/investment/create`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
      body: JSON.stringify(payload),
    });

    const result = await readJsonBody(response, "investment create");
    if (!response.ok) {
      const msg = formatApiErrorBody(result) || `HTTP ${response.status}`;
      console.error("[investment create] failed", response.status, msg, result);
      throw new Error(msg);
    }

    if (investmentForm) investmentForm.reset();
    hideOverlay();
    data.investment.error = null;
    await getInvestment({ page: 1, ...getInvestmentSearchState() });
    await investmentOverview();
    safeSyncRivets();
  } catch (error) {
    console.error("Error adding investment:", error);
    data.investment.error = error.message || "Failed to add investment.";
    hideOverlay();
  } finally {
    data.investment.loading = false;
  }
}

async function investmentOverview() {
  const url = `${API_URL}/api/v1/investment/investment_overview`;
  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });
    const result = await readJsonBody(response, "investment overview");
    if (!response.ok) {
      const msg = formatApiErrorBody(result) || `HTTP ${response.status}`;
      console.error("[investment overview] request failed", response.status, url, msg, result);
      data.investment.error = msg;
      safeSyncRivets();
      return;
    }
    if (result && typeof result === "object") {
      Object.assign(data.investment.overview, result);
    }
    safeSyncRivets();
  } catch (error) {
    const msg = error?.message || String(error);
    console.error("[investment overview] error", url, error);
    data.investment.error = msg;
    safeSyncRivets();
  }
}

async function getInvestment({
  page = 1,
  limit = 20,
  id = null,
  exact_amount = null,
  greater_amount = null,
  lower_amount = null,
  status = null,
  date = null,
  search = null,
} = {}) {
  data.investment.loading = true;
  const params = new URLSearchParams();
  params.append("page", String(page));
  params.append("limit", String(limit));
  if (id != null) params.append("id", String(id));
  if (exact_amount != null) params.append("amount", String(exact_amount));
  if (greater_amount != null) params.append("max_amount", String(greater_amount));
  if (lower_amount != null) params.append("min_amount", String(lower_amount));
  if (date) params.append("date", date);
  if (status && status.trim() !== "") {
    params.append("status", status.trim());
  }
  const searchVal = search !== undefined ? search : data.investment.search.input;
  if (searchVal) params.append("search", searchVal);

  const url = `${API_URL}/api/v1/investment/?${params.toString()}`;
  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });
    const result = await readJsonBody(response, "investment list");
    if (!response.ok) {
      const msg = formatApiErrorBody(result) || `HTTP ${response.status}`;
      console.error("[investment list] request failed", response.status, url, msg, result);
      data.investment.error = msg;
      safeSyncRivets();
      return;
    }
    const list = Array.isArray(result?.data) ? result.data : [];
    console.log("Investment item sample:", list[0]);
    if (!Array.isArray(result?.data)) {
      console.warn("[investment list] response.data is not an array; keys=", result && Object.keys(result));
    }
    const total = result.total ?? 0;
    const pageLimit = Math.max(1, Number(result.limit) || 20);
    const currentPage = result.current_page ?? result.page ?? 1;
    const totalPages = result.total_pages ?? Math.max(1, Math.ceil(total / pageLimit));
    replaceList(data.investment.list, list);
    data.investment.page.total_pages = totalPages;
    data.investment.page.current_page = currentPage;
    data.investment.page.total_investments = total;
    data.investment.error = null;
    syncInvestmentListEmpty();
    paintInvestmentTable();
    safeSyncRivets();
  } catch (error) {
    const msg = error?.message || String(error);
    console.error("[investment list] error", url, error);
    data.investment.error = msg;
    safeSyncRivets();
  } finally {
    data.investment.loading = false;
  }
}

async function editInvestment({ investmentId, payload } = {}) {
  if (!investmentId) return;
  data.investment.loading = true;
  data.investment.error = null;
  try {
    const response = await fetch(`${API_URL}/api/v1/investment/update/${investmentId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
      body: JSON.stringify(payload),
    });
    const result = await readJsonBody(response, "investment update");
    if (!response.ok) {
      const msg = formatApiErrorBody(result) || `HTTP ${response.status}`;
      console.error("[investment update] failed", response.status, msg, result);
      throw new Error(msg);
    }

    toggleElement(document.getElementById("investment-edit-screen"));
    await getInvestment({ page: data.investment.page.current_page, ...getInvestmentSearchState() });
    await investmentOverview();
  } catch (error) {
    console.error("Error editing investment:", error);
    data.investment.error = error.message;
  } finally {
    data.investment.loading = false;
  }
}

async function deleteInvestment({ investmentId } = {}) {
  if (!investmentId) return;
  data.investment.loading = true;
  data.investment.error = null;
  try {
    const response = await fetch(`${API_URL}/api/v1/investment/delete/${investmentId}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });
    if (!response.ok) throw new Error("Failed to delete investment");

    const kept = data.investment.list.filter((i) => Number(i.id) !== Number(investmentId));
    replaceList(data.investment.list, kept);
    syncInvestmentListEmpty();
    paintInvestmentTable();
    safeSyncRivets();
    await investmentOverview();
    toggleElement(document.getElementById("investment-edit-screen"));
  } catch (error) {
    console.error("Error deleting investment:", error);
    data.investment.error = error.message;
  } finally {
    data.investment.loading = false;
  }
}

async function updateInvestmentCurrentPrice() {
  const id = data.investment.investmentToEdit?.id;
  if (!id) return;

  const priceInput = document.getElementById("edit_current_price");
  const pricePerUnit = parseFloat(priceInput?.value ?? "");
  if (!Number.isFinite(pricePerUnit) || pricePerUnit <= 0) {
    data.investment.error = "Enter a valid current price per unit (greater than 0).";
    safeSyncRivets();
    return;
  }

  const units = parseFloat(String(data.investment.investmentToEdit.units ?? ""));
  const totalValue =
    Number.isFinite(units) && units > 0 ? Math.round(pricePerUnit * units * 100) / 100 : null;

  data.investment.loading = true;
  data.investment.error = null;
  try {
    const response = await fetch(`${API_URL}/api/v1/investment_prices/create`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
      body: JSON.stringify({
        investment_id: Number(id),
        price_per_unit: pricePerUnit,
        total_value: totalValue,
      }),
    });
    const result = await readJsonBody(response, "investment price create");
    if (!response.ok) {
      const msg = formatApiErrorBody(result) || `HTTP ${response.status}`;
      console.error("[investment price] failed", response.status, msg, result);
      throw new Error(msg);
    }

    data.investment.investmentToEdit.current_price = result.price_per_unit;
    data.investment.error = null;
    await getInvestment({ page: data.investment.page.current_page, ...getInvestmentSearchState() });
    await investmentOverview();
    safeSyncRivets();
  } catch (error) {
    console.error("Error updating investment price:", error);
    data.investment.error = error.message || "Failed to update price.";
    safeSyncRivets();
  } finally {
    data.investment.loading = false;
  }
}

function openInvestmentEditor({ investmentId = null, investmentList = [] } = {}) {
  if (investmentId == null || !investmentList?.length) {
    return;
  }
  const inv = investmentList.find((i) => Number(i.id) === Number(investmentId));
  if (!inv) return;
  const dateStr = inv.date ? new Date(inv.date).toISOString().slice(0, 10) : "";
  data.investment.investmentToEdit = {
    id: inv.id,
    name: inv.name,
    date: dateStr,
    amount: inv.amount,
    type: inv.investment_type ?? inv.type ?? "",
    platform: inv.platform || "Nill",
    units: inv.units,
    buy_price: inv.buy_price,
    current_price: inv.current_price ?? "",
    description: inv.description || "",
  };
}

if (searchBtn) {
  searchBtn.addEventListener("click", () => {
    getInvestment({ page: 1, ...getInvestmentSearchState() });
  });
}

if (nextPageBtn) {
  nextPageBtn.addEventListener("click", () => {
    const next = Math.min(data.investment.page.current_page + 1, data.investment.page.total_pages);
    getInvestment({ page: next, ...getInvestmentSearchState() });
  });
}

if (prevPageBtn) {
  prevPageBtn.addEventListener("click", () => {
    const prev = Math.max(1, data.investment.page.current_page - 1);
    getInvestment({ page: prev, ...getInvestmentSearchState() });
  });
}

if (filterToggleBtn?.length && filterOption) {
  filterToggleBtn.forEach((btn) => {
    btn.addEventListener("click", () => filterOption.classList.toggle("hidden"));
  });
}

function showAddInvestmentOverlay() {
  const overlay = document.getElementById("overlay-screen");
  if (overlay && document.getElementById("investment-addition-form")) {
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
    getInvestment({ page: data.investment.page.current_page, ...getInvestmentSearchState() }),
    investmentOverview(),
  ]);
  syncRivets();

  if (searchInputEl) {
    searchInputEl.addEventListener("keydown", (event) => {
      if (event.key !== "Enter") return;
      event.preventDefault();
      getInvestment({ page: 1, ...getInvestmentSearchState() });
    });
  }

  [lowerPriceEl, greaterPriceEl, exactPriceEl, statusE1].forEach((input) => {
    if (!input) return;
    input.addEventListener("keydown", (event) => {
      if (event.key !== "Enter") return;
      event.preventDefault();
      getInvestment({ page: 1, ...getInvestmentSearchState() });
    });
  });

  document.querySelectorAll("button.open-add-investment-form").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      showAddInvestmentOverlay();
    });
  });

  const updatePriceBtn = document.getElementById("update-price-btn");
  if (updatePriceBtn) {
    updatePriceBtn.addEventListener("click", () => {
      void updateInvestmentCurrentPrice();
    });
  }
});

body.addEventListener("click", (e) => {
  const target = e.target;
  if (target.closest && target.closest(".open-add-investment-form")) {
    showAddInvestmentOverlay();
  }
  const openEditorBtn = target.closest?.(".open-investment-editor");
  if (openEditorBtn) {
    const id = openEditorBtn.getAttribute("data-investment-id");
    openInvestmentEditor({ investmentId: id, investmentList: data.investment.list });
    toggleElement(document.getElementById("investment-edit-screen"));
  }
  if (target.closest?.(".edit-screen-toggle")?.closest?.("#investment-edit-screen")) {
    toggleElement(document.getElementById("investment-edit-screen"));
  }
  if (target.closest && target.closest(".screen-toggle") && target.closest("#overlay-screen")) {
    hideOverlay();
  }
  const deleteBtn = target.closest?.(".delete-investment");
  if (deleteBtn) {
    const id = deleteBtn.getAttribute("data-investment-id");
    deleteInvestment({ investmentId: id });
  }
});

function toggleElement(element) {
  if (element) element.classList.toggle("hidden");
}