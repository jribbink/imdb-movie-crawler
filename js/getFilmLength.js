let elements = document.querySelectorAll(".ipc-inline-list__item");

for (let i = 0; i < elements.length; i++)
  if (/((\d+h ?)(\d+min))|(\d+h)|(\d+min)/g.test(elements[i].textContent))
    return elements[i].textContent;
