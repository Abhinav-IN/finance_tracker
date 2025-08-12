// main.js
import { data, token, body } from "../main.js";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const expenseForm = document.getElementById("expense-addition-form");

body.addEventListener("click", (e) => {
  const target = e.target;

  if (target.classList.contains("expense-info")) {
    console.log(target.getAttribute("expense-id"));
  }
});

if (expenseForm) {
  expenseForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = createPayload();
    await addExpense(payload);
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

export async function getExpense(params) {
  try {
    const response = await fetch(`${API_URL}/api/v1/transaction/expense/`, {
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
      throw new Error(
        `Failed to fetch expense : ${response.status} ${response.statusText}`
      );
    }

    const result = await response.json();
    console.log("expense information fetched :", result);
    data.expense.list = result;
  } catch (error) {
    console.log(error);
  }
}

getExpense();
