let elements = document.getElementsByTagName("*")

for(let i = 0; i < elements.length; i++) {
    if(elements[i].textContent.includes("ERR_")) return true
}

return false