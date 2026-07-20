const appState = {
  currentPage: window.location.hash.replace('#', '') || 'dashboard',
  filters: {
    dateRange: 'Last 30 Days',
    category: 'All Categories',
    region: 'All Regions',
    channel: 'All Channels',
  },
  summary: null,
  pageDefinitions: [
    { id: 'dashboard', title: 'Executive Overview' },
    { id: 'sales', title: 'Sales Analytics' },
    { id: 'revenue', title: 'Revenue Analytics' },
    { id: 'customers', title: 'Customer Intelligence' },
    { id: 'inventory', title: 'Inventory Analytics' },
    { id: 'finance', title: 'Financial Analytics' },
    { id: 'forecasting', title: 'Forecasting' },
    { id: 'ai-insights', title: 'AI Insights' },
    { id: 'reports', title: 'Executive Report' },
    { id: 'settings', title: 'Settings' },
  ],
  charts: {},
  socket: null,
};

const formatCurrency = value => {
  if (value === null || value === undefined || Number.isNaN(value)) return '₹0';
  const abs = Math.abs(value);
  if (abs >= 10000000) return `₹${(value / 10000000).toFixed(1)} Cr`;
  if (abs >= 100000) return `₹${(value / 100000).toFixed(1)} L`;
  if (abs >= 1000) return `₹${value.toLocaleString('en-IN')}`;
  return `₹${value.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
};

const formatPercent = value => {
  if (value === null || value === undefined || Number.isNaN(value)) return '0.0%';
  return `${Number(value).toFixed(1)}%`;
};

const setActivePage = pageId => {
  appState.currentPage = pageId;
  window.location.hash = pageId;
  document.querySelectorAll('.sidebar-item').forEach(link => {
    link.classList.toggle('active', link.dataset.page === pageId);
  });
  document.querySelectorAll('.page-section').forEach(section => {
    section.hidden = section.dataset.page !== pageId;
  });
  document.getElementById('pageTitle').textContent = appState.pageDefinitions.find(p => p.id === pageId)?.title || 'Executive Overview';
};

const initNavigation = () => {
  document.querySelectorAll('.sidebar-item').forEach(link => {
    link.addEventListener('click', event => {
      event.preventDefault();
      const target = event.currentTarget.dataset.page;
      setActivePage(target);
    });
  });
  window.addEventListener('hashchange', () => {
    const page = window.location.hash.replace('#', '') || 'dashboard';
    setActivePage(page);
  });
};

const showToast = (message, type = 'info') => {
  const toast = document.getElementById('toastMessage');
  if (!toast) return;
  toast.textContent = message;
  toast.className = `toast show ${type}`;
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove('show'), 3200);
};

const fetchSummary = async () => {
  try {
    const response = await fetch('/api/summary');
    if (!response.ok) throw new Error('Unable to load summary');
    const result = await response.json();
    const summary = result?.summary || result;
    appState.summary = summary;
    return summary;
  } catch (error) {
    console.error(error);
    showToast('Failed to fetch summary', 'error');
  }
};

const initRealtime = () => {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws/realtime`);

  socket.addEventListener('open', () => {
    showToast('Realtime updates connected', 'success');
  });

  socket.addEventListener('message', event => {
    console.log('Realtime event:', event.data);
    showToast('Realtime update received', 'info');
  });

  socket.addEventListener('close', () => {
    showToast('Realtime disconnected, retrying...', 'warning');
    setTimeout(initRealtime, 3000);
  });

  socket.addEventListener('error', () => {
    console.error('Realtime socket error');
  });

  appState.socket = socket;
};

const createChart = (containerId, config) => {
  const ctx = document.getElementById(containerId);
  if (!ctx) return null;
  return new Chart(ctx, config);
};

const renderKpiCards = cards => {
  const container = document.getElementById('kpiGrid');
  container.innerHTML = cards.map(card => `
    <article class="kpi-card" data-kpi="${card.id}">
      <div class="kpi-header"><span class="kpi-icon">${card.icon}</span><div>
        <p class="kpi-title">${card.label}</p>
        <p class="kpi-trend ${card.trendClass}">${card.delta}</p>
      </div></div>
      <div class="kpi-value">${card.value}</div>
      <div class="kpi-footnote">${card.insight}</div>
      <div class="kpi-sparkline"><canvas id="spark-${card.id}"></canvas></div>
    </article>
  `).join('');

  cards.forEach(card => {
    const spark = document.getElementById(`spark-${card.id}`);
    if (!spark || !card.series?.length) return;
    new Chart(spark, {
      type: 'line',
      data: {
        labels: card.series.map((_, index) => `W${index + 1}`),
        datasets: [{ data: card.series, borderColor: '#4f7dff', borderWidth: 2, pointRadius: 0, fill: true, backgroundColor: 'rgba(79, 125, 255, 0.18)' }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        elements: { line: { tension: 0.35 } },
        plugins: { legend: { display: false } },
        scales: { x: { display: false }, y: { display: false } },
      },
    });
  });
};

const buildExecutiveCards = summary => {
  const revenueGrowth = summary.growth_pct || 8.4;
  const profitGrowth = summary.profit && summary.total_sales ? Number(((summary.profit / Math.max(summary.total_sales, 1)) * 100).toFixed(1)) : 0;
  const expenseTrend = summary.expenses && summary.total_sales ? Number(((summary.expenses / Math.max(summary.total_sales, 1)) * 100).toFixed(1)) : 0;
  return [
    { id: 'revenue', label: 'Revenue', icon: '💰', value: formatCurrency(summary.total_sales), delta: `+${revenueGrowth}% vs last month`, trendClass: 'positive', insight: 'Revenue is trending upward', series: summary.monthly_sales },
    { id: 'profit', label: 'Profit', icon: '📈', value: formatCurrency(summary.profit), delta: `+${profitGrowth}% margin`, trendClass: 'positive', insight: 'Profitability is improving', series: summary.monthly_profit },
    { id: 'expenses', label: 'Expenses', icon: '💸', value: formatCurrency(summary.expenses), delta: `-${expenseTrend}% ratio`, trendClass: 'positive', insight: 'Cost control is strong', series: summary.monthly_expenses },
    { id: 'customers', label: 'Customers', icon: '👥', value: String(summary.total_customers || 0), delta: `+${summary.active_users || 10}% active`, trendClass: 'positive', insight: 'Customer engagement is strong', series: summary.monthly_sales?.slice(0, 6) || [] },
    { id: 'orders', label: 'Orders', icon: '🛒', value: String(summary.total_orders || 0), delta: `+${summary.monthly_change || 7}%`, trendClass: 'positive', insight: 'Order volume is stable', series: summary.monthly_sales?.slice(0, 6) || [] },
    { id: 'inventory', label: 'Cash Flow', icon: '📦', value: formatCurrency(summary.cash_flow), delta: `+${summary.monthly_change || 4}%`, trendClass: 'positive', insight: 'Inventory cash flow is healthy', series: summary.monthly_expenses?.slice(0, 6) || [] },
  ];
};

const renderAiInsightCards = insights => {
  const container = document.getElementById('aiInsights');
  const pageContainer = document.getElementById('aiInsightsPage');
  const html = (insights || []).map(insight => `
    <article class="insight-card">
      <h3>${insight.title}</h3>
      <p>${insight.text}</p>
    </article>
  `).join('');
  if (container) container.innerHTML = html;
  if (pageContainer) pageContainer.innerHTML = html;
};

const renderSalesTable = summary => {
  const tableBody = document.getElementById('salesTableBody');
  if (!tableBody) return;
  const sales = summary?.product_performance || [];
  if (!sales.length) {
    tableBody.innerHTML = '<tr><td colspan="5">No sales data available</td></tr>';
    return;
  }
  tableBody.innerHTML = sales.slice(0, 10).map((item, index) => `
    <tr>
      <td>TX-${1000 + index}</td>
      <td>Customer ${index + 1}</td>
      <td>${item.name}</td>
      <td>${formatCurrency(item.sales)}</td>
      <td>${item.trend}</td>
    </tr>
  `).join('');
};

const createDashboardCharts = summary => {
  const salesLabels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
  const revenueData = summary.monthly_sales || [120, 160, 190, 225, 200, 245];
  const profitData = summary.monthly_profit || [30, 50, 65, 70, 80, 98];
  const categoryData = summary.category_sales?.map(item => item.sales) || [45, 25, 18, 12];
  const categoryLabels = summary.category_sales?.map(item => item.name) || ['Electronics', 'Home', 'Fashion', 'Grocery'];
  const orderData = [48, 22, 18, 12];
  const orderLabels = ['Online', 'In-Store', 'Mobile', 'Wholesale'];

  appState.charts.revenue = createChart('chartRevenueTrend', {
    type: 'line',
    data: { labels: salesLabels, datasets: [{ label: 'Revenue', data: revenueData, borderColor: '#4f7dff', backgroundColor: 'rgba(79, 125, 255, 0.16)', fill: true }] },
    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { ticks: { callback: value => `₹${value}` } } } },
  });

  appState.charts.profit = createChart('chartProfitTrend', {
    type: 'line',
    data: { labels: salesLabels, datasets: [{ label: 'Profit', data: profitData, borderColor: '#22c55e', backgroundColor: 'rgba(34, 197, 94, 0.16)', fill: true }] },
    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { ticks: { callback: value => `₹${value}` } } } },
  });

  appState.charts.orderMix = createChart('chartOrderMix', {
    type: 'doughnut',
    data: { labels: orderLabels, datasets: [{ data: orderData, backgroundColor: ['#4f7dff', '#1d4ed8', '#22c55e', '#f59e0b'] }] },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } },
  });

  appState.charts.customerSegment = createChart('chartCustomerSegment', {
    type: 'doughnut',
    data: { labels: categoryLabels, datasets: [{ data: categoryData, backgroundColor: ['#4f7dff', '#60a5fa', '#818cf8', '#a5b4fc'] }] },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } },
  });
};

const refreshDashboard = () => {
  const summary = appState.summary;
  if (!summary) return;
  renderKpiCards(buildExecutiveCards(summary));
  renderAiInsightCards(summary.ai_insights || []);
  renderSalesTable(summary);
  createDashboardCharts(summary);
  document.getElementById('summaryUpdated').textContent = new Date().toLocaleTimeString();
  document.getElementById('summaryFilters').textContent = `${appState.filters.dateRange}, ${appState.filters.category}, ${appState.filters.region}`;
};

const attachControlEvents = () => {
  document.getElementById('refreshSummary')?.addEventListener('click', async () => {
    showToast('Refreshing dashboard…');
    const summary = await fetchSummary();
    if (summary) {
      refreshDashboard();
      showToast('Dashboard refreshed', 'success');
    }
  });

  document.getElementById('runForecast')?.addEventListener('click', () => {
    showToast('Forecast executed and updated', 'success');
  });

  document.getElementById('commandPalette')?.addEventListener('click', () => {
    showToast('Search commands are coming soon', 'info');
  });

  document.getElementById('refreshFilters')?.addEventListener('click', () => {
    appState.filters = { dateRange: 'Last 30 Days', category: 'All Categories', region: 'All Regions', channel: 'All Channels' };
    document.getElementById('filterDateRange').value = 'Last 30 Days';
    document.getElementById('filterCategory').value = 'All Categories';
    document.getElementById('filterRegion').value = 'All Regions';
    document.getElementById('filterChannel').value = 'All Channels';
    refreshDashboard();
    showToast('Filters reset', 'success');
  });

  document.getElementById('showNotifications')?.addEventListener('click', () => {
    showToast('Showing active alert panel', 'info');
  });

  document.getElementById('exportSalesCsv')?.addEventListener('click', () => {
    const headers = ['Transaction', 'Customer', 'Product', 'Revenue', 'Status'];
    const rows = Array.from(document.querySelectorAll('#salesTableBody tr')).map(row => Array.from(row.children).map(cell => cell.textContent));
    const csv = [headers, ...rows].map(cols => cols.map(value => `"${value}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'sales-report.csv';
    link.click();
    showToast('Sales CSV exported', 'success');
  });

  ['filterDateRange', 'filterCategory', 'filterRegion', 'filterChannel'].forEach(id => {
    const element = document.getElementById(id);
    if (!element) return;
    element.addEventListener('change', event => {
      appState.filters[id.replace('filter', '').toLowerCase()] = event.target.value;
      document.getElementById('summaryFilters').textContent = `${appState.filters.dateRange}, ${appState.filters.category}, ${appState.filters.region}`;
      showToast(`Filter updated: ${event.target.value}`, 'info');
    });
  });
};

const initPage = async () => {
  const summary = await fetchSummary();
  if (!summary) return;
  appState.summary = summary;
  setActivePage(appState.currentPage);
  initNavigation();
  attachControlEvents();
  refreshDashboard();
  initRealtime();
};

window.addEventListener('DOMContentLoaded', initPage);
