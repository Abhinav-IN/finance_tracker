import { body, data } from "../main";
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const subscriptionForm = document.getElementById("subscription-addition-form");
const subscriptionEditForm = document.getElementById("subscription-edit-form");
const nextPageBtn = document.getElementById("next-page");
const prevPageBtn = document.getElementById("prev-page");
const searchBtn = document.getElementById("search-btn");
const filterToggleBtn = document.querySelectorAll(".filter-toggle");
const filterOption = document.getElementById("filter-options");
body.addEventListener("click", (e) => {
  const target = e.target;
  if (target.classList.contains("subscription-screen-toggle")) {
    document
      .getElementById("subscription-addition-screen")
      .classList.toggle("hidden");
  }

  if (target.classList.contains("subscription-edit-screen-toggle")) {
    const subscription_id = target.getAttribute("subscription-id");
    console.log(subscription_id);
    openSubscriptionEditor({
      subscriptionId: subscription_id,
      subscriptionList: data.subscription.list,
    });
    document
      .getElementById("subscription-edit-screen")
      .classList.toggle("hidden");
  }
});

subscriptionForm.addEventListener("submit", (e) => {
  e.preventDefault();
  console.log(createSubscriptionPayload());
});
subscriptionEditForm.addEventListener("submit", (e) => {
  e.preventDefault();
  console.log(data.subscription.subscriptionToEdit);
});

function openSubscriptionEditor({
  subscriptionId = null,
  subscriptionList = [],
} = {}) {
  console.log(subscriptionId);
  if (!subscriptionId || subscriptionId == null) {
    return alert("Subscription ID is invalid");
  }

  if (!subscriptionList || subscriptionList.length <= 0) {
    return alert("Subscription List To Filter From Is Empty Or Invalid");
  }

  data.subscription.subscriptionToEdit = subscriptionList.filter(
    (subscription) =>
      Number(subscription.subscription_id) === Number(subscriptionId)
  )[0];
}

getSubscriptions({
  page: data.subscription.page.current_page,
  search: data.subscription.search.input,
  greater_amount: data.subscription.search.greater_price,
  lower_amount: data.subscription.search.lower_price,
  exact_amount: data.subscription.search.exact_price,
});

function nextPage() {
  let nextPage = Number(data.subscription.page.current_page) + 1;

  if (nextPage > data.subscription.page.total_pages) {
    nextPage = data.subscription.page.total_pages;
  }

  getSubscriptions({
    page: nextPage,
    greater_amount: data.subscription.search.greater_price,
    lower_amount: data.subscription.search.lower_price,
    exact_amount: data.subscription.search.exact_price,
  });
}

function prevPage() {
  let prevPage = Number(data.subscription.page.current_page) - 1;

  if (prevPage < 1) {
    prevPage = 1;
  }
  getSubscriptions({
    page: prevPage,
    greater_amount: data.subscription.search.greater_price,
    lower_amount: data.subscription.search.lower_price,
    exact_amount: data.subscription.search.exact_price,
  });
}

if (searchBtn) {
  searchBtn.addEventListener("click", (e) => {
    getSubscriptions({
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
    data.subscription.categories = result;
  } catch (error) {
    console.log(error);
  }
}

async function editsubscription({ subscriptionId = "", payload = {} }) {
  try {
    const response = await fetch(
      `${API_URL}/api/v1/transaction/subscription/update/${subscriptionId}`,
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
        `Failed to edit subscription: ${response.status} ${response.statusText}`
      );
    }

    const result = await response.json();
    console.log("subscription edited successfully:", result);
    alert("subscription Edited Successfully.");
  } catch (error) {
    console.log(error);
    alert(`Error editing subscription: ${error.message}`);
  }
}
async function deletesubscription({ subscriptionId = "" } = {}) {
  try {
    const response = await fetch(
      `${API_URL}/api/v1/transaction/subscription/delete/${subscriptionId}`,
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
    console.log("subscription deleted successfully:", result);
    data.subscription.list = data.subscription.list.filter(
      (subscription) => subscription.income_id !== subscriptionId
    );
  } catch (error) {
    console.log(error);
    alert(`Error editing subscription: ${error.message}`);
  } finally {
    toggleElement(document.getElementById("subscription-edit-screen"));
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

function createSubscriptionPayload() {
  const payload = {
    subscription_name: document.getElementById("subscription_name").value,
    amount: document.getElementById("subscription_amount").value,
    description: document.getElementById("subscription_description").value,
    currency: "INR",
    account_name: document.getElementById("subscription_account_name").value,
    billing_cycle: document.getElementById("subscription_billing_cycle").value,
    category_name: document.getElementById("subscription_category_name").value,
    subscription_type_name: "recurring",
    payment_mode_name: document.getElementById("subscription_payment_mode_name")
      .value,
    start_date: document.getElementById("subscription_start_date").value,
    end_date: document.getElementById("subscription_end_date").value,
    is_active:
      document.getElementById("subscription_is_active").value === "true"
        ? true
        : false,
    last_paid_at: document.getElementById("subscription_last_paid_at").value,
  };

  return payload;
}
