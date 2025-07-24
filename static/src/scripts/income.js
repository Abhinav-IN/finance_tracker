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

function token() {
  const jwtToken = localStorage.getItem("jwtToken");
  if (!jwtToken) {
    console.error("No JWT token found. User is not logged in.");
    window.location.href = "/login.html";
    return;
  }
  return jwtToken;
}
