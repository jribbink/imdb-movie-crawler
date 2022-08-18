const links = [...document.querySelectorAll('.yuRUbf > a')]

for (let i = 0; i < links.length; i++) {
    const link = links[i]
    if(link.getAttribute('href').match(/https:\/\/www\.imdb\.com\/title\/.+\//)) {
        return link
    }
}