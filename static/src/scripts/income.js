import { body, data } from "../main";
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const nextPageBtn = document.getElementById("next-page");
const prevPageBtn = document.getElementById("prev-page");
const searchBtn = document.getElementById("search-btn");
const filterToggleBtn = document.querySelectorAll(".filter-toggle");
const filterOption = document.getElementById("filter-options");

const incomeForm = document.getElementById("income-addition-form");
const editIncomeForm = document.getElementById("edit-income-form");

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

if (editIncomeForm) {
  editIncomeForm.addEventListener("submit", (e) => {
    e.preventDefault();
    editIncome({
      incomeId: data.income.incomeToEdit.income_id,
      payload: data.income.incomeToEdit,
    });
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

async function editIncome({ incomeId = "", payload } = {}) {
  try {
    const response = await fetch(
      `${API_URL}/api/v1/transaction/income/update/${incomeId}`,
      {
        method: "PUT",
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
        `Failed to edit income: ${response.status} ${response.statusText}`
      );
    }

    const result = await response.json();
    console.log("income edited successfully:", result);
  } catch (error) {
    console.log(error);
    alert(`Error editing income: ${error.message}`);
  }
}
async function deleteIncome({ incomeId = "" } = {}) {
  try {
    const response = await fetch(
      `${API_URL}/api/v1/transaction/income/delete/${incomeId}`,
      {
        method: "DELETE",
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
        `Failed to edit income: ${response.status} ${response.statusText}`
      );
    }

    const result = await response.json();
    console.log("income deleted successfully:", result);
    data.income.list = data.income.list.filter(
      (income) => income.income_id !== incomeId
    );
  } catch (error) {
    console.log(error);
    alert(`Error editing income: ${error.message}`);
  } finally {
    toggleElement(document.getElementById("income-edit-screen"));
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
    queryParams.append("search", data.income.search.input);
  }

  const queryString = queryParams.toString();
  console.log(queryParams);

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
    data.income.list = result.incomes;
    data.income.page.total_pages = result.total_pages;
    data.income.page.current_page = result.current_page;
    data.income.page.total_incomes = result.total_income;
  } catch (error) {
    console.error("Error fetching income overview:", error);
    // alert(`Error fetching income overview: ${error.message}`);
  }
}

function nextPage() {
  let nextPage = Number(data.income.page.current_page) + 1;

  if (nextPage > data.income.page.total_pages) {
    nextPage = data.income.page.total_pages;
  }

  getIncome({
    page: nextPage,

    greater_amount: data.income.search.greater_price,
    lower_amount: data.income.search.lower_price,
    exact_amount: data.income.search.exact_price,
  });
}

function prevPage() {
  let prevPage = Number(data.income.page.current_page) - 1;

  if (prevPage < 1) {
    prevPage = 1;
  }
  getIncome({
    page: prevPage,
    greater_amount: data.income.search.greater_price,
    lower_amount: data.income.search.lower_price,
    exact_amount: data.income.search.exact_price,
  });
}

function openIncomeEditor({ incomeId = null, incomeList = [] } = {}) {
  if (!incomeId || incomeId == null) {
    return alert("Income ID is invalid");
  }

  if (!incomeList || incomeList.length <= 0) {
    return alert("Income List To Filter From Is Empty Or Invalid");
  }

  data.income.incomeToEdit = incomeList.filter(
    (income) => Number(income.income_id) === Number(incomeId)
  )[0];
  console.log(data.income.incomeToEdit);
}

if (searchBtn) {
  searchBtn.addEventListener("click", (e) => {
    getIncome({
      page: 1,
      search: data.income.search.input,
      greater_amount: data.income.search.greater_price,
      lower_amount: data.income.search.lower_price,
      exact_amount: data.income.search.exact_price,
    });
  });
} else {
  console.log("SEARCH BUTTON NOT FOUND ON THIS PAGE");
}

if (nextPageBtn) {
  nextPageBtn.addEventListener("click", (e) => {
    nextPage();
  });
} else {
  console.log("NEXT PAGE BUTTON NOT FOUND ON THIS PAGE");
}

if (prevPageBtn) {
  prevPageBtn.addEventListener("click", (e) => {
    prevPage();
  });
} else {
  console.log("PREV PAGE BUTTON NOT FOUND ON THIS PAGE");
}

if (filterToggleBtn) {
  filterToggleBtn.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      filterOption.classList.toggle("hidden");
    });
  });
} else {
  console.log("FILTER OPTIONS ARE NOT FOUND ON THIS PAGE");
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

document.addEventListener("DOMContentLoaded", (e) => {
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
    const incomeId = target.getAttribute("income-id");
    openIncomeEditor({
      incomeId: incomeId,
      incomeList: data.income.list,
    });
    toggleElement(document.getElementById("income-edit-screen"));
  }

  if (target.classList.contains("edit-screen-toggle")) {
    toggleElement(document.getElementById("income-edit-screen"));
  }
  if (target.classList.contains("delete-income")) {
    const incomeId = target.getAttribute("income-id");
    deleteIncome({ incomeId: incomeId });
  }
});

function toggleElement(element) {
  element.classList.toggle("hidden");
}
