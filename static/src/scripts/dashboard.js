const API_URL = "http://api.fi-track.manavkashyap.com";
import { data, token, onPageReady } from "../main.js";
import Chart from "chart.js/auto";

// ─── State ────────────────────────────────────────────────────────────────────
let activePeriod = "30";
let cashflowChart = null;
let allocationChart = null;
let averagesChart = null;
let subscriptionChart = null;
let investmentChart = null;

// Raw fetched data cached at module level
const cache = {
  overview: null,
  expenseOverview: null,
  incomeOverview: null,
  subscriptionOverview: null,
  investmentOverview: null,
  expenseRecords: [],   // [{date, total_transaction}]
  incomeRecords: [],    // [{date, total_transaction}]
  budgets: [],
  recentTransactions: [],
};

// ─── Helpers ─────────────────────────────────────────────────────────────────
function fmt(amount) {
  if (amount == null || isNaN(amount)) return "₹0";
  const n = Math.round(Number(amount));
  if (n >= 10_00_000) return `₹${(n / 10_00_000).toFixed(1)}L`;
  if (n >= 1_000) return `₹${(n / 1_000).toFixed(1)}k`;
  return `₹${n.toLocaleString("en-IN")}`;
}

function fmtFull(amount) {
  if (amount == null) return "₹0";
  return `₹${Number(amount).toLocaleString("en-IN")}`;
}

function fmtDate(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  return `${d.getDate()}/${d.getMonth() + 1}`;
}

function fmtDateFull(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

function isDark() {
  return document.documentElement.classList.contains("dark");
}

function textColor() {
  return isDark() ? "rgba(255,255,255,0.6)" : "rgba(0,0,0,0.55)";
}

function gridColor() {
  return isDark() ? "rgba(255,255,255,0.07)" : "rgba(0,0,0,0.07)";
}

function destroyChart(ref) {
  if (ref) { try { ref.destroy(); } catch (_) {} }
  return null;
}

// ─── Fetch helpers ────────────────────────────────────────────────────────────
async function apiFetch(path) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { Authorization: `Bearer ${token()}` },
  });
  if (!res.ok) throw new Error(`${path} → ${res.status}`);
  return res.json();
}

// ─── Fetch all data in parallel ───────────────────────────────────────────────
async function fetchAllData() {
  const results = await Promise.allSettled([
    apiFetch("/api/v1/dashboard/overview"),
    apiFetch("/api/v1/transaction/expense_overview"),
    apiFetch("/api/v1/transaction/income_overview"),
    apiFetch("/api/v1/subscription/overview"),
    apiFetch("/api/v1/investment/investment_overview"),
    apiFetch("/api/v1/dashboard/transaction_record/EXPENSE"),
    apiFetch("/api/v1/dashboard/transaction_record/INCOME"),
    apiFetch("/api/v1/budget/"),
    apiFetch("/api/v1/transaction/?limit=8&page=1"),
  ]);

  const [
    overview, expenseOverview, incomeOverview,
    subscriptionOverview, investmentOverview,
    expenseRecords, incomeRecords,
    budgets, recentTx,
  ] = results.map((r) => (r.status === "fulfilled" ? r.value : null));

  cache.overview             = overview;
  cache.expenseOverview      = expenseOverview;
  cache.incomeOverview       = incomeOverview;
  cache.subscriptionOverview = subscriptionOverview;
  cache.investmentOverview   = investmentOverview;
  cache.expenseRecords       = Array.isArray(expenseRecords) ? expenseRecords : [];
  cache.incomeRecords        = Array.isArray(incomeRecords)  ? incomeRecords  : [];
  cache.budgets              = Array.isArray(budgets) ? budgets : [];
  cache.recentTransactions   = recentTx?.transactions ?? [];

  // Also store in rivets data for bindings used elsewhere
  if (overview) data.overview = { ...data.overview, ...overview };
}

// ─── KPI Cards ────────────────────────────────────────────────────────────────
function getPeriodValues() {
  const exp = cache.expenseOverview;
  const inc = cache.incomeOverview;
  if (!exp || !inc) return { income: 0, expense: 0, label: "30-day" };

  switch (activePeriod) {
    case "7":
      return {
        income:  inc.total_income_last_7_days,
        expense: exp.total_expense_last_7_days,
        label:   "7-day",
      };
    case "month":
      return {
        income:  inc.total_income_current_month,
        expense: exp.total_expense_current_month,
        label:   "month-to-date",
      };
    default:
      return {
        income:  inc.total_income_last_30_days,
        expense: exp.total_expense_last_30_days,
        label:   "30-day",
      };
  }
}

function renderKPIs() {
  const { income, expense, label } = getPeriodValues();
  const net = income - expense;

  const netEl = document.getElementById("kpi-net");
  if (netEl) {
    netEl.textContent = fmt(net);
    netEl.className = `font-bold text-2xl mt-1 ${net >= 0 ? "text-green-500" : "text-red-500"}`;
  }
  setEl("kpi-net-label", `Income − Expense (${label})`);
  setEl("kpi-income", fmt(income));
  setEl("kpi-income-sub", label);
  setEl("kpi-expense", fmt(expense));
  setEl("kpi-expense-sub", label);

  const sub = cache.subscriptionOverview;
  setEl("kpi-subscription", fmt(sub?.total_subscription_last_30_days ?? cache.overview?.total_subscription));

  const inv = cache.investmentOverview;
  setEl("kpi-investment", fmt(inv?.total_investment_last_30_days ?? cache.overview?.total_investment));
}

function setEl(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text ?? "—";
}

// ─── Chart 1: Cash Flow (Income vs Expense over 30 days) ─────────────────────
function renderCashflowChart() {
  const el = document.getElementById("cashflow-chart");
  if (!el) return;

  cashflowChart = destroyChart(cashflowChart);

  // Build a unified date axis from both datasets
  const allDates = [...new Set([
    ...cache.expenseRecords.map((r) => r.date),
    ...cache.incomeRecords.map((r) => r.date),
  ])].sort();

  const expMap = Object.fromEntries(cache.expenseRecords.map((r) => [r.date, r.total_transaction]));
  const incMap = Object.fromEntries(cache.incomeRecords.map((r) => [r.date, r.total_transaction]));

  const labels   = allDates.map(fmtDate);
  const expData  = allDates.map((d) => expMap[d] ?? 0);
  const incData  = allDates.map((d) => incMap[d] ?? 0);

  cashflowChart = new Chart(el, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Income",
          data: incData,
          borderColor: "#3b82f6",
          backgroundColor: "rgba(59,130,246,0.08)",
          tension: 0.4,
          fill: true,
          pointRadius: 2,
          pointHoverRadius: 5,
          borderWidth: 2,
        },
        {
          label: "Expense",
          data: expData,
          borderColor: "#f87171",
          backgroundColor: "rgba(248,113,113,0.08)",
          tension: 0.4,
          fill: true,
          pointRadius: 2,
          pointHoverRadius: 5,
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: ${fmtFull(ctx.raw)}`,
          },
        },
      },
      scales: {
        x: {
          ticks: { color: textColor(), maxTicksLimit: 10, font: { size: 10 } },
          grid: { color: gridColor() },
        },
        y: {
          ticks: {
            color: textColor(),
            font: { size: 10 },
            callback: (v) => fmt(v),
          },
          grid: { color: gridColor() },
        },
      },
    },
  });
}

// ─── Chart 2: Allocation Donut ────────────────────────────────────────────────
function renderAllocationDonut() {
  const el = document.getElementById("allocation-donut");
  if (!el) return;

  allocationChart = destroyChart(allocationChart);

  const exp = cache.expenseOverview;
  const sub = cache.subscriptionOverview;
  const inv = cache.investmentOverview;

  const expVal = Number(exp?.total_expense_last_30_days ?? 0);
  const subVal = Number(sub?.total_subscription_last_30_days ?? 0);
  const invVal = Number(inv?.total_investment_last_30_days ?? 0);
  const incVal = Number(cache.incomeOverview?.total_income_last_30_days ?? 0);

  // Savings = income - expense - subscription - investment (floor at 0)
  const savingsVal = Math.max(0, incVal - expVal - subVal - invVal);

  const labels = ["Expense", "Subscriptions", "Investments", "Savings"];
  const values = [expVal, subVal, invVal, savingsVal];
  const colors = ["#f87171", "#a78bfa", "#34d399", "#60a5fa"];

  // Legend
  const legendEl = document.getElementById("allocation-legend");
  if (legendEl) {
    legendEl.innerHTML = labels.map((l, i) => `
      <span class="flex items-center gap-1">
        <span class="w-2 h-2 rounded-full flex-shrink-0" style="background:${colors[i]}"></span>
        ${l}
      </span>
    `).join("");
  }

  allocationChart = new Chart(el, {
    type: "doughnut",
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: colors,
        borderWidth: 0,
        hoverOffset: 6,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      cutout: "68%",
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${fmtFull(ctx.raw)}`,
          },
        },
      },
    },
  });
}

// ─── Chart 3: Daily Averages Bar ─────────────────────────────────────────────
function renderAveragesChart() {
  const el = document.getElementById("averages-bar");
  if (!el) return;

  averagesChart = destroyChart(averagesChart);

  const inc = cache.incomeOverview;
  const exp = cache.expenseOverview;

  const labels = ["Avg Daily Income\n(Monthly)", "Avg Daily Expense\n(Monthly)", "Avg Daily Income\n(Weekly)", "Avg Daily Expense\n(Weekly)"];
  const values = [
    inc?.average_monthly_income  ?? 0,
    exp?.average_monthly_expense ?? 0,
    inc?.average_weekly_income   ?? 0,
    exp?.average_weekly_expense  ?? 0,
  ];
  const colors = ["#3b82f6", "#f87171", "#60a5fa", "#fca5a5"];

  averagesChart = new Chart(el, {
    type: "bar",
    data: {
      labels: ["Monthly Income", "Monthly Expense", "Weekly Income", "Weekly Expense"],
      datasets: [{
        data: values,
        backgroundColor: colors,
        borderRadius: 6,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: { label: (ctx) => ` ${fmtFull(ctx.raw)} / day` },
        },
      },
      scales: {
        x: {
          ticks: { color: textColor(), font: { size: 10 } },
          grid: { display: false },
        },
        y: {
          ticks: { color: textColor(), font: { size: 10 }, callback: (v) => fmt(v) },
          grid: { color: gridColor() },
        },
      },
    },
  });
}

// ─── Chart 4: Subscription Spend Bar ─────────────────────────────────────────
function renderSubscriptionChart() {
  const el = document.getElementById("subscription-bar");
  if (!el) return;

  subscriptionChart = destroyChart(subscriptionChart);

  const sub = cache.subscriptionOverview;
  const values = [
    sub?.total_subscription_last_30_days  ?? 0,
    sub?.total_subscription_last_7_days   ?? 0,
    sub?.total_subscription_current_month ?? 0,
    sub?.average_monthly_subscription     ?? 0,
    sub?.average_weekly_subscription      ?? 0,
  ];

  subscriptionChart = new Chart(el, {
    type: "bar",
    data: {
      labels: ["30 Days", "7 Days", "This Month", "Avg Monthly", "Avg Weekly"],
      datasets: [{
        data: values,
        backgroundColor: [
          "rgba(167,139,250,0.85)",
          "rgba(167,139,250,0.65)",
          "rgba(139,92,246,0.85)",
          "rgba(109,40,217,0.5)",
          "rgba(109,40,217,0.35)",
        ],
        borderRadius: 6,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: { label: (ctx) => ` ${fmtFull(ctx.raw)}` },
        },
      },
      scales: {
        x: {
          ticks: { color: textColor(), font: { size: 10 } },
          grid: { display: false },
        },
        y: {
          ticks: { color: textColor(), font: { size: 10 }, callback: (v) => fmt(v) },
          grid: { color: gridColor() },
        },
      },
    },
  });
}

// ─── Chart 5: Investment Trend Bar ────────────────────────────────────────────
function renderInvestmentChart() {
  const el = document.getElementById("investment-trend");
  if (!el) return;

  investmentChart = destroyChart(investmentChart);

  const inv = cache.investmentOverview;
  const values = [
    inv?.total_investment_last_30_days  ?? 0,
    inv?.total_investment_last_7_days   ?? 0,
    inv?.total_investment_current_month ?? 0,
    inv?.average_monthly_investment     ?? 0,
    inv?.average_weekly_investment      ?? 0,
  ];

  investmentChart = new Chart(el, {
    type: "bar",
    data: {
      labels: ["30 Days", "7 Days", "This Month", "Avg Monthly", "Avg Weekly"],
      datasets: [{
        data: values,
        backgroundColor: [
          "rgba(52,211,153,0.85)",
          "rgba(52,211,153,0.65)",
          "rgba(16,185,129,0.85)",
          "rgba(5,150,105,0.5)",
          "rgba(5,150,105,0.35)",
        ],
        borderRadius: 6,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: { label: (ctx) => ` ${fmtFull(ctx.raw)}` },
        },
      },
      scales: {
        x: {
          ticks: { color: textColor(), font: { size: 10 } },
          grid: { display: false },
        },
        y: {
          ticks: { color: textColor(), font: { size: 10 }, callback: (v) => fmt(v) },
          grid: { color: gridColor() },
        },
      },
    },
  });
}

// ─── Budget Health Bars ───────────────────────────────────────────────────────
async function renderBudgetHealth() {
  const container = document.getElementById("budget-health-list");
  if (!container) return;

  const budgets = cache.budgets;
  if (!budgets.length) {
    container.innerHTML = `<p class="text-xs text-gray-400">No budgets set up yet. <a href="../dashboard/budget/" class="text-blue-500 hover:underline">Add one →</a></p>`;
    return;
  }

  // Fetch status for each budget in parallel (cap at 5 to keep it quick)
  const slice = budgets.slice(0, 5);
  const statuses = await Promise.allSettled(
    slice.map((b) => apiFetch(`/api/v1/budget/budget-status/${b.id}`))
  );

  container.innerHTML = slice.map((b, i) => {
    const s = statuses[i].status === "fulfilled" ? statuses[i].value : null;
    const spent     = s?.spent    ?? 0;
    const budget    = s?.budget   ?? b.amount ?? 0;
    const remaining = s?.remaining ?? budget - spent;
    const pct       = budget > 0 ? Math.min(Math.round((spent / budget) * 100), 100) : 0;
    const over      = s?.status === "over";
    const barColor  = over ? "bg-red-500" : pct >= 80 ? "bg-yellow-400" : "bg-green-500";
    const badge     = over
      ? `<span class="text-red-500 font-semibold">Over</span>`
      : `<span class="text-green-600 dark:text-green-400 font-semibold">${fmtFull(remaining)} left</span>`;

    return `
      <div class="space-y-1">
        <div class="flex items-center justify-between text-xs font-medium">
          <span class="capitalize truncate max-w-[120px]">${b.category_name || "Uncategorized"}</span>
          <div class="flex items-center gap-2 text-gray-400">
            ${badge}
            <span>${fmtFull(spent)} / ${fmtFull(budget)}</span>
            <span class="font-bold ${over ? "text-red-500" : "text-gray-500"}">${pct}%</span>
          </div>
        </div>
        <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 overflow-hidden">
          <div class="h-1.5 rounded-full ${barColor} transition-all duration-700" style="width:${pct}%"></div>
        </div>
      </div>
    `;
  }).join("");
}

// ─── Recent Transactions Feed ─────────────────────────────────────────────────
function renderRecentTransactions() {
  const container = document.getElementById("recent-tx-list");
  if (!container) return;

  const txs = cache.recentTransactions;
  if (!txs.length) {
    container.innerHTML = `<li class="text-xs text-gray-400 py-2">No recent transactions.</li>`;
    return;
  }

  container.innerHTML = txs.map((tx) => {
    const isIncome = String(tx.direction).toUpperCase() === "INCOME";
    const amtColor  = isIncome ? "text-green-500" : "text-red-500";
    const amtPrefix = isIncome ? "+" : "−";
    const dateLabel = fmtDateFull(tx.date);
    const category  = tx.category_name || "—";

    return `
      <li class="flex items-center justify-between gap-3 py-2">
        <div class="flex items-center gap-3 min-w-0">
          <div class="w-7 h-7 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold
            ${isIncome ? "bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400" : "bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400"}">
            ${isIncome ? "↑" : "↓"}
          </div>
          <div class="min-w-0">
            <p class="text-xs font-semibold truncate capitalize">${tx.title || "—"}</p>
            <p class="text-xs text-gray-400 truncate">${category} · ${dateLabel}</p>
          </div>
        </div>
        <span class="text-xs font-bold ${amtColor} flex-shrink-0">${amtPrefix}${fmtFull(tx.amount)}</span>
      </li>
    `;
  }).join("");
}

// ─── Period Toggle ────────────────────────────────────────────────────────────
function setupPeriodToggle() {
  document.querySelectorAll(".period-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      activePeriod = btn.dataset.period;
      document.querySelectorAll(".period-btn").forEach((b) => {
        b.className = "period-btn px-3 py-1.5 hover:bg-gray-100 dark:hover:bg-gray-800";
      });
      btn.className = "period-btn px-3 py-1.5 bg-black text-white dark:bg-white dark:text-black";
      renderKPIs();
    });
  });
}

// ─── Redraw all charts (called on theme change) ───────────────────────────────
function redrawAllCharts() {
  renderCashflowChart();
  renderAllocationDonut();
  renderAveragesChart();
  renderSubscriptionChart();
  renderInvestmentChart();
}

// ─── Init ─────────────────────────────────────────────────────────────────────
async function init() {
  setupPeriodToggle();

  await fetchAllData();

  renderKPIs();
  renderCashflowChart();
  renderAllocationDonut();
  renderAveragesChart();
  renderSubscriptionChart();
  renderInvestmentChart();
  await renderBudgetHealth();
  renderRecentTransactions();

  // Re-render charts when dark mode toggles (MutationObserver on <html> class)
  const observer = new MutationObserver(() => redrawAllCharts());
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
}

onPageReady(init);