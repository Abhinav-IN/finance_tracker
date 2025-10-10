// main.js
import { data, token, body } from "../main.js";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const nextPageBtn = document.getElementById("next-page");
const prevPageBtn = document.getElementById("prev-page");
const searchBtn = document.getElementById("search-btn");
const filterToggleBtn = document.querySelectorAll(".filter-toggle");
const filterOption = document.getElementById("filter-options");

const expenseForm = document.getElementById("expense-addition-form");
const expenseEditingForm = document.getElementById("edit-expense-form");

if (expenseForm) {
  expenseForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = createPayload();
    await addExpense(payload);
  });
}

if (expenseEditingForm) {
  expenseEditingForm.addEventListener("submit", (e) => {
    e.preventDefault();
    editExpense({
      expenseId: data.expense.expenseToEdit.expense_id,
      payload: data.expense.expenseToEdit,
    });
  });
}

export function createPayload() {
  const expenseName = document.getElementById("expense_name").value;
  const expensePrice = document.getElementById("expense_price").value;
  const expenseDate = document.getElementById("expense_date").value;
  const expenseCategory = document.getElementById("expense_category").value;
  const expensePaymentMode = document.getElementById(
    "expense_payment_mode"
  ).value;
  const expenseNote = document.getElementById("expense_note").value;

  const payload = {
    expense_name: expenseName,
    expense_date: expenseDate ? new Date(expenseDate).toISOString() : null,
    price: parseFloat(expensePrice),
    expense_type_name: "Nill",
    category_name: expenseCategory,
    payment_mode_name: expensePaymentMode,
    additional_note: expenseNote,
  };
  return payload;
}

export async function addExpense(payload) {
  console.log("Formatted data to send:", payload);

  try {
    const response = await fetch(
      `${API_URL}/api/v1/transaction/expense/create`,
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
        `Failed to add expense: ${response.status} ${response.statusText}`
      );
    }

    const result = await response.json();
    console.log("Expense added successfully:", result);

    alert("Expense added successfully!");
  } catch (error) {
    console.error("Error adding expense:", error);
    alert(`Error adding expense: ${error.message}`);
  }
}

async function editExpense({ expenseId = "", payload = {} }) {
  try {
    const response = await fetch(
      `${API_URL}/api/v1/transaction/expense/update/${expenseId}`,
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
        `Failed to edit expense: ${response.status} ${response.statusText}`
      );
    }

    const result = await response.json();
    console.log("Expense edited successfully:", result);
    alert("Expense Edited Successfully.");
  } catch (error) {
    console.log(error);
    alert(`Error editing expense: ${error.message}`);
  }
}
async function deleteExpense({ expenseId = "" } = {}) {
  try {
    const response = await fetch(
      `${API_URL}/api/v1/transaction/expense/delete/${expenseId}`,
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
    console.log("expense deleted successfully:", result);
    data.expense.list = data.expense.list.filter(
      (expense) => expense.income_id !== expenseId
    );
  } catch (error) {
    console.log(error);
    alert(`Error editing expense: ${error.message}`);
  } finally {
    toggleElement(document.getElementById("expense-edit-screen"));
  }
}
async function expenseOverview() {
  try {
    const response = await fetch(
      `${API_URL}/api/v1/transaction/expense/overview`,
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
        `Failed to fetch expense: ${response.status} ${response.statusText}`
      );
    }

    const result = await response.json();
    console.log("expense fetched successfully:", result);
    data.expense.overview = result;
  } catch (error) {
    console.error("Error fetching expense overview:", error);
    alert(`Error fetching expense overview: ${error.message}`);
  }
}

async function getExpense({
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
    queryParams.append("search", data.expense.search.input);
  }

  const queryString = queryParams.toString();
  console.log(queryParams);

  try {
    const response = await fetch(
      `${API_URL}/api/v1/transaction/expense/?${queryString}`,
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
        `Failed to fetch expense: ${response.status} ${response.statusText}`
      );
    }

    const result = await response.json();
    data.expense.list = result.expenses;
    data.expense.page.total_pages = result.total_pages;
    data.expense.page.current_page = result.current_page;
    data.expense.page.total_expenses = result.total_expense;
  } catch (error) {
    console.error("Error fetching expense overview:", error);
    alert("oops, error fetching the information about the expense");
  }
}

getExpense({
  page: data.expense.page.current_page,
  search: data.expense.search.input,
  greater_amount: data.expense.search.greater_price,
  lower_amount: data.expense.search.lower_price,
  exact_amount: data.expense.search.exact_price,
});

function nextPage() {
  let nextPage = Number(data.expense.page.current_page) + 1;

  if (nextPage > data.expense.page.total_pages) {
    nextPage = data.expense.page.total_pages;
  }

  getExpense({
    page: nextPage,
    greater_amount: data.expense.search.greater_price,
    lower_amount: data.expense.search.lower_price,
    exact_amount: data.expense.search.exact_price,
  });
}

function prevPage() {
  let prevPage = Number(data.expense.page.current_page) - 1;

  if (prevPage < 1) {
    prevPage = 1;
  }
  getExpense({
    page: prevPage,
    greater_amount: data.expense.search.greater_price,
    lower_amount: data.expense.search.lower_price,
    exact_amount: data.expense.search.exact_price,
  });
}

function openExpenseEditor({ expenseId = null, expenseList = [] } = {}) {
  if (!expenseId || expenseId == null) {
    return alert("Income ID is invalid");
  }

  if (!expenseList || expenseList.length <= 0) {
    return alert("Income List To Filter From Is Empty Or Invalid");
  }

  data.expense.expenseToEdit = expenseList.filter(
    (expense) => Number(expense.expense_id) === Number(expenseId)
  )[0];
}

if (searchBtn) {
  searchBtn.addEventListener("click", (e) => {
    getExpense({
      page: 1,
      search: data.expense.search.input,
      greater_amount: data.expense.search.greater_price,
      lower_amount: data.expense.search.lower_price,
      exact_amount: data.expense.search.exact_price,
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

document.addEventListener("DOMContentLoaded", (e) => {
  expenseOverview();
});

body.addEventListener("click", (e) => {
  const target = e.target;

  if (target.classList.contains("open-expense-editor")) {
    const expenseId = target.getAttribute("expense-id");
    console.log(expenseId);
    openExpenseEditor({
      expenseId: expenseId,
      expenseList: data.expense.list,
    });
    toggleElement(document.getElementById("expense-edit-screen"));
  }

  if (target.classList.contains("edit-screen-toggle")) {
    toggleElement(document.getElementById("expense-edit-screen"));
  }
  if (target.classList.contains("edit-screen-toggle")) {
    const expenseId = target.getAttribute("expense-id");
    deleteExpense({ expenseId: expenseId });
  }
});

function toggleElement(element) {
  element.classList.toggle("hidden");
}
