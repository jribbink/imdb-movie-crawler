const text = arguments[0];
const elements = document.getElementsByTagName("*");

for (let i = 0; i < elements.length; i++)
  if (elements[i].textContent.includes("text")) return elements[i];
