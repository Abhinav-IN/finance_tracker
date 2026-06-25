function formatDate(value) {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "";
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function formatMoney(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "";
  const n = Number(value).toFixed(2);
  const [intPart, decPart] = n.split(".");
  const formatted = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return decPart ? `${formatted}.${decPart}` : formatted;
}

function clearRenderedRows(tbody) {
  tbody.querySelectorAll("tr[data-rendered-row]").forEach((row) => row.remove());
}

function setEmptyRowVisible(tbody, visible) {
  const emptyRow = tbody.querySelector("tr[data-empty-row]");
  if (!emptyRow) return;
  emptyRow.classList.toggle("hidden", !visible);
}

/** Render income/expense transaction rows into a tbody (keeps Rivets empty-state row). */
export function renderTransactionRows(tbody, items, { editorClass, idField = "id" }) {
  if (!tbody) return;
  clearRenderedRows(tbody);

  const list = Array.isArray(items) ? items : [];
  setEmptyRowVisible(tbody, list.length === 0);
  if (!list.length) return;

  const fragment = document.createDocumentFragment();
  for (const item of list) {
    const tr = document.createElement("tr");
    tr.setAttribute("data-rendered-row", "1");
    tr.className =
      "bg-white border-b dark:bg-gray-800 dark:border-gray-700 border-gray-200 even:bg-gray-200 dark:even:bg-gray-900 capitalize";
    const id = item[idField];
    tr.innerHTML = `
      <th scope="row" class="px-2 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white border-r border-black/20 dark:border-white/20">
        <button type="button"
          class="flex items-center justify-center gap-1 bg-gray-300 p-2 rounded-md dark:bg-gray-700 cursor-pointer ${editorClass}"
          data-transaction-id="${id}">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
          </svg>
          Open
        </button>
      </th>
      <td class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white border-r border-black/20 dark:border-white/20">${formatDate(item.date)}</td>
      <td class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white border-r border-black/20 dark:border-white/20">${item.title ?? ""}</td>
      <td class="px-6 py-4 border-r border-black/20 dark:border-white/20">${item.category_name ?? ""}</td>
      <td class="px-6 py-4 border-r border-black/20 dark:border-white/20">${item.payment_mode_name ?? ""}</td>
      <td class="px-6 py-4">${formatMoney(item.amount)}</td>
    `;
    fragment.appendChild(tr);
  }

  const emptyRow = tbody.querySelector("tr[data-empty-row]");
  if (emptyRow) {
    tbody.insertBefore(fragment, emptyRow);
  } else {
    tbody.appendChild(fragment);
  }
}

/** Render subscription rows. */
export function renderSubscriptionRows(tbody, items) {
  if (!tbody) return;
  clearRenderedRows(tbody);

  const list = Array.isArray(items) ? items : [];
  setEmptyRowVisible(tbody, list.length === 0);
  if (!list.length) return;

  const fragment = document.createDocumentFragment();
  for (const sub of list) {
    const id = sub.subscription_id ?? sub.id;
    const tr = document.createElement("tr");
    tr.setAttribute("data-rendered-row", "1");
    tr.className =
      "bg-white border-b dark:bg-gray-800 dark:border-gray-700 border-gray-200 even:bg-gray-200 dark:even:bg-gray-900 capitalize";
    tr.innerHTML = `
      <th scope="row" class="px-2 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white border-r border-black/20 dark:border-white/20">
        <button type="button"
          class="flex items-center justify-center gap-1 bg-gray-300 p-2 rounded-md dark:bg-gray-700 cursor-pointer open-subscription-editor"
          data-subscription-id="${id}">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
          </svg>
          Open
        </button>
      </th>
      <td class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white border-r border-black/20 dark:border-white/20">${formatDate(sub.start_date || sub.subscription_date)}</td>
      <td class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white border-r border-black/20 dark:border-white/20">${sub.subscription_name || sub.name || ""}</td>
      <td class="px-6 py-4 border-r border-black/20 dark:border-white/20">${sub.category_name ?? ""}</td>
      <td class="px-6 py-4 border-r border-black/20 dark:border-white/20">${sub.payment_mode_name ?? ""}</td>
      <td class="px-6 py-4">${formatMoney(sub.amount)}</td>
    `;
    fragment.appendChild(tr);
  }

  const emptyRow = tbody.querySelector("tr[data-empty-row]");
  if (emptyRow) tbody.insertBefore(fragment, emptyRow);
  else tbody.appendChild(fragment);
}

/** Render investment rows. */
export function renderInvestmentRows(tbody, items) {
  if (!tbody) return;
  clearRenderedRows(tbody);

  const list = Array.isArray(items) ? items : [];
  setEmptyRowVisible(tbody, list.length === 0);
  if (!list.length) return;

  const fragment = document.createDocumentFragment();
  for (const item of list) {
    const tr = document.createElement("tr");
    tr.setAttribute("data-rendered-row", "1");
    tr.className =
      "bg-white border-b dark:bg-gray-800 dark:border-gray-700 border-gray-200 even:bg-gray-200 dark:even:bg-gray-900 capitalize";
    tr.innerHTML = `
      <th scope="row" class="px-2 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white border-r border-black/20 dark:border-white/20">
        <button type="button"
          class="flex items-center justify-center gap-1 bg-gray-300 p-2 rounded-md dark:bg-gray-700 cursor-pointer open-investment-editor"
          data-investment-id="${item.id}">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
          </svg>
          Open
        </button>
      </th>
      <td class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white border-r border-black/20 dark:border-white/20">${formatDate(item.date || item.investment_date)}</td>
      <td class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white border-r border-black/20 dark:border-white/20">${item.name ?? ""}</td>
      <td class="px-6 py-4 border-r border-black/20 dark:border-white/20">${formatMoney(item.current_price)}</td>
      <td class="px-6 py-4 border-r border-black/20 dark:border-white/20">${formatMoney(item.current_value)}</td>
      <td class="px-6 py-4 border-r border-black/20 dark:border-white/20">${formatMoney(item.pnl)}</td>
      <td class="px-6 py-4">${item.status ?? ""}</td>
    `;
    fragment.appendChild(tr);
  }

  const emptyRow = tbody.querySelector("tr[data-empty-row]");
  if (emptyRow) tbody.insertBefore(fragment, emptyRow);
  else tbody.appendChild(fragment);
}
