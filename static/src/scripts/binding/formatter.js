import rivets from "rivets";

rivets.formatters.date = function (value) {
  const inputDate = new Date(value);

  const year = inputDate.getFullYear();
  const month = String(inputDate.getMonth() + 1).padStart(2, "0");
  const day = String(inputDate.getDate()).padStart(2, "0");
  const formattedDate = `${year}-${month}-${day}`;
  return formattedDate;
};

rivets.formatters.time = function (value) {
  const date = new Date(value);
  return `${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`;
};

rivets.formatters.money = function (
  value,
  decimalPlaces = 2,
  thousandsSeparator = ",",
  decimalSeparator = "."
) {
  if (value === null || typeof value === "undefined" || isNaN(value)) {
    return ""; // Or some other default, e.g., "N/A"
  }
  let numValue = parseFloat(value);
  numValue = numValue.toFixed(decimalPlaces);
  const parts = numValue.split(decimalSeparator);
  let integerPart = parts[0];
  const decimalPart = parts[1] ? decimalSeparator + parts[1] : "";

  // Handle negative sign separately before adding thousands separators
  const isNegative = integerPart.startsWith("-");
  if (isNegative) {
    integerPart = integerPart.substring(1); // Remove the negative sign for formatting
  }
  const formattedIntegerPart = integerPart.replace(
    /\B(?=(\d{3})+(?!\d))/g,
    thousandsSeparator
  );
  const finalValue =
    (isNegative ? "-" : "") + formattedIntegerPart + decimalPart;

  return finalValue;
};

rivets.formatters.firstletter = function (value) {
  if (!value || value === null) {
    return "N/A";
  }
  return value.toString().split("")[0];
};
