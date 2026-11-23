/* Activity report charts (account app). The report API url is given on
   the script tag: <script src="activity-report.js" data-url="..."> */
(function () {
  'use strict';

  var url = document.currentScript.getAttribute('data-url');
  var labels = JSON.parse(document.getElementById('report-labels').textContent);
  var styles = getComputedStyle(document.documentElement);
  var token = function (name) { return styles.getPropertyValue(name).trim(); };
  var PALETTE = [token('--sh-primary'), token('--sh-accent'), '#7a9e7e', '#a0679c',
                 '#c9a227', '#4a90a4', '#8a6d3b', '#7d5ba6', '#c34a5f', '#4f7dc9'];
  Chart.defaults.color = token('--sh-muted');
  Chart.defaults.borderColor = token('--sh-border');

  var charts = {};

  function fmt(value) { return Math.round(value).toLocaleString(); }

  function draw(id, config) {
    var canvas = document.getElementById(id);
    if (!canvas) { return; }
    if (charts[id]) { charts[id].destroy(); }
    charts[id] = new Chart(canvas, config);
  }

  function topKey(dict) {
    var entries = Object.entries(dict || {}).filter(function (entry) { return entry[0] !== 'Others'; });
    if (!entries.length) { return '—'; }
    entries.sort(function (a, b) { return b[1] - a[1]; });
    return entries[0][0];
  }

  function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function renderMetrics(data) {
    var total = data.total.reduce(function (a, b) { return a + b; }, 0);
    var cards = [[labels.total, fmt(total)], [labels.common, topKey(data.by_type)],
                 [labels.area, topKey(data.by_area)]];
    if (data.top_users) { cards.push([labels.user, topKey(data.top_users)]); }
    document.getElementById('reportMetrics').innerHTML = cards.map(function (card) {
      return '<div class="col-6 col-md-3"><div class="card stat-card"><div class="card-body">' +
        '<div class="stat-label">' + escapeHtml(card[0]) + '</div>' +
        '<div class="stat-value fs-4">' + escapeHtml(String(card[1])) + '</div></div></div></div>';
    }).join('');
  }

  function render(data) {
    renderMetrics(data);
    var lineOptions = {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { beginAtZero: true, ticks: { callback: fmt } } }
    };
    draw('totalChart', {
      type: 'line',
      data: { labels: data.months, datasets: [{ label: labels.activities, data: data.total,
              borderColor: PALETTE[0], backgroundColor: PALETTE[0], tension: .3, fill: false }] },
      options: Object.assign({}, lineOptions, { plugins: { legend: { display: false } } })
    });
    var types = Object.keys(data.by_type);
    draw('typeChart', {
      type: 'line',
      data: { labels: data.months, datasets: types.map(function (name, index) {
        return { label: name, data: data.by_type[name], tension: .3,
                 borderColor: PALETTE[index % PALETTE.length], backgroundColor: PALETTE[index % PALETTE.length] };
      }) },
      options: lineOptions
    });
    var areas = Object.keys(data.by_area);
    draw('areaChart', {
      type: 'doughnut',
      data: { labels: areas, datasets: [{ data: areas.map(function (name) { return data.by_area[name]; }),
              backgroundColor: areas.map(function (_, index) { return PALETTE[index % PALETTE.length]; }) }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
    });
    if (data.top_users) {
      var users = Object.keys(data.top_users);
      draw('topUsersChart', {
        type: 'bar',
        data: { labels: users, datasets: [{ label: labels.activities, borderRadius: 6,
                data: users.map(function (name) { return data.top_users[name]; }), backgroundColor: PALETTE[1] }] },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
      });
    }
  }

  function load() {
    var params = new URLSearchParams({
      from_date: document.getElementById('reportFromDate').value,
      to_date: document.getElementById('reportToDate').value
    });
    fetch(url + '?' + params.toString(), { credentials: 'same-origin', headers: { 'Accept': 'application/json' } })
      .then(function (response) { return response.json(); })
      .then(render);
  }

  document.getElementById('reportApply').addEventListener('click', load);
  load();
})();
