const label = arguments[0];

const elements = document.querySelectorAll(".ipc-metadata-list-item__label");
for (let i = 0; i < elements.length; i++) {
  if (elements[i].textContent == label) {
    const creditElements = elements[i].parentElement.querySelectorAll(
      ".ipc-metadata-list-item__list-content-item"
    );
    return [...creditElements].map((element) => element.textContent);
  }
}
