import { data } from "../main";
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const incomeForm = document.getElementById("income-addition-form");
if (incomeForm) {
  incomeForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const incomeName = document.getElementById("income_name").value;
    const incomeAmount = document.getElementById("income_amount").value;
    const incomeDate = document.getElementById("income_date").value;
    const incomeCategory = document.getElementById("income_category").value;
    const incomeNote = document.getElementById("income_note").value;
    const payment_mode_name =
      document.getElementById("payment_mode_name").value;

    const payload = {
      income_name: incomeName,
      recieved_date: incomeDate ? new Date(incomeDate).toISOString() : null,
      amount: parseFloat(incomeAmount),
      category_name: incomeCategory,
      payment_mode_name: payment_mode_name,
      income_type_name: "Nill",
      additional_note: incomeNote,
    };

    await addIncome(payload);
  });
}

async function addIncome(payload) {
  console.log("Formatted data to send:", payload);

  try {
    const response = await fetch(
      `${API_URL}/api/v1/transaction/income/create`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token()}`,
        },
        body: JSON.stringify(payload),
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      console.error(
        `HTTP error! status: ${response.status}, message: ${errorText}`
      );
      throw new Error(
        `Failed to add income: ${response.status} ${response.statusText}`
      );
    }

    const result = await response.json();
    console.log("income added successfully:", result);

    alert("income added successfully!");
  } catch (error) {
    console.error("Error adding income:", error);
    alert(`Error adding income: ${error.message}`);
  }
}

async function incomeOverview() {
  try {
    const response = await fetch(
      `${API_URL}/api/v1/transaction/income/overview`,
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

    const result = await response.json();
    console.log("income fetched successfully:", result);
    data.income.overview = result;
  } catch (error) {
    console.error("Error fetching income overview:", error);
    alert(`Error fetching income overview: ${error.message}`);
  }
}

async function getIncome({
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
    // For numbers, explicitly check for null/undefined as 0 is a valid value
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
  }

  const queryString = queryParams.toString();

  try {
    const response = await fetch(
      `${API_URL}/api/v1/transaction/income/?${queryString}`,
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

    const result = await response.json();
    data.income.list = result;
    console.log(data.income.list);
  } catch (error) {
    console.error("Error fetching income overview:", error);
    alert(`Error fetching income overview: ${error.message}`);
  }
}

incomeOverview();

getIncome();

function token() {
  const jwtToken = localStorage.getItem("jwtToken");
  if (!jwtToken) {
    console.error("No JWT token found. User is not logged in.");
    window.location.href = "/login.html";
    return;
  }
  return jwtToken;
}
