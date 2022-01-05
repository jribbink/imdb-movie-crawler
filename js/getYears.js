let elements = document.getElementsByTagName("*");
for (let i = 0; i < elements.length; i++)
  if (/\/releaseinfo\?/g.test(elements[i].getAttribute("href")))
    return elements[i].textContent;
