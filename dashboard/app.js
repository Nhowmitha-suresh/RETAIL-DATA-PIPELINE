const appState = {
  currentPage: window.location.hash.replace('#', '') || 'dashboard',
  filters: {
    dateRange: 'Last 30 Days',
    category: 'All Categories',
    region: 'All Regions',
    store: 'All Stores',
    warehouse: 'All Warehouses',
    state: 'All States',
    city: 'All Cities',
    customerType: 'All Types',
    gender: 'All',
    ageGroup: 'All Ages',
    paymentMethod: 'All Methods',
    channel: 'All Channels',
    device: 'All Devices',
    festival: 'All',
    weather: 'All',
    promotion: 'All',
    coupon: 'All',
    orderStatus: 'All Status',
  },
  summary: null,
  pageDefinitions: [
    { id: 'dashboard', title: 'Executive Overview' },
    { id: 'sales', title: 'Sales Analytics' },
    { id: 'revenue', title: 'Revenue Analytics' },
    { id: 'customers', title: 'Customer Intelligence' },
    { id: 'products', title: 'Product Intelligence' },
    { id: 'inventory', title: 'Inventory Analytics' },
    { id: 'finance', title: 'Financial Analytics' },
    { id: 'marketing', title: 'Marketing Analytics' },
    { id: 'forecasting', title: 'Forecasting' },
    { id: 'ai-insights', title: 'AI Insights' },
    { id: 'reports', title: 'Executive Report' },
    { id: 'settings', title: 'Settings' },
  ],
  charts: {},
  liveInterval: null,
};

const formatCurrency = value => {
  const abs = Math.abs(value);
  if (abs >= 1_00_00_000) return `₹${(value / 1_00_00_000).toFixed(1)} Cr`;
  if (abs >= 1_00_000) return `₹${(value / 1_00_00_000).toFixed(1)} L`;
  if (abs >= 1000) return `₹${value.toLocaleString('en-IN')}`;
  return `₹${value.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
};

const formatPercent = value => `${value.toFixed(1)}%`;

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
  window.addEventListener('popstate', () => {
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
    appState.summary = result;
    return result;
  } catch (error) {
    console.error(error);
    showToast('Failed to fetch summary', 'error');
  }
};

const renderKpiCards = cards => {
  const container = document.getElementById('kpiGrid');
  container.innerHTML = cards.map(card => `
    <article class="kpi-card ${card.variant || ''}" data-kpi="${card.id}">
      <div class="kpi-header"><span class="kpi-icon">${card.icon}</span><div>
        <p class="kpi-title">${card.label}</p>
        <p class="kpi-trend ${card.trendClass}">${card.delta}</p>
      </div></div>
      <div class="kpi-value">${card.value}</div>
      <div class="kpi-footnote">${card.insight}</div>
      <div class="kpi-sparkline"><canvas id="spark-${card.id}"></canvas></div>
    </article>
  `).join('');
};

const buildExecutiveCards = summary => [
  { id: 'revenue', label: 'Revenue', icon: '💰', value: formatCurrency(summary.total_revenue), delta: `+${summary.revenue_growth_pct}% vs LY`, trendClass: 'positive', insight: 'Strong top-line momentum', series: summary.monthly_sales },
  { id: 'profit', label: 'Profit', icon: '📈', value: formatCurrency(summary.total_profit), delta: `+${summary.profit_growth_pct}%`, trendClass: 'positive', insight: 'Healthy operating gains', series: summary.monthly_profit },
  { id: 'expenses', label: 'Expenses', icon: '💸', value: formatCurrency(summary.total_expenses), delta: `-${summary.expense_reduction_pct}%`, trendClass: 'positive', insight: 'Controlled spend', series: summary.monthly_expenses },
  { id: 'customers', label: 'Customers', icon: '👥', value: summary.unique_customers.toLocaleString('en-IN'), delta: `+${summary.customer_growth_pct}%`, trendClass: 'positive', insight: 'High retention lift', series: summary.customer_trend },
  { id: 'orders', label: 'Orders', icon: '🛒', value: summary.total_orders.toLocaleString('en-IN'), delta: `+${summary.order_growth_pct}%`, trendClass: 'positive', insight: 'Order volumes improving', series: summary.order_trend },
  { id: 'inventory', label: 'Inventory Value', icon: '📦', value: formatCurrency(summary.inventory_value), delta: `-${summary.stock_turnover_pct}%`, trendClass: 'positive', insight: 'Efficient stock turn', series: summary.inventory_trend },
];

const renderDashboardPage = summary => {
  renderKpiCards(buildExecutiveCards(summary));
  document.getElementById('topRevenue').textContent = formatCurrency(summary.top_region_revenue);
  document.getElementById('topCategory').textContent = summary.top_category;
  document.getElementById('topBrand').textContent = summary.top_brand;
  document.getElementById('topChannel').textContent = summary.top_channel;
};

const initPage = async () => {
  const summary = await fetchSummary();
  if (!summary) return;
  appState.summary = summary;
  renderDashboardPage(summary);
  setActivePage(appState.currentPage);
  initNavigation();
};

window.addEventListener('DOMContentLoaded', initPage);
