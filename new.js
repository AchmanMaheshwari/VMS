// Initialize data storage
const users = [
  { empId: "ADMIN001", password: "admin123", name: "Admin User", role: "admin" },
  { empId: "HR001", password: "hr123", name: "HR User", role: "hr" },
  { empId: "SEC001", password: "security123", name: "Security User", role: "security" }
];
localStorage.setItem('users', JSON.stringify(users));

let visitors = JSON.parse(localStorage.getItem('visitors')) || [];
let approvals = JSON.parse(localStorage.getItem('approvals')) || [];

// Login logic
document.getElementById('loginForm').addEventListener('submit', function(e) {
  e.preventDefault();
  const empId = document.getElementById('empId').value;
  const password = document.getElementById('password').value;
  const user = users.find(u => u.empId === empId && u.password === password);
  if (user) {
    localStorage.setItem('currentUser', JSON.stringify(user));
    document.getElementById('userName').textContent = user.name;
    document.getElementById('userRole').textContent = user.role.charAt(0).toUpperCase() + user.role.slice(1);
    document.getElementById('userAvatar').textContent = user.name.charAt(0);
    showMainApp(user.role);
  } else {
    alert("Invalid credentials. Try again.");
  }
});

// Show main app based on role
function showMainApp(role) {
  document.getElementById('loginScreen').classList.add('hidden');
  document.getElementById('mainApp').classList.remove('hidden');
  updateNavTabs(role);
  showTab('dashboard');
  updateDashboard();
}

// Update navigation tabs based on role
function updateNavTabs(role) {
  const navTabs = document.getElementById('navigationTabs');
  navTabs.innerHTML = '';
  const tabs = [
    { id: 'dashboard', icon: 'fas fa-chart-line', label: 'Dashboard', show: true },
    { id: 'newVisitor', icon: 'fas fa-user-plus', label: 'New Visitor', show: role === 'admin' || role === 'hr' || role === 'security' },
    { id: 'visitors', icon: 'fas fa-users', label: 'Visitors', show: true },
    { id: 'approval', icon: 'fas fa-check-circle', label: 'Approvals', show: role === 'admin' || role === 'security' },
    { id: 'users', icon: 'fas fa-user-cog', label: 'Users', show: role === 'admin' || role === 'hr' },
    { id: 'checkout', icon: 'fas fa-sign-out-alt', label: 'Checkout', show: role === 'security' }
  ];
  tabs.forEach(tab => {
    if (tab.show) {
      const button = document.createElement('button');
      button.className = 'nav-tab';
      if (tab.id === 'dashboard') button.classList.add('active');
      button.innerHTML = `<i class="${tab.icon}"></i> ${tab.label}`;
      button.onclick = () => showTab(tab.id);
      navTabs.appendChild(button);
    }
  });
}

// Show tab content
function showTab(tabId) {
  document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(tab => tab.classList.add('hidden'));
  document.getElementById(tabId).classList.remove('hidden');
  const activeTab = document.querySelector(`.nav-tab[onclick*="${tabId}"]`);
  if (activeTab) activeTab.classList.add('active');
  if (tabId === 'dashboard') updateDashboard();
  if (tabId === 'visitors') updateVisitorsTable();
  if (tabId === 'approval') updateApprovalsTable();
  if (tabId === 'users') updateUsersTable();
  if (tabId === 'checkout') updateCheckoutTable();
}

// Update dashboard stats
function updateDashboard() {
  document.getElementById('totalVisitors').textContent = visitors.filter(v => isToday(new Date(v.entryTime))).length;
  document.getElementById('pendingApprovals').textContent = approvals.length;
  document.getElementById('activeVisitors').textContent = visitors.filter(v => v.status === 'inside').length;
  document.getElementById('checkedOut').textContent = visitors.filter(v => v.status === 'checked-out' && isToday(new Date(v.checkoutTime))).length;
  updateRecentVisitorsTable();
}

function isToday(date) {
  const today = new Date();
  return date.getDate() === today.getDate() && 
         date.getMonth() === today.getMonth() && 
         date.getFullYear() === today.getFullYear();
}

// Update recent visitors table
function updateRecentVisitorsTable() {
  const table = document.getElementById('recentVisitorsTable');
  table.innerHTML = '';
  const recent = visitors.slice(-5).reverse();
  recent.forEach(v => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${v.id || ''}</td>
      <td>${v.visitorName}</td>
      <td>${v.visitorMobile}</td>
      <td>${v.representing}</td>
      <td>${formatTime(v.entryTime)}</td>
      <td><span class="status-badge status-${v.status === 'inside' ? 'inside' : 'checked-out'}">${v.status === 'inside' ? 'Inside' : 'Checked Out'}</span></td>
      <td><button class="btn btn-secondary" onclick="viewVisitor('${v.id}')">View</button></td>
    `;
    table.appendChild(row);
  });
}

// Update visitors table
function updateVisitorsTable() {
  const table = document.getElementById('visitorsTable');
  table.innerHTML = '';
  visitors.forEach(v => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${v.id || ''}</td>
      <td>${v.visitorName}</td>
      <td>${v.visitorMobile}</td>
      <td>${v.representing}</td>
      <td>${formatTime(v.entryTime)}</td>
      <td><span class="status-badge status-${v.status === 'inside' ? 'inside' : 'checked-out'}">${v.status === 'inside' ? 'Inside' : 'Checked Out'}</span></td>
      <td><button class="btn btn-secondary" onclick="viewVisitor('${v.id}')">View</button></td>
    `;
    table.appendChild(row);
  });
}

// Update approvals table
function updateApprovalsTable() {
  const table = document.getElementById('approvalsTable');
  table.innerHTML = '';
  approvals.forEach(a => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${a.id || ''}</td>
      <td>${a.visitorName}</td>
      <td>${a.visitorMobile}</td>
      <td>${a.representing}</td>
      <td>${a.purpose}</td>
      <td>${formatTime(a.entryTime)}</td>
      <td>
        <button class="btn btn-success" onclick="approveVisitor('${a.id}')">Approve</button>
        <button class="btn btn-danger" onclick="rejectVisitor('${a.id}')">Reject</button>
      </td>
    `;
    table.appendChild(row);
  });
}

// Update users table
function updateUsersTable() {
  const table = document.getElementById('usersTable');
  table.innerHTML = '';
  users.forEach(u => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${u.empId}</td>
      <td>${u.name}</td>
      <td>${u.department || '-'}</td>
      <td>${u.mobile || '-'}</td>
      <td>${u.role}</td>
      <td><span class="status-badge status-approved">Active</span></td>
      <td>
        <button class="btn btn-secondary" onclick="editUser('${u.empId}')">Edit</button>
      </td>
    `;
    table.appendChild(row);
  });
}

// Update checkout table
function updateCheckoutTable() {
  const table = document.getElementById('checkoutTable');
  table.innerHTML = '';
  const insideVisitors = visitors.filter(v => v.status === 'inside');
  insideVisitors.forEach(v => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${v.id || ''}</td>
      <td>${v.visitorName}</td>
      <td>${v.visitorMobile}</td>
      <td>${v.representing}</td>
      <td>${formatTime(v.entryTime)}</td>
      <td><button class="btn btn-primary" onclick="checkoutVisitor('${v.id}')">Checkout</button></td>
    `;
    table.appendChild(row);
  });
}

// Helper functions
function formatTime(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function logout() {
  localStorage.removeItem('currentUser');
  document.getElementById('loginScreen').classList.remove('hidden');
  document.getElementById('mainApp').classList.add('hidden');
}

// Register new visitor
document.getElementById('visitorForm')?.addEventListener('submit', function(e) {
  e.preventDefault();
  const formData = new FormData(this);
  const data = Object.fromEntries(formData.entries());
  data.entryTime = new Date().toISOString();
  data.status = 'inside';
  data.id = 'V' + Date.now();
  visitors.push(data);
  localStorage.setItem('visitors', JSON.stringify(visitors));
  alert('Visitor registered successfully!');
  resetForm();
  showTab('dashboard');
  updateDashboard();
});

function resetForm() {
  document.getElementById('visitorForm').reset();
}

function viewVisitor(id) {
  // Implement view logic
  alert(`Viewing visitor ${id}`);
}

function approveVisitor(id) {
  const index = approvals.findIndex(a => a.id === id);
  if (index !== -1) {
    const visitor = approvals[index];
    visitor.status = 'inside';
    visitors.push(visitor);
    approvals.splice(index, 1);
    localStorage.setItem('visitors', JSON.stringify(visitors));
    localStorage.setItem('approvals', JSON.stringify(approvals));
    updateApprovalsTable();
    updateDashboard();
  }
}

function rejectVisitor(id) {
  const index = approvals.findIndex(a => a.id === id);
  if (index !== -1) {
    approvals.splice(index, 1);
    localStorage.setItem('approvals', JSON.stringify(approvals));
    updateApprovalsTable();
  }
}

function checkoutVisitor(id) {
  const index = visitors.findIndex(v => v.id === id);
  if (index !== -1) {
    visitors[index].status = 'checked-out';
    visitors[index].checkoutTime = new Date().toISOString();
    localStorage.setItem('visitors', JSON.stringify(visitors));
    updateCheckoutTable();
    updateDashboard();
  }
}

function filterVisitors() {
  const search = document.getElementById('visitorSearch').value.toLowerCase();
  const rows = document.querySelectorAll('#visitorsTable tr');
  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    if (text.includes(search) || row.querySelector('th')) {
      row.style.display = '';
    } else {
      row.style.display = 'none';
    }
  });
}

function filterCheckoutVisitors() {
  const search = document.getElementById('checkoutSearch').value.toLowerCase();
  const rows = document.querySelectorAll('#checkoutTable tr');
  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    if (text.includes(search) || row.querySelector('th')) {
      row.style.display = '';
    } else {
      row.style.display = 'none';
    }
  });
}

// Initialize app
window.onload = function() {
  const user = JSON.parse(localStorage.getItem('currentUser'));
  if (user) {
    showMainApp(user.role);
  }
};
