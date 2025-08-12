// main.js
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
import { data, token } from "../main";
import { createPayload, addExpense } from "./expenses";
import Chart from "chart.js/auto";

const expenseForm = document.getElementById("expense-addition-form");

if (expenseForm) {
  expenseForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = createPayload();
    await addExpense(payload);
  });
}

async function getOverview(params) {
  try {
    const response = await fetch(`${API_URL}/api/v1/dashboard/overview`, {
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
    console.log("Overviewinformation fetched :", result);
    data.overview = result;
    console.log(data.overview);
  } catch (error) {
    console.log(error);
    alert("something went wrong");
  }
}

async function getExpeneOverview(params) {
  try {
    const response = await fetch(`${API_URL}/api/v1/dashboard/expense_record`, {
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
    console.log("Expense Overview Fetched :", result);
    data.overview.expense = result;
    console.log(data.overview.expense);

    generateChart(
      data.overview.expense,
      document.getElementById("expense-chart-overview")
    );
  } catch (error) {
    console.log(error);
    alert("something went wrong while fetching expense overview for the chart");
  }
}
async function getIncomeOverview(params) {
  try {
    const response = await fetch(`${API_URL}/api/v1/dashboard/income_record`, {
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
        `Failed to fetch income : ${response.status} ${response.statusText}`
      );
    }
    const result = await response.json();
    console.log("income Overview Fetched :", result);
    data.overview.income = result;
    console.log(data.overview.income);

    generateIncomeChart(
      data.overview.income,
      document.getElementById("income-chart-overview")
    );
  } catch (error) {
    console.log(error);
    // alert("something went wrong while fetching income overview for the chart");
  }
}

getOverview();
getExpeneOverview();
getIncomeOverview();

function generateChart(data, element) {
  if (!element) {
    return console.log("INVALID ELEMENT PROVIDED");
  }

  return new Chart(element, {
    type: "bar",
    data: {
      labels: data.map((row) => row.date),
      datasets: [
        {
          label: "Expense Overview Past 30 Days",
          data: data.map((row) => row.total_expense),
          borderColor: "#000000",
          backgroundColor: "#FF2222",
        },
      ],
    },
  });
}

function generateIncomeChart(data, element) {
  if (!element) {
    return console.log("INVALID ELEMENT PROVIDED");
  }

  return new Chart(element, {
    type: "bar",
    data: {
      labels: data.map((row) => row.date),
      datasets: [
        {
          label: "Income Overview Past 30 Days",
          data: data.map((row) => row.total_income),
          borderColor: "#000000",
          backgroundColor: "#4444FF",
        },
      ],
    },
  });
}
