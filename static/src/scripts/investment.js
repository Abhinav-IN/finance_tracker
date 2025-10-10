import { data } from "../main";
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const investmentForm = document.getElementById("investment-addition-form");
if (investmentForm) {
  investmentForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    console.log("submit");
  });
}

async function addInvestment(payload) {
  console.log("Formatted data to send:", payload);

  try {
    const response = await fetch(`${API_URL}/api/v1/investment/create`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(
        `HTTP error! status: ${response.status}, message: ${errorText}`
      );
      throw new Error(
        `Failed to add investment: ${response.status} ${response.statusText}`
      );
    }

    const result = await response.json();
    console.log("investment added successfully:", result);

    alert("investment added successfully!");
  } catch (error) {
    console.error("Error adding investment:", error);
    alert(`Error adding investment: ${error.message}`);
  }
}

async function getInvestment({
  page = 1,
  limit = 20,
  transaction_id = null,
  name = null,
  exact_amount = null,
  greater_amount = null,
  lower_amount = null,
  date = null,
  search = null,
} = {}) {
  try {
    const queryParams = new URLSearchParams();

    if (page !== null && page !== undefined) {
      queryParams.append("page", page);
    }

    if (limit !== null && limit !== undefined) {
      queryParams.append("limit", limit);
    }

    if (name) {
      // For strings, check for truthiness (non-empty string, not null/undefined)
      queryParams.append("name", name);
    }
    if (transaction_id) {
      queryParams.append("transaction_id", transaction_id);
    }

    if (exact_amount !== null && exact_amount !== undefined) {
      queryParams.append("exact_amount", exact_amount);
    }

    if (greater_amount !== null && greater_amount !== undefined) {
      queryParams.append("greater_amount", greater_amount);
    }

    if (lower_amount !== null && lower_amount !== undefined) {
      queryParams.append("lower_amount", lower_amount);
    }

    if (date) {
      queryParams.append("date", date);
    }
    if (search) {
      queryParams.append("search", search);
    } else {
      queryParams.append("search", data.expense.search.input);
    }

    const queryString = queryParams.toString();

    const response = await fetch(
      `${API_URL}/api/v1/investment/${queryString}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token()}`,
        },
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      console.error(
        `HTTP error! status: ${response.status}, message: ${errorText}`
      );
      throw new Error(
        `Failed to fetch income: ${response.status} ${response.statusText}`
      );
    }
    const resolved = await response.json();
    console.log(resolved);
    data.investments.list = resolved.investments;
    data.investments.page.total_pages = result.total_pages;
    data.investments.page.current_page = result.current_page;
    data.investments.page.total_investments = result.total_investments;
  } catch (error) {
    console.log(error);
    alert("oops, error fetching the information about the investments");
  }
}

function openInvestmentEditor({
  investmentId = null,
  investmentList = [],
} = {}) {
  if (!investmentId || investmentId == null) {
    return alert("Income ID is invalid");
  }

  if (!investmentId || investmentId.length <= 0) {
    return alert("Income List To Filter From Is Empty Or Invalid");
  }

  data.investments.investmentToEdit = investmentList.filter(
    (investment) => Number(investment.investment_id) === Number(investmentId)
  )[0];
  console.log(data.investments.investmentToEdit);
}

function token() {
  const jwtToken = localStorage.getItem("jwtToken");
  if (!jwtToken) {
    console.error("No JWT token found. User is not logged in.");
    window.location.href = "/login.html";
    return;
  }
  return jwtToken;
}
function toggleElement(element) {
  element.classList.toggle("hidden");
}

const body = document.querySelector("body");

body.addEventListener("click", (e) => {
  e.preventDefault();
  const target = e.target;
  if (target.classList.contains("toggle-investment-editor")) {
    const investmentId = target.getAttribute("investments-id");
    openInvestmentEditor({
      investmentId: investmentId,
      investmentList: data.investments.list,
    });
    toggleElement(document.getElementById("investment-editor-info"));
  }

  if (target.classList.contains("add-investment-screen-toggle")) {
    toggleElement(document.getElementById("add-investment-screen"));
  }
  if (target.classList.contains("submit-invetment-form")) {
    const payload = createPayloadForAddingInvestment();
    addInvestment(payload);
  }
});

function createPayloadForAddingInvestment() {
  const payload = {
    investment_name: document.getElementById("investment_name").value,
    investment_type: document.getElementById("investment_type").value,
    investment_date: document.getElementById("investment_date").value,
    description: document.getElementById("investment_description").value,
    platform: document.getElementById("investment_platform").value,
    amount_invested: document.getElementById("investment_amount").value,
    withdrawl_amount: document.getElementById("investment_withdrawl_amount")
      .value,
    withdrawl_date: document.getElementById("investment_withdrawl_date").value,
    account_name: document.getElementById("investment_account_name").value,
    units: document.getElementById("investment_units").value,
    buy_price_per_unit: document.getElementById("investment_buy_price_per_unit")
      .value,
    current_price_per_unit: document.getElementById(
      "investment_current_unit_price"
    ).value,
    maturity_date: document.getElementById("investment_maturity_date").value,
  };
  console.log(payload);
  return payload;
}

window.document.onload = () => {
  getInvestment();
};
