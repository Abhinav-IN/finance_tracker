const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
import "./style.css";
import rivets from "rivets";

// import Swup from 'swup';
// const swup = new Swup();

export const data = {
  user: {},
  income: {
    list: [],
    page: {
      total_pages: 1,
      current_page: 1,
      total_incomes: 0,
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
      income_id: "",
      income_name: "",
      recieved_date: "",
      amount: "",
      income_type_name: "",
      category_name: "",
      payment_mode_name: "",
      account_name: "",
      additional_note: "",
    },
  },
  expense: {
    categories: [],
    list: [],
    page: {
      total_pages: 1,
      current_page: 1,
      total_incomes: 0,
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
      expense_id: "",
      expense_name: "",
      expense_date: "",
      price: "",
      expense_type_name: "",
      category_name: "",
      payment_mode_name: "",
      account_name: "",
      additional_note: "",
    },
  },
  investments: {
    list: [
      {
        investment_name: "string",
        investment_type: "stock",
        investment_date: "2025-09-11T14:25:01.118Z",
        description: "string",
        platform: "string",
        amount_invested: 1,
        status: "active",
        withdrawl_amount: 0,
        withdrawl_date: "2025-09-11T14:25:01.118Z",
        account_name: "string",
        investment_id: 0,
        current_price_per_unit: 0,
        current_value: 0,
        last_synced_at: "2025-09-11T14:25:01.118Z",
        gain_or_loss: 0,
        units: 0,
        units_withdrawl: 0,
        buy_price_per_unit: 0,
        maturity_date: "2025-09-11T14:25:01.118Z",
        interest_rate: 0,
        compounding_frequency: "annually",
        account_linked: 0,
      },
    ],
    investmentToEdit: {
      investment_name: "string",
      investment_type: "stock",
      investment_date: "2025-09-11T14:25:01.118Z",
      description: "string",
      platform: "string",
      amount_invested: 1,
      status: "active",
      withdrawl_amount: 0,
      withdrawl_date: "2025-09-11T14:25:01.118Z",
      account_name: "string",
      investment_id: 0,
      current_price_per_unit: 0,
      current_value: 0,
      last_synced_at: "2025-09-11T14:25:01.118Z",
      gain_or_loss: 0,
      units: 0,
      units_withdrawl: 0,
      buy_price_per_unit: 0,
      maturity_date: "2025-09-11T14:25:01.118Z",
      interest_rate: 0,
      compounding_frequency: "annually",
      account_linked: 0,
    },
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
    },
  },
  subscription: {
    list: [
      {
        subscription_name: "string",
        amount: 1,
        description: "string",
        currency: "INR",
        account_name: "string",
        billing_cycle: "yearly",
        category_name: "string",
        expense_type_name: "string",
        payment_mode_name: "string",
        start_date: "2025-10-10T09:03:34.970Z",
        end_date: "2025-10-10T09:03:34.970Z",
        is_active: true,
        last_paid_at: "2025-10-10T09:03:34.970Z",
        subscription_id: 0,
        category_id: 0,
        expense_type_id: 0,
        payment_mode_id: 0,
        account_id: 0,
        next_billing_date: "2025-10-10T09:03:34.970Z",
      },
    ],
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
    },
  },
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
rivets.bind(body, {
  data: data,
});

rivets.formatters.date = function (value) {
  const date = new Date(value);

  return `${date.getDate()}-${date.getMonth()}-${date.getFullYear()}`;
};
rivets.formatters.time = function (value) {
  const date = new Date(value);

  return `${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`;
};

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

  if (target.classList.contains("screen-toggle")) {
    console.log("Toggling Pop Up Screen");
    toggleHiddenElement({ element: document.getElementById("overlay-screen") });
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
    console.log("User Info:", result);
    data.user = result;
  } catch (error) {
    console.log(error);
  }
}

export function token() {
  const jwtToken = localStorage.getItem("jwtToken");
  if (!jwtToken) {
    console.error("No JWT token found. User is not logged in.");
    window.location.href = "/login.html";
    return;
  }
  return jwtToken;
}

document.addEventListener("DOMContentLoaded", () => {
  const jwtToken = localStorage.getItem("jwtToken");
  getUserDetails();
  getCategoryList();
  if (jwtToken) {
    console.log("user token is present");
  } else {
    console.log("user token is not present, redirecting");
    window.location.href = "/";
  }
});

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
