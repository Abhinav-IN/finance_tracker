import { body, data } from "../main";
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
getSubscriptions();
async function getSubscriptions({
  page = null,
  subscription_id = null,
  name = null,
  exact_amount = null,
  greater_amount = null,
  lower_amount = null,
  start_date = null,
  end_date = null,
  billing_date = null,
  limit = 20,
  search = null,
  active_subscriptions = null,
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

  if (subscription_id !== null && subscription_id !== undefined) {
    queryParams.append("subscription_id", subscription_id);
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
  if (search) {
    queryParams.append("search", search);
  } else {
    queryParams.append("search", data.subscription.search.input);
  }

  //   queryParams.append("active_subscriptions", active_subscriptions);

  try {
    const queryString = queryParams.toString();
    console.log(queryParams);
    const response = await fetch(
      `${API_URL}/api/v1/subscription/?${queryString}`,
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
    }
    const result = await response.json();
    console.log("Category List:", result);
    data.expense.categories = result;
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
