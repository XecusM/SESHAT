/* Order form: shows the item stock, suggests the unit price and keeps the
   order total up to date */
(function () {
  'use strict';
  var container = document.querySelector('[data-formset="lines"]');
  if (!container) { return; }
  var raw = JSON.parse(document.getElementById('items-data').textContent);
  var items = typeof raw === 'string' ? JSON.parse(raw) : raw;
  var totalElement = document.querySelector('[data-order-total]');
  var inStock = container.getAttribute('data-in-stock') || 'in stock';

  function field(row, name) { return row.querySelector('[name$="-' + name + '"]'); }

  function updateTotal() {
    var total = 0;
    container.querySelectorAll('[data-formset-row]').forEach(function (row) {
      if (row.classList.contains('is-deleted')) { return; }
      var item = items[field(row, 'item').value];
      var quantity = parseFloat(field(row, 'quantity').value) || 0;
      var price = parseFloat(field(row, 'price').value);
      if (isNaN(price) && item) { price = parseFloat(item.price); }
      total += quantity * (price || 0);
    });
    totalElement.textContent = total.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function bind(row) {
    var select = field(row, 'item');
    var info = row.querySelector('[data-line-info]');
    function refresh() {
      var item = items[select.value];
      field(row, 'price').placeholder = item ? item.price : '';
      info.textContent = item ? (item.description ? item.description + ' · ' : '') + item.quantity + ' ' + inStock : '';
      updateTotal();
    }
    select.addEventListener('change', refresh);
    row.addEventListener('input', updateTotal);
    refresh();
  }

  container.addEventListener('formset:row', function (event) { bind(event.detail); });
  container.addEventListener('formset:changed', updateTotal);
  container.querySelectorAll('[data-formset-row]').forEach(bind);
})();
