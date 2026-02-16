const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
import { data, token } from "../main";
import Chart from "chart.js/auto";
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
    console.log("Overview information fetched :", result);
    data.overview = result;
    console.log(data.overview);
  } catch (error) {
    console.log(error);
    alert("something went wrong");
  }
}

async function getExpeneOverview(params) {
  try {
    const response = await fetch(`${API_URL}/api/v1/dashboard/transaction_record/EXPENSE`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      return;
    }
    const result = await response.json();
    data.overview.expense = result || [];
    const el = document.getElementById("expense-chart-overview");
    if (el && data.overview.expense.length) {
      generateChart(data.overview.expense, el);
    }
  } catch (error) {
    console.error("Error fetching expense chart data:", error);
  }
}
async function getIncomeOverview(params) {
  try {
    const response = await fetch(`${API_URL}/api/v1/dashboard/transaction_record/INCOME`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      return;
    }
    const result = await response.json();
    data.overview.income = result || [];
    const el = document.getElementById("income-chart-overview");
    if (el && data.overview.income.length) {
      generateIncomeChart(data.overview.income, el);
    }
  } catch (error) {
    console.error("Error fetching income chart data:", error);
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
          data: data.map((row) => row.total_transaction),
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
          data: data.map((row) => row.total_transaction),
          borderColor: "#000000",
          backgroundColor: "#4444FF",
        },
      ],
    },
  });
}
