// Change all selectors to bootstrap selectors
var selects = document.getElementsByTagName('select');
for (var i = 0; i < selects.length; i++){
  select = selects[i]
  if (!hasClass(select, "selectpicker")) {
    select.classList.add("selectpicker")
    select.setAttribute("data-live-search", "true")
    select.setAttribute("data-style", "btn-outline-primary")

    for (var j = 0; j < select.options.length; j++){
      option = select.options[j]
      if (option.value == ''){
        option.setAttribute('disabled', 'disabled')
        option.text = "Select " + select.name.charAt(0).toUpperCase() + select.name.slice(1).replace('_', ' ')
      } else{
        option.setAttribute('data-tokens', option.text)
      }
    }
  }
}
// check if element has a certain class
function hasClass(element, className) {
  return (' ' + element.className + ' ').indexOf(' ' + className + ' ') > -1;
}
