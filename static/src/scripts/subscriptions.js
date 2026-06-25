import { body, data, token, syncRivets, onPageReady, replaceList } from "../main.js";
import { renderSubscriptionRows } from "./lib/table-render.js";



const API_URL = "http://api.fi-track.manavkashyap.com";

const nextPageBtn = document.getElementById("next-page");
const prevPageBtn = document.getElementById("prev-page");
const searchBtn = document.getElementById("search-btn");
const filterToggleBtn = document.querySelectorAll(".filter-toggle");
const filterOption = document.getElementById("filter-options");
const searchInputEl = document.getElementById("search-input");
const lowerPriceEl = document.getElementById("lower-price");
const greaterPriceEl = document.getElementById("greater-price");
const exactPriceEl = document.getElementById("exact-price");

const subscriptionForm = document.getElementById("subscription-addition-form");
const editSubscriptionForm = document.getElementById("subscription-edit-form");
const listTableBody = document.getElementById("subscription-list-body");

function paintSubscriptionTable() {
  renderSubscriptionRows(listTableBody, data.subscription.list);
}

function syncSubscriptionListEmpty() {
  data.subscription.listEmpty = data.subscription.list.length === 0;
}

function parseFilterNumber(value) {
  if (value === null || value === undefined || value === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function normalizeBillingPeriod(value) {
  const normalized = String(value || "").trim().toUpperCase();
  const allowed = new Set(["YEARLY", "HALF_YEARLY", "QUATERLY", "WEEKLY", "MONTHLY", "ONE_TIME"]);
  return allowed.has(normalized) ? normalized : "MONTHLY";
}

function normalizeSubscriptionForUi(sub = {}) {
  return {
    ...sub,
    subscription_id: sub.id,
    subscription_name: sub.name || "",
    billing_cycle: sub.billing_period || "MONTHLY",
    category_name: sub.category_name || "",
    payment_mode_name: sub.payment_mode_name || "",
    account_name: sub.account_name || "",
    subscription_date: sub.start_date || null,
  };
}

function getSubscriptionSearchState() {
  const input = typeof data.subscription.search.input === "string" ? data.subscription.search.input.trim() : "";
  const lower = parseFilterNumber(data.subscription.search.lower_price);
  const greater = parseFilterNumber(data.subscription.search.greater_price);
  const exact = parseFilterNumber(data.subscription.search.exact_price);

  data.subscription.search.input = input;
  data.subscription.search.lower_price = lower;
  data.subscription.search.greater_price = greater;
  data.subscription.search.exact_price = exact;

  return { search: input, lower_amount: lower, greater_amount: greater, exact_amount: exact };
}

function buildSubscriptionPayload({
  subscription_name,
  amount,
  description,
  billing_cycle,
  category_name,
  payment_mode_name,
  start_date,
  end_date,
  is_active,
  last_paid_at,
}) {
  return {
    name: subscription_name || "",
    amount: parseFloat(amount) || 0,
    description: description || "",
    currency: "INR",
    billing_period: normalizeBillingPeriod(billing_cycle),
    category_name: category_name || "",
    transaction_type_name: "Nill",
    payment_mode_name: payment_mode_name || "",
    start_date: start_date ? new Date(start_date).toISOString() : new Date().toISOString(),
    end_date: end_date ? new Date(end_date).toISOString() : null,
    is_active: is_active === "true" || is_active === true,
    last_paid_at: last_paid_at ? new Date(last_paid_at).toISOString() : new Date().toISOString(),
  };
}

if (subscriptionForm) {
  subscriptionForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const subscription_name = document.getElementById("subscription_name").value.trim();
    const amount = document.getElementById("subscription_amount").value;
    const description = document.getElementById("subscription_description").value.trim() || "";
    const billing_cycle = document.getElementById("subscription_billing_cycle").value;
    const category_name = document.getElementById("subscription_category_name").value.trim();
    const payment_mode_name = document.getElementById("subscription_payment_mode_name").value;
    const start_date = document.getElementById("subscription_start_date").value;
    const end_date = document.getElementById("subscription_end_date").value;
    const is_active = document.getElementById("subscription_is_active").value;
    const last_paid_at = document.getElementById("subscription_last_paid_at").value;

    if (!subscription_name || !amount || parseFloat(amount) <= 0) {
      data.subscription.error = "Please enter a name and a valid amount.";
      return;
    }
    data.subscription.error = null;

    const payload = buildSubscriptionPayload({
      subscription_name,
      amount,
      description,
      billing_cycle,
      category_name,
      payment_mode_name,
      start_date: start_date || new Date().toISOString().slice(0, 10),
      end_date,
      is_active,
      last_paid_at: last_paid_at || new Date().toISOString().slice(0, 10),
    });

    await addSubscription(payload);
  });
}

if (editSubscriptionForm) {
  editSubscriptionForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = data.subscription.subscriptionToEdit.subscription_id;
    if (!id) return;
    const payload = buildSubscriptionPayload({
      subscription_name: document.getElementById("subscription_name_edit")?.value?.trim() ?? data.subscription.subscriptionToEdit.subscription_name,
      amount: document.getElementById("subscription_amount_edit")?.value ?? data.subscription.subscriptionToEdit.amount,
      description: document.getElementById("subscription_description_edit")?.value?.trim() || "",
      billing_cycle: document.getElementById("subscription_billing_cycle_edit")?.value ?? data.subscription.subscriptionToEdit.billing_cycle,
      category_name: document.getElementById("subscription_category_name_edit")?.value?.trim() ?? data.subscription.subscriptionToEdit.category_name,
      payment_mode_name: document.getElementById("subscription_payment_mode_name_edit")?.value ?? data.subscription.subscriptionToEdit.payment_mode_name,
      start_date: document.getElementById("subscription_start_date_edit")?.value ?? data.subscription.subscriptionToEdit.start_date,
      end_date: document.getElementById("subscription_end_date_edit")?.value ?? data.subscription.subscriptionToEdit.end_date,
      is_active: document.getElementById("subscription_is_active_edit")?.value ?? (data.subscription.subscriptionToEdit.is_active ? "true" : "false"),
      last_paid_at: document.getElementById("subscription_last_paid_at_edit")?.value ?? data.subscription.subscriptionToEdit.last_paid_at,
    });
    await editSubscription({ subscriptionId: id, payload });
  });
}

async function addSubscription(payload) {
  data.subscription.loading = true;
  data.subscription.error = null;
  try {
    const response = await fetch(`${API_URL}/api/v1/subscription/create`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
      body: JSON.stringify(payload),
    });

    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(result.detail || result.message || `Failed to add subscription: ${response.status}`);
    }

    if (subscriptionForm) subscriptionForm.reset();
    hideSubscriptionOverlay();
    data.subscription.error = null;
    await Promise.all([subscriptionOverview(), getSubscriptions({ page: data.subscription.page.current_page })]);
  } catch (error) {
    console.error("Error adding subscription:", error);
    data.subscription.error = error.message || "Failed to add subscription.";
    hideSubscriptionOverlay();
  } finally {
    data.subscription.loading = false;
  }
}

async function subscriptionOverview() {
  try {
    const response = await fetch(`${API_URL}/api/v1/subscription/overview`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });
    if (!response.ok) throw new Error("Failed to fetch subscription overview");
    const result = await response.json();
    data.subscription.overview.total_subscription_last_30_days = result.total_subscription_last_30_days ?? 0;
    data.subscription.overview.total_subscription_last_7_days = result.total_subscription_last_7_days ?? 0;
    data.subscription.overview.total_subscription_current_month = result.total_subscription_current_month ?? 0;
    data.subscription.overview.average_monthly_subscription = result.average_monthly_subscription ?? 0;
    data.subscription.overview.average_weekly_subscription = result.average_weekly_subscription ?? 0;
    syncRivets();
  } catch (error) {
    console.error("Error fetching subscription overview:", error);
    data.subscription.error = error.message;
  }
}

async function getSubscriptions({
  page = 1,
  limit = 20,
  subscription_id = null,
  exact_amount = null,
  greater_amount = null,
  lower_amount = null,
  search = null,
} = {}) {
  data.subscription.loading = true;
  data.subscription.error = null;
  const params = new URLSearchParams();
  params.append("page", String(page));
  params.append("limit", String(limit));
  if (subscription_id != null) params.append("id", String(subscription_id));
  if (exact_amount != null) params.append("exact_amount", String(exact_amount));
  if (greater_amount != null) params.append("greater_amount", String(greater_amount));
  if (lower_amount != null) params.append("lower_amount", String(lower_amount));
  const searchVal = search !== undefined ? search : data.subscription.search.input;
  if (searchVal) params.append("search", searchVal);

  try {
    const response = await fetch(`${API_URL}/api/v1/subscription/?${params.toString()}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });
    if (!response.ok) throw new Error("Failed to fetch subscription list");
    const result = await response.json().catch(() => ({}));
    const list = (Array.isArray(result?.subscriptions) ? result.subscriptions : []).map(normalizeSubscriptionForUi);
    replaceList(data.subscription.list, list);
    data.subscription.page.total_pages = result.total_pages ?? 1;
    data.subscription.page.current_page = result.current_page ?? 1;
    data.subscription.page.total_subscriptions = result.total_subscriptions ?? 0;
    syncSubscriptionListEmpty();
    paintSubscriptionTable();
    syncRivets();
  } catch (error) {
    console.error("Error fetching subscription list:", error);
    data.subscription.error = error.message;
    syncRivets();
  } finally {
    data.subscription.loading = false;
    syncRivets();
  }
}

async function editSubscription({ subscriptionId, payload } = {}) {
  if (!subscriptionId) return;
  data.subscription.loading = true;
  data.subscription.error = null;
  try {
    const response = await fetch(`${API_URL}/api/v1/subscription/update/${subscriptionId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
      body: JSON.stringify(payload),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.detail || result.message || "Failed to update subscription");

    hideSubscriptionEditOverlay();
    await Promise.all([subscriptionOverview(), getSubscriptions({ page: data.subscription.page.current_page })]);
  } catch (error) {
    console.error("Error editing subscription:", error);
    data.subscription.error = error.message;
  } finally {
    data.subscription.loading = false;
  }
}

async function deleteSubscription({ subscriptionId } = {}) {
  if (!subscriptionId) return;
  data.subscription.loading = true;
  data.subscription.error = null;
  try {
    const response = await fetch(`${API_URL}/api/v1/subscription/delete/${subscriptionId}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });
    if (!response.ok) throw new Error("Failed to delete subscription");

    const kept = data.subscription.list.filter((s) => Number(s.subscription_id) !== Number(subscriptionId));
    replaceList(data.subscription.list, kept);
    syncSubscriptionListEmpty();
    paintSubscriptionTable();
    await subscriptionOverview();
    hideSubscriptionEditOverlay();
  } catch (error) {
    console.error("Error deleting subscription:", error);
    data.subscription.error = error.message;
  } finally {
    data.subscription.loading = false;
  }
}

function openSubscriptionEditor({ subscriptionId = null, subscriptionList = [] } = {}) {
  if (subscriptionId == null || !subscriptionList?.length) return;

  const sub = subscriptionList.find((s) => Number(s.subscription_id ?? s.id) === Number(subscriptionId));
  if (!sub) return;

  const startDateStr  = sub.start_date   ? new Date(sub.start_date).toISOString().slice(0, 10)   : "";
  const endDateStr    = sub.end_date     ? new Date(sub.end_date).toISOString().slice(0, 10)     : "";
  const lastPaidStr   = sub.last_paid_at ? new Date(sub.last_paid_at).toISOString().slice(0, 10) : "";

  // Use Object.assign so Rivets binding stays alive
  Object.assign(data.subscription.subscriptionToEdit, {
    subscription_id:   sub.subscription_id ?? sub.id,
    subscription_name: sub.subscription_name || sub.name || "",
    amount:            sub.amount,
    description:       sub.description || "",
    billing_cycle:     sub.billing_cycle || sub.billing_period || "MONTHLY",
    category_name:     sub.category_name || "",
    payment_mode_name: sub.payment_mode_name || "",
    start_date:        startDateStr,
    end_date:          endDateStr,
    is_active:         sub.is_active ? "true" : "false",
    last_paid_at:      lastPaidStr,
  });

  // Manually set form field values since Rivets may not re-sync date/select inputs
  const set = (id, val) => { const el = document.getElementById(id); if (el) el.value = val ?? ""; };
  set("subscription_name_edit",         data.subscription.subscriptionToEdit.subscription_name);
  set("subscription_amount_edit",       data.subscription.subscriptionToEdit.amount);
  set("subscription_last_paid_at_edit", data.subscription.subscriptionToEdit.last_paid_at);
  set("subscription_category_name_edit",data.subscription.subscriptionToEdit.category_name);
  set("subscription_billing_cycle_edit",data.subscription.subscriptionToEdit.billing_cycle);
  set("subscription_start_date_edit",   data.subscription.subscriptionToEdit.start_date);
  set("subscription_end_date_edit",     data.subscription.subscriptionToEdit.end_date);
  set("subscription_is_active_edit",    data.subscription.subscriptionToEdit.is_active);
  set("subscription_payment_mode_name_edit", data.subscription.subscriptionToEdit.payment_mode_name);

  // Set delete button data attribute
  const deleteBtn = document.querySelector(".delete-subscription");
  if (deleteBtn) deleteBtn.setAttribute("data-subscription-id", data.subscription.subscriptionToEdit.subscription_id);
}

function showAddSubscriptionOverlay() {
  const overlay = document.getElementById("subscription-addition-screen");
  if (overlay && document.getElementById("subscription-addition-form")) {
    overlay.classList.remove("hidden");
    overlay.style.display = "flex";
  }
}

function hideSubscriptionOverlay() {
  const overlay = document.getElementById("subscription-addition-screen");
  if (overlay) {
    overlay.classList.add("hidden");
    overlay.style.display = "none";
  }
}

function hideSubscriptionEditOverlay() {
  const overlay = document.getElementById("subscription-edit-screen");
  if (overlay) {
    overlay.classList.add("hidden");
    overlay.style.display = "none";
  }
}

function toggleElement(element) {
  if (element) element.classList.toggle("hidden");
}

onPageReady(async () => {
  await Promise.all([
    subscriptionOverview(),
    getSubscriptions({ page: data.subscription.page.current_page, ...getSubscriptionSearchState() }),
  ]);
  syncRivets();

  if (searchInputEl) {
    searchInputEl.addEventListener("keydown", (event) => {
      if (event.key !== "Enter") return;
      event.preventDefault();
      getSubscriptions({ page: 1, ...getSubscriptionSearchState() });
    });
  }

  [lowerPriceEl, greaterPriceEl, exactPriceEl].forEach((input) => {
    if (!input) return;
    input.addEventListener("keydown", (event) => {
      if (event.key !== "Enter") return;
      event.preventDefault();
      getSubscriptions({ page: 1, ...getSubscriptionSearchState() });
    });
  });

  document.querySelectorAll("button.subscription-screen-toggle").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      showAddSubscriptionOverlay();
    });
  });
});

if (searchBtn) {
  searchBtn.addEventListener("click", () => {
    getSubscriptions({ page: 1, ...getSubscriptionSearchState() });
  });
}

if (nextPageBtn) {
  nextPageBtn.addEventListener("click", () => {
    const next = Math.min(data.subscription.page.current_page + 1, data.subscription.page.total_pages);
    getSubscriptions({ page: next, ...getSubscriptionSearchState() });
  });
}

if (prevPageBtn) {
  prevPageBtn.addEventListener("click", () => {
    const prev = Math.max(1, data.subscription.page.current_page - 1);
    getSubscriptions({ page: prev, ...getSubscriptionSearchState() });
  });
}

if (filterToggleBtn?.length && filterOption) {
  filterToggleBtn.forEach((btn) => {
    btn.addEventListener("click", () => filterOption.classList.toggle("hidden"));
  });
}

body.addEventListener("click", (e) => {
  const target = e.target;
  if (target.closest && target.closest(".subscription-screen-toggle")) {
    const insideModal = target.closest("#subscription-addition-screen");
    if (insideModal) {
      hideSubscriptionOverlay();
    } else {
      showAddSubscriptionOverlay();
    }
  }
  const editorBtn = target.closest(".open-subscription-editor");
  if (editorBtn) {
      const id = editorBtn.getAttribute("data-subscription-id");
      if (id) {
          openSubscriptionEditor({ subscriptionId: id, subscriptionList: data.subscription.list });
          const overlay = document.getElementById("subscription-edit-screen");
          if (overlay) {
              overlay.classList.remove("hidden");
              overlay.style.display = "flex";
          }
      }
  }
  if (target.classList.contains("subscription-edit-screen-toggle") && !target.closest(".open-subscription-editor")) {
    hideSubscriptionEditOverlay();
  }
  if (target.classList.contains("delete-subscription")) {
    const id = target.getAttribute("data-subscription-id");
    deleteSubscription({ subscriptionId: id });
  }
});
