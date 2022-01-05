let regex = new RegExp(arguments[0]);
let knowledge_panel = arguments[1];

let links = knowledge_panel.querySelectorAll("a");
for (let i = 0; i < links.length; i++) {
  let href = links[i].getAttribute("href");
  if (href && href.match(regex)) return links[i];
}
