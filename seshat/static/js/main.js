/* SESHAT front-end helpers (no framework, no jQuery) */
(function () {
  'use strict';

  // Tooltips
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
    new bootstrap.Tooltip(el);
  });

  // Keep the automatic theme in sync with the operating system
  var root = document.documentElement;
  if (root.dataset.theme === 'auto' && window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (event) {
      root.setAttribute('data-bs-theme', event.matches ? 'dark' : 'light');
    });
  }
  // The theme toggle sends what the user currently sees
  document.querySelectorAll('[data-theme-current]').forEach(function (input) {
    input.value = root.getAttribute('data-bs-theme') || 'light';
  });

  // Shared delete confirmation modal
  var deleteModal = document.getElementById('deleteModal');
  if (deleteModal) {
    deleteModal.addEventListener('show.bs.modal', function (event) {
      var button = event.relatedTarget;
      deleteModal.querySelector('form').setAttribute('action', button.getAttribute('data-url'));
      deleteModal.querySelector('[data-delete-name]').textContent = button.getAttribute('data-name') || '';
    });
  }

  // Filters that submit their form when changed
  document.querySelectorAll('[data-autosubmit]').forEach(function (el) {
    el.addEventListener('change', function () { el.form.submit(); });
  });

  // Dynamic formsets: <div data-formset="prefix"> with a <template> row
  document.querySelectorAll('[data-formset]').forEach(function (container) {
    var prefix = container.getAttribute('data-formset');
    var total = document.getElementById('id_' + prefix + '-TOTAL_FORMS');
    var template = document.getElementById(prefix + '-empty');
    var rows = container.querySelector('[data-formset-rows]');

    function bindRow(row) {
      var remove = row.querySelector('[data-formset-remove]');
      if (remove) {
        remove.addEventListener('click', function () {
          var deleteInput = row.querySelector('input[name$="-DELETE"]');
          if (deleteInput) {
            deleteInput.checked = true;
            row.classList.add('is-deleted');
          } else {
            row.remove();
          }
          container.dispatchEvent(new Event('formset:changed'));
        });
      }
      container.dispatchEvent(new CustomEvent('formset:row', { detail: row }));
    }

    rows.querySelectorAll('[data-formset-row]').forEach(bindRow);

    container.querySelectorAll('[data-formset-add]').forEach(function (button) {
      button.addEventListener('click', function () {
        var index = parseInt(total.value, 10);
        var html = template.innerHTML.replace(/__prefix__/g, index);
        var wrapper = document.createElement('div');
        wrapper.innerHTML = html.trim();
        var row = wrapper.firstElementChild;
        rows.appendChild(row);
        total.value = index + 1;
        bindRow(row);
        var first = row.querySelector('select, input:not([type=hidden])');
        if (first) { first.focus(); }
        container.dispatchEvent(new Event('formset:changed'));
      });
    });
  });

  // Photo cropping: <input type="file" data-crop="size"> fills id_x, id_y,
  // id_width and id_height from the crop box chosen in #cropModal
  document.querySelectorAll('input[type="file"][data-crop]').forEach(function (input) {
    var modalElement = document.getElementById('cropModal');
    if (!modalElement || typeof Cropper === 'undefined') { return; }
    var image = modalElement.querySelector('img');
    var modal = bootstrap.Modal.getOrCreateInstance(modalElement, { backdrop: 'static' });
    var preview = document.querySelector(input.getAttribute('data-preview'));
    var cropper = null;
    var minSize = parseInt(input.getAttribute('data-crop'), 10) || 200;

    input.addEventListener('change', function () {
      if (!input.files || !input.files[0]) { return; }
      var reader = new FileReader();
      reader.onload = function (event) {
        image.src = event.target.result;
        modal.show();
      };
      reader.readAsDataURL(input.files[0]);
    });

    modalElement.addEventListener('shown.bs.modal', function () {
      cropper = new Cropper(image, {
        viewMode: 1,
        aspectRatio: 1,
        autoCropArea: 1,
        minCropBoxWidth: Math.min(minSize, 120),
        minCropBoxHeight: Math.min(minSize, 120)
      });
    });
    modalElement.addEventListener('hidden.bs.modal', function () {
      if (cropper) { cropper.destroy(); cropper = null; }
    });
    modalElement.querySelectorAll('[data-zoom]').forEach(function (button) {
      button.addEventListener('click', function () {
        if (cropper) { cropper.zoom(parseFloat(button.getAttribute('data-zoom'))); }
      });
    });
    modalElement.querySelector('[data-crop-apply]').addEventListener('click', function () {
      if (!cropper) { return; }
      var data = cropper.getData(true);
      ['x', 'y', 'width', 'height'].forEach(function (key) {
        var field = document.getElementById('id_' + key);
        if (field) { field.value = data[key]; }
      });
      if (preview) {
        preview.src = cropper.getCroppedCanvas({ width: 300, height: 300 }).toDataURL();
      }
      modal.hide();
    });
  });
})();
