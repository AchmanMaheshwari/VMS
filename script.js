// Visitor Management System - JavaScript

// Global variables
let visitors = [];
let users = [];
let currentUser = null;
let visitorIdCounter = 1000;

// Site and Plant mapping
const sitePlantMapping = {
    'SITE001': ['PLANT001 - Administration', 'PLANT002 - IT Center'],
    'SITE002': ['PLANT003 - Production Line A', 'PLANT004 - Production Line B', 'PLANT005 - Quality Control'],
    'SITE003': ['PLANT006 - Assembly Unit', 'PLANT007 - Packaging Unit', 'PLANT008 - Warehouse']
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize default data
    initializeDefaultUsers();
    initializeSampleVisitors();
    
    // Skip login for demo - directly show main app
    showMainApp();
    
    // Set up event listeners
    setupEventListeners();
    
    // Show dashboard by default
    showTab('dashboard');
    
    // Update dashboard stats
    updateDashboardStats();
    
    // Populate tables
    populateRecentVisitorsTable();
    populateVisitorsTable();
    populateApprovalsTable();
    populateUsersTable();
}

function initializeDefaultUsers() {
    users = [
        {
            empId: 'ADMIN001',
            password: 'admin123',
            name: 'Admin User',
            department: 'Administration',
            mobile: '9876543210',
            role: 'Administrator',
            status: 'Active'
        },
        {
            empId: 'EMP001',
            password: 'emp123',
            name: 'John Manager',
            department: 'Operations',
            mobile: '9876543211',
            role: 'Manager',
            status: 'Active'
        },
        {
            empId: 'EMP002',
            password: 'emp123',
            name: 'Sarah Wilson',
            department: 'Security',
            mobile: '9876543212',
            role: 'Security',
            status: 'Active'
        }
    ];
    
    // Set current user as admin for demo
    currentUser = users[0];
    updateUserInfo();
}

function initializeSampleVisitors() {
    const now = new Date();
    const today = new Date();
    today.setHours(9, 0, 0, 0);
    
    visitors = [
        {
            id: 'V' + (visitorIdCounter++),
            visitorName: 'Rajesh Kumar',
            visitorMobile: '9876543210',
            visitorDesignation: 'Sales Manager',
            siteCode: 'SITE001',
            plantCode: 'PLANT001',
            visitorCategory: 'CLIENT',
            purpose: 'MEETING',
            noOfPersons: 1,
            persons: [{name: 'Rajesh Kumar', mobile: '9876543210', idType: 'Aadhar', idNumber: '1234-5678-9012'}],
            representing: 'Tech Solutions Pvt Ltd',
            employeeToMeet: 'John Manager',
            employeeId: 'EMP001',
            vehicleNo: 'GJ01AB1234',
            address1: '123 Business Park',
            address2: 'Ahmedabad',
            cardNo: 'C001',
            luggage: 'Laptop bag',
            purposeDetails: 'Quarterly business review meeting',
            entryTime: new Date(today.getTime() + Math.random() * 8 * 60 * 60 * 1000),
            exitTime: null,
            status: 'approved',
            approvedBy: 'EMP001',
            approvalTime: new Date(today.getTime() + Math.random() * 8 * 60 * 60 * 1000)
        },
        {
            id: 'V' + (visitorIdCounter++),
            visitorName: 'Priya Sharma',
            visitorMobile: '9876543211',
            visitorDesignation: 'Engineer',
            siteCode: 'SITE002',
            plantCode: 'PLANT003',
            visitorCategory: 'VENDOR',
            purpose: 'MAINTENANCE',
            noOfPersons: 2,
            persons: [
                {name: 'Priya Sharma', mobile: '9876543211', idType: 'Aadhar', idNumber: '2345-6789-0123'},
                {name: 'Amit Patel', mobile: '9876543212', idType: 'PAN', idNumber: 'ABCDE1234F'}
            ],
            representing: 'Industrial Services Ltd',
            employeeToMeet: 'Sarah Wilson',
            employeeId: 'EMP002',
            vehicleNo: 'GJ02CD5678',
            address1: '456 Industrial Area',
            address2: 'Vadodara',
            cardNo: 'C002',
            luggage: 'Tool kit',
            purposeDetails: 'Equipment maintenance and inspection',
            entryTime: new Date(today.getTime() + Math.random() * 8 * 60 * 60 * 1000),
            exitTime: null,
            status: 'pending',
            approvedBy: null,
            approvalTime: null
        }
    ];
}

function setupEventListeners() {
    // Form submissions
    document.getElementById('visitorForm').addEventListener('submit', handleVisitorRegistration);
    
    // Site code change
    document.getElementById('siteCode').addEventListener('change', updatePlantOptions);
    
    // Number of persons change
    document.getElementById('noOfPersons').addEventListener('change', updatePersonDetails);
    
    // Search functionality
    document.getElementById('visitorSearch').addEventListener('input', filterVisitors);
    
    // Initialize person details
    updatePersonDetails();
}

function showMainApp() {
    // Remove hidden class from main app
    const mainApp = document.getElementById('mainApp');
    if (mainApp.classList.contains('hidden')) {
        mainApp.classList.remove('hidden');
    }
}

function updateUserInfo() {
    if (currentUser) {
        document.getElementById('userAvatar').textContent = currentUser.name.charAt(0).toUpperCase();
        document.getElementById('userName').textContent = currentUser.name;
        document.getElementById('userRole').textContent = currentUser.role;
        
        // Hide users tab for non-admin users
        if (currentUser.role !== 'Administrator') {
            document.getElementById('usersTab').style.display = 'none';
        }
    }
}

function showTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(tab => tab.classList.add('hidden'));
    
    // Remove active class from all nav tabs
    const navTabs = document.querySelectorAll('.nav-tab');
    navTabs.forEach(tab => tab.classList.remove('active'));
    
    // Show selected tab content
    document.getElementById(tabName).classList.remove('hidden');
    
    // Add active class to clicked nav tab
    event.target.classList.add('active');
    
    // Update data based on selected tab
    switch(tabName) {
        case 'dashboard':
            updateDashboardStats();
            populateRecentVisitorsTable();
            break;
        case 'visitors':
            populateVisitorsTable();
            break;
        case 'approval':
            populateApprovalsTable();
            break;
        case 'users':
            populateUsersTable();
            break;
    }
}

function updatePlantOptions() {
    const siteCode = document.getElementById('siteCode').value;
    const plantSelect = document.getElementById('plantCode');
    
    // Clear existing options
    plantSelect.innerHTML = '<option value="">Select Plant</option>';
    
    if (siteCode && sitePlantMapping[siteCode]) {
        sitePlantMapping[siteCode].forEach(plant => {
            const option = document.createElement('option');
            option.value = plant.split(' - ')[0];
            option.textContent = plant;
            plantSelect.appendChild(option);
        });
    }
}

function updatePersonDetails() {
    const noOfPersons = parseInt(document.getElementById('noOfPersons').value) || 1;
    const container = document.getElementById('personDetailsContainer');
    
    container.innerHTML = '';
    
    for (let i = 0; i < noOfPersons; i++) {
        const personDiv = document.createElement('div');
        personDiv.className = 'person-details';
        personDiv.innerHTML = `
            <div class="person-header">
                <h4><i class="fas fa-user"></i> Person ${i + 1}</h4>
            </div>
            <div class="form-grid">
                <div class="form-group">
                    <label><i class="fas fa-user"></i> Full Name *</label>
                    <input type="text" name="person_${i}_name" required>
                </div>
                <div class="form-group">
                    <label><i class="fas fa-phone"></i> Mobile Number *</label>
                    <input type="tel" name="person_${i}_mobile" pattern="[0-9]{10}" required>
                </div>
                <div class="form-group">
                    <label><i class="fas fa-id-card"></i> ID Type *</label>
                    <select name="person_${i}_idType" required>
                        <option value="">Select ID Type</option>
                        <option value="Aadhar">Aadhar Card</option>
                        <option value="PAN">PAN Card</option>
                        <option value="Passport">Passport</option>
                        <option value="Driving License">Driving License</option>
                        <option value="Voter ID">Voter ID</option>
                    </select>
                </div>
                <div class="form-group">
                    <label><i class="fas fa-hashtag"></i> ID Number *</label>
                    <input type="text" name="person_${i}_idNumber" required>
                </div>
            </div>
        `;
        container.appendChild(personDiv);
    }
}

function handleVisitorRegistration(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const noOfPersons = parseInt(formData.get('noOfPersons'));
    
    // Collect person details
    const persons = [];
    for (let i = 0; i < noOfPersons; i++) {
        persons.push({
            name: formData.get(`person_${i}_name`),
            mobile: formData.get(`person_${i}_mobile`),
            idType: formData.get(`person_${i}_idType`),
            idNumber: formData.get(`person_${i}_idNumber`)
        });
    }
    
    // Create visitor object
    const visitor = {
        id: 'V' + (visitorIdCounter++),
        visitorName: formData.get('visitorName'),
        visitorMobile: formData.get('visitorMobile'),
        visitorDesignation: formData.get('visitorDesignation'),
        siteCode: formData.get('siteCode'),
        plantCode: formData.get('plantCode'),
        visitorCategory: formData.get('visitorCategory'),
        purpose: formData.get('purpose'),
        noOfPersons: noOfPersons,
        persons: persons,
        representing: formData.get('representing'),
        employeeToMeet: formData.get('employeeToMeet'),
        employeeId: formData.get('employeeId'),
        vehicleNo: formData.get('vehicleNo'),
        address1: formData.get('address1'),
        address2: formData.get('address2'),
        cardNo: formData.get('cardNo'),
        luggage: formData.get('luggage'),
        purposeDetails: formData.get('purposeDetails'),
        entryTime: new Date(),
        exitTime: null,
        status: 'pending',
        approvedBy: null,
        approvalTime: null
    };
    
    // Add to visitors array
    visitors.push(visitor);
    
    // Show success message
    alert(`Visitor registered successfully! ID: ${visitor.id}`);
    
    // Reset form
    resetForm();
    
    // Update dashboard if on dashboard tab
    updateDashboardStats();
}

function resetForm() {
    document.getElementById('visitorForm').reset();
    updatePersonDetails();
    document.getElementById('plantCode').innerHTML = '<option value="">Select Plant</option>';
}

function updateDashboardStats() {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    const todayVisitors = visitors.filter(v => {
        const entryDate = new Date(v.entryTime);
        entryDate.setHours(0, 0, 0, 0);
        return entryDate.getTime() === today.getTime();
    });
    
    const pendingApprovals = visitors.filter(v => v.status === 'pending').length;
    const activeVisitors = visitors.filter(v => v.status === 'approved' && !v.exitTime).length;
    const checkedOut = visitors.filter(v => v.exitTime && new Date(v.exitTime) >= today).length;
    
    document.getElementById('totalVisitors').textContent = todayVisitors.length;
    document.getElementById('pendingApprovals').textContent = pendingApprovals;
    document.getElementById('activeVisitors').textContent = activeVisitors;
    document.getElementById('checkedOut').textContent = checkedOut;
}

function populateRecentVisitorsTable() {
    const tbody = document.getElementById('recentVisitorsTable');
    tbody.innerHTML = '';
    
    // Get recent visitors (last 10)
    const recentVisitors = visitors.slice(-10).reverse();
    
    recentVisitors.forEach(visitor => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${visitor.visitorName}</td>
            <td>${visitor.visitorMobile}</td>
            <td>${visitor.representing}</td>
            <td>${formatDateTime(visitor.entryTime)}</td>
            <td><span class="status-badge status-${visitor.status}">${visitor.status}</span></td>
            <td>
                <button class="btn btn-secondary" onclick="viewVisitorDetails('${visitor.id}')">
                    <i class="fas fa-eye"></i> View
                </button>
                ${visitor.status === 'approved' && !visitor.exitTime ? 
                    `<button class="btn btn-warning" onclick="checkoutVisitor('${visitor.id}')">
                        <i class="fas fa-sign-out-alt"></i> Checkout
                    </button>` : ''}
            </td>
        `;
        tbody.appendChild(row);
    });
}

function populateVisitorsTable() {
    const tbody = document.getElementById('visitorsTable');
    tbody.innerHTML = '';
    
    visitors.forEach(visitor => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${visitor.id}</td>
            <td>${visitor.visitorName}</td>
            <td>${visitor.visitorMobile}</td>
            <td>${visitor.representing}</td>
            <td>${formatDateTime(visitor.entryTime)}</td>
            <td><span class="status-badge status-${visitor.status}">${visitor.status}</span></td>
            <td>
                <button class="btn btn-secondary" onclick="viewVisitorDetails('${visitor.id}')">
                    <i class="fas fa-eye"></i> View
                </button>
                ${visitor.status === 'approved' && !visitor.exitTime ? 
                    `<button class="btn btn-warning" onclick="checkoutVisitor('${visitor.id}')">
                        <i class="fas fa-sign-out-alt"></i> Checkout
                    </button>` : ''}
            </td>
        `;
        tbody.appendChild(row);
    });
}

function populateApprovalsTable() {
    const tbody = document.getElementById('approvalsTable');
    tbody.innerHTML = '';
    
    const pendingVisitors = visitors.filter(v => v.status === 'pending');
    
    pendingVisitors.forEach(visitor => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${visitor.id}</td>
            <td>${visitor.visitorName}</td>
            <td>${visitor.visitorMobile}</td>
            <td>${visitor.representing}</td>
            <td>${visitor.purpose}</td>
            <td>${formatDateTime(visitor.entryTime)}</td>
            <td>
                <button class="btn btn-success" onclick="approveVisitor('${visitor.id}')">
                    <i class="fas fa-check"></i> Approve
                </button>
                <button class="btn btn-danger" onclick="rejectVisitor('${visitor.id}')">
                    <i class="fas fa-times"></i> Reject
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function populateUsersTable() {
    const tbody = document.getElementById('usersTable');
    tbody.innerHTML = '';
    
    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.empId}</td>
            <td>${user.name}</td>
            <td>${user.department}</td>
            <td>${user.mobile}</td>
            <td>${user.role}</td>
            <td><span class="status-badge ${user.status === 'Active' ? 'status-approved' : 'status-rejected'}">${user.status}</span></td>
            <td>
                <button class="btn btn-secondary" onclick="editUser('${user.empId}')">
                    <i class="fas fa-edit"></i> Edit
                </button>
                <button class="btn btn-danger" onclick="deleteUser('${user.empId}')">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function filterVisitors() {
    const searchTerm = document.getElementById('visitorSearch').value.toLowerCase();
    const tbody = document.getElementById('visitorsTable');
    const rows = tbody.getElementsByTagName('tr');
    
    Array.from(rows).forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

function approveVisitor(visitorId) {
    const visitor = visitors.find(v => v.id === visitorId);
    if (visitor) {
        visitor.status = 'approved';
        visitor.approvedBy = currentUser.empId;
        visitor.approvalTime = new Date();
        
        alert(`Visitor ${visitor.visitorName} has been approved!`);
        populateApprovalsTable();
        updateDashboardStats();
    }
}

function rejectVisitor(visitorId) {
    const visitor = visitors.find(v => v.id === visitorId);
    if (visitor && confirm('Are you sure you want to reject this visitor?')) {
        visitor.status = 'rejected';
        visitor.approvedBy = currentUser.empId;
        visitor.approvalTime = new Date();
        
        alert(`Visitor ${visitor.visitorName} has been rejected!`);
        populateApprovalsTable();
        updateDashboardStats();
    }
}

function checkoutVisitor(visitorId) {
    const visitor = visitors.find(v => v.id === visitorId);
    if (visitor && confirm('Checkout this visitor?')) {
        visitor.exitTime = new Date();
        
        alert(`Visitor ${visitor.visitorName} has been checked out!`);
        populateVisitorsTable();
        populateRecentVisitorsTable();
        updateDashboardStats();
    }
}

function viewVisitorDetails(visitorId) {
    const visitor = visitors.find(v => v.id === visitorId);
    if (visitor) {
        let personsDetails = visitor.persons.map((person, index) => 
            `Person ${index + 1}: ${person.name} (${person.mobile}) - ${person.idType}: ${person.idNumber}`
        ).join('\n');
        
        alert(`Visitor Details:
ID: ${visitor.id}
Name: ${visitor.visitorName}
Mobile: ${visitor.visitorMobile}
Company: ${visitor.representing}
Purpose: ${visitor.purpose}
Employee to Meet: ${visitor.employeeToMeet}
Entry Time: ${formatDateTime(visitor.entryTime)}
Status: ${visitor.status}
${visitor.exitTime ? 'Exit Time: ' + formatDateTime(visitor.exitTime) : ''}

Persons:
${personsDetails}

Address: ${visitor.address1}, ${visitor.address2}
Vehicle: ${visitor.vehicleNo || 'N/A'}
Luggage: ${visitor.luggage || 'None'}
Purpose Details: ${visitor.purposeDetails || 'N/A'}`);
    }
}

function formatDateTime(date) {
    return new Date(date).toLocaleString('en-IN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        currentUser = null;
        // In a real application, you would redirect to login page
        alert('Logged out successfully!');
        location.reload();
    }
}

// User management functions
function showCreateUserModal() {
    const name = prompt('Enter user name:');
    const empId = prompt('Enter employee ID:');
    const department = prompt('Enter department:');
    const mobile = prompt('Enter mobile number:');
    const role = prompt('Enter role (Administrator/Manager/Security):');
    const password = prompt('Enter password:');
    
    if (name && empId && department && mobile && role && password) {
        const newUser = {
            empId: empId,
            password: password,
            name: name,
            department: department,
            mobile: mobile,
            role: role,
            status: 'Active'
        };
        
        users.push(newUser);
        populateUsersTable();
        alert('User created successfully!');
    }
}

function editUser(empId) {
    const user = users.find(u => u.empId === empId);
    if (user) {
        const newName = prompt('Enter new name:', user.name);
        const newDepartment = prompt('Enter new department:', user.department);
        const newMobile = prompt('Enter new mobile:', user.mobile);
        const newRole = prompt('Enter new role:', user.role);
        
        if (newName) user.name = newName;
        if (newDepartment) user.department = newDepartment;
        if (newMobile) user.mobile = newMobile;
        if (newRole) user.role = newRole;
        
        populateUsersTable();
        alert('User updated successfully!');
    }
}

function deleteUser(empId) {
    if (confirm('Are you sure you want to delete this user?')) {
        const index = users.findIndex(u => u.empId === empId);
        if (index > -1) {
            users.splice(index, 1);
            populateUsersTable();
            alert('User deleted successfully!');
        }
    }
}