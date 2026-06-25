API_URL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
import "./style.css";
import "./scripts/binding/formatter.js";
import rivets from "rivets";

// import Swup from 'swup';
// const swup = new Swup();

export const data = {
  user: {},
  income: {
    list: [],
    listEmpty: true,
    loading: false,
    error: null,
    page: {
      total_pages: 1,
      current_page: 1,
      total_transactions: 0,
    },
    search: {
      input: "",
      lower_price: null,
      greater_price: null,
      exact_price: null,
    },
    overview: {
      total_income_current_month: 0,
      total_income_last_30_days: 0,
      total_income_last_7_days: 0,
      average_monthly_income: 0,
      average_weekly_income: 0,
    },
    incomeToEdit: {
      id: null,
      title: "",
      date: "",
      amount: "",
      transaction_type_name: "Nill",
      category_name: "",
      payment_mode_name: "",
      account_name: null,
      description: "",
      status: "",
    },
  },
  expense: {
    categories: [],
    list: [],
    listEmpty: true,
    loading: false,
    error: null,
    page: {
      total_pages: 1,
      current_page: 1,
      total_transactions: 0,
    },
    search: {
      input: "",
      lower_price: null,
      greater_price: null,
      exact_price: null,
    },
    overview: {
      total_expense_current_month: 0,
      total_expense_last_30_days: 0,
      total_expense_last_7_days: 0,
      average_monthly_expense: 0,
      average_weekly_expense: 0,
    },
    expenseToEdit: {
      id: null,
      title: "",
      date: "",
      amount: "",
      transaction_type_name: "Nill",
      category_name: "",
      payment_mode_name: "",
      account_name: null,
      description: "",
    },
  },
  investment: {
  list: [],
  /** Rivets cannot bind to Array.length (non-configurable); use this for empty-state UI. */
  listEmpty: true,
  loading: false,
  error: null,

  page: {
    total_pages: 1,
    current_page: 1,
    total_investments: 0,
  },

  search: {
    input: "",
    lower_price: null,
    greater_price: null,
    exact_price: null,
    status: null,
    date: null,
  },

  overview: {
    total_investment_current_month: 0,
    total_investment_last_30_days: 0,
    total_investment_last_7_days: 0,
    average_monthly_investment: 0,
    average_weekly_investment: 0,
  },

  investmentToEdit: {
    id: null,
    name: "",
    date: "",
    amount: "",
    type: "",
    platform: "",
    units: "",
    buy_price: "",
    current_price: "",
    description: "",
  },
},
  subscription: {
    list: [],
    listEmpty: true,
    loading: false,
    error: null,
    overview: {
      total_subscription_last_30_days: 0,
      total_subscription_last_7_days: 0,
      total_subscription_current_month: 0,
      average_monthly_subscription: 0,
      average_weekly_subscription: 0,
    },
    subscriptionToEdit: {
      subscription_name: "",
      amount: "",
      description: "",
      currency: "INR",
      account_name: "",
      billing_cycle: "MONTHLY",
      category_name: "",
      payment_mode_name: "",
      start_date: "",
      end_date: "",
      is_active: true,
      last_paid_at: "",
      subscription_id: 0,
    },
    page: {
      total_pages: 1,
      current_page: 1,
      total_subscriptions: 0,
    },
    search: {
      input: "",
      lower_price: null,
      greater_price: null,
      exact_price: null,
    },
  },
  // ─── ADD THIS BLOCK inside the `data` object in main.js ──────────────────────
// Place it alongside the other sections (income, expense, subscription, etc.)

  budget: {
    list: [],
    loading: false,
    error: null,
    page: {
      total_pages: 1,
      current_page: 1,
      total_budgets: 0,
    },
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
  },
// ─────────────────────────────────────────────────────────────────────────────
  overview: {},
  password: {
    length: false,
    number: false,
    lowercase: false,
    uppercase: false,
    symbol: false,
    match: false,
  },
};

export const body = document.querySelector("body");

// // Delay Rivets binding until DOM is ready to avoid length property redefinition errors
// function initializeRivets() {
//   try {
//     if (body) {
//       rivets.bind(body, {
//         data: data,
//       });
//     }
//   } catch (error) {
//     console.error("Rivets binding error:", error);
//     // Retry after a short delay if initial binding fails
//     setTimeout(() => {
//       try {
//         if (body) {
//           rivets.bind(body, {
//             data: data,
//           });
//         }
//       } catch (retryError) {
//         console.error("Rivets binding retry failed:", retryError);
//       }
//     }, 100);
//   }
// }

let rivetsView = null;
const pageInits = [];

/** Replace array contents in-place so Rivets keeps observing the same reference. */
export function replaceList(arr, items) {
  if (!Array.isArray(arr)) return;
  const next = Array.isArray(items) ? items : [];
  arr.splice(0, arr.length, ...next);
}

/** Register page-specific data loading; runs after Rivets bind + auth. */
export function onPageReady(fn) {
  pageInits.push(fn);
}

/** Re-run Rivets bindings after mutating `data` (overview object, lists, etc.). */
export function syncRivets() {
  try {
    if (rivetsView && typeof rivetsView.sync === "function") {
      rivetsView.sync();
    }
  } catch (err) {
    console.warn("Rivets sync failed:", err);
  }
}

/** ES module scripts may load after DOMContentLoaded; this runs init reliably. */
export function runWhenDomReady(fn) {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", fn);
  } else {
    fn();
  }
}

function initializeRivets() {
  if (rivetsView) return;

  if (body) {
    try {
      rivetsView = rivets.bind(body, { data });
    } catch (err) {
      console.error("Rivets bind failed:", err);
    }
  }
}

async function bootApp() {
  initializeRivets();

  const onDashboard = window.location.pathname.includes("/dashboard");
  const jwtToken = localStorage.getItem("jwtToken");

  if (onDashboard && !jwtToken) {
    window.location.href = "/";
    return;
  }

  if (jwtToken) {
    await Promise.allSettled([getUserDetails(), getCategoryList()]);
  }

  for (const init of pageInits) {
    try {
      await init();
    } catch (err) {
      console.error("Page init failed:", err);
    }
  }

  syncRivets();
}

// Defer one tick so sibling <script type="module"> tags can call onPageReady first.
runWhenDomReady(() => {
  setTimeout(() => {
    bootApp().catch((err) => console.error("App boot failed:", err));
  }, 0);
});

body.addEventListener("click", (e) => {
  const target = e.target;

  if (target.classList.contains("user-panel-toggle")) {
    toggleUserPanel();
  }

  if (target.classList.contains("navigation-toggle")) {
    toggleNavigationPanel();
  }

  if (target.classList.contains("logout")) {
    logout();
  }

  if (target.closest && target.closest(".screen-toggle")) {
    const overlay = document.getElementById("overlay-screen");
    if (overlay) {
      if (target.closest("#overlay-screen")) {
        overlay.classList.add("hidden");
        overlay.style.display = "none";
      } else {
        overlay.classList.remove("hidden");
        overlay.style.display = "flex";
      }
    }
  }
});

function toggleUserPanel() {
  const userpanel = document.getElementById("user-panel");
  userpanel.classList.toggle("hidden");
}

function toggleNavigationPanel(element) {
  console.log("Toggle Navigation Panel");
  const panel = document.getElementById("navigation-panel");
  panel.classList.toggle("-translate-x-full");
}

function toggleHiddenElement({ element, elemnetsToHide } = {}) {
  if (elemnetsToHide) {
    elemnetsToHide.forEach((element) => {
      element.classList.add("hidden");
    });
  } else {
    console.log("Elements To Hide Is Not Present");
  }
  if (element) {
    element.classList.toggle("hidden");
  } else {
    console.log("Element To Toggle Is Not Present");
  }
}

function logout() {
  const jwtToken = localStorage.getItem("jwtToken");
  if (!jwtToken) {
    console.log("User is not logged in");
    return;
  }
  localStorage.removeItem("jwtToken");
  alert("User Has Been Logged Out");
  window.location.href = "/";
}

async function getUserDetails() {
  try {
    const response = await fetch(`${API_URL}/api/v1/user/profile`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(
        `HTTP error! status: ${response.status}, message: ${errorText}`
      );

      if (response.status === 401) {
        alert("User is not authenticated");
        window.location.href = "/";
        return;
      }
    }
    const result = await response.json();
    Object.assign(data.user, result);
    syncRivets();
  } catch (error) {
    console.log(error);
  }
}

export function token() {
  const jwtToken = localStorage.getItem("jwtToken");
  if (!jwtToken) {
    console.error("No JWT token found. User is not logged in.");
    window.location.href = "/";
    throw new Error("Not authenticated: no jwtToken in localStorage.");
  }
  return jwtToken;
}

async function getCategoryList(params) {
  try {
    const response = await fetch(`${API_URL}/api/v1/category/`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(
        `HTTP error! status: ${response.status}, message: ${errorText}`
      );
    }
    const result = await response.json();
    console.log("Category List:", result);
    data.expense.categories = result;
  } catch (error) {
    console.log(error);
  }
}
