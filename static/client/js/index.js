// ====== Global Variables ======

// Dashboard data from template
let dashboardData = window.dashboardData || {};

// Profile data tracking
let currentSkills = [];
let currentTools = [];

// WebSocket variables
let socket = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
let userId = document.getElementById('user_id_for_socket')?.textContent.trim();

// Community WebSocket variables
let communitySocket = null;
let currentUserId = document.getElementById('user_id_for_socket')?.textContent.trim();

// ====== Initialization ======

document.addEventListener('DOMContentLoaded', function() {
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    
    // Initialize WebSocket connection
    initializeWebSocket();
    
    // Load dashboard data
    if (Object.keys(dashboardData).length === 0) {
        // If no initial data, fetch from server
        loadDashboardData();
    } else {
        // Use the data passed from template
        updateDashboardUI(dashboardData);
    }
    
    // Initialize event listeners
    initializeEventListeners();
});

// ====== WebSocket Functions ======

function initializeWebSocket() {
    if (!userId) {
        console.error('User ID not found for WebSocket connection');
        return;
    }
    
    try {
        // Determine WebSocket URL based on current location
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${userId}`;
        
        socket = new WebSocket(wsUrl);
        
        socket.onopen = function(event) {
            console.log('WebSocket connected successfully');
            updateConnectionStatus('connected', 'Connected');
            reconnectAttempts = 0;
        };
        
        socket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            console.log('WebSocket message received:', data);
            
            if (data.type === 'notification') {
                handleNewNotification(data.notification);
            } else if (data.type === 'connected_users') {
                console.log('Connected users:', data.users);
            }
        };
        
        socket.onclose = function(event) {
            console.log('WebSocket disconnected:', event);
            updateConnectionStatus('disconnected', 'Disconnected');
            
            // Attempt to reconnect
            if (reconnectAttempts < maxReconnectAttempts) {
                setTimeout(() => {
                    reconnectAttempts++;
                    console.log(`Attempting to reconnect... (${reconnectAttempts}/${maxReconnectAttempts})`);
                    initializeWebSocket();
                }, 3000);
            }
        };
        
        socket.onerror = function(error) {
            console.error('WebSocket error:', error);
            updateConnectionStatus('disconnected', 'Connection Error');
        };
        
    } catch (error) {
        console.error('Error initializing WebSocket:', error);
        updateConnectionStatus('disconnected', 'Connection Failed');
    }
}

function updateConnectionStatus(status, text) {
    const indicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    
    if (indicator && statusText) {
        indicator.className = 'status-indicator';
        indicator.classList.add(`status-${status}`);
        statusText.textContent = text;
    }
}

// ====== Notification Functions ======

function handleNewNotification(notificationData) {
    const [message, status, timestamp] = notificationData;
    
    // Update notification badge
    updateNotificationBadge();
    
    // Show toast notification
    showToast(message, 'success');
    
    // If notification modal is open, update it
    const modal = document.getElementById('notificationModal');
    if (modal && modal.classList.contains('active')) {
        addNotificationToModal(message, status);
    }
    
    // Play notification sound (optional)
    playNotificationSound();
}

function addNotificationToModal(message, status) {
    const notificationBody = document.getElementById('notificationBody');
    const emptyState = notificationBody ? notificationBody.querySelector('.notification-empty') : null;
    
    if (!notificationBody) return;
    
    // Remove empty state if it exists
    if (emptyState) {
        emptyState.remove();
    }
    
    // Create new notification element
    const notificationElement = document.createElement('div');
    notificationElement.className = `notification-item ${status === 0 ? 'notification-unread' : ''}`;
    notificationElement.innerHTML = `
        <div class="notification-icon-container ${status === 0 ? 'notification-warning' : 'notification-success'}">
            <i class="fas ${status === 0 ? 'fa-exclamation' : 'fa-check'}"></i>
        </div>
        <div class="notification-content">
            <div class="notification-message">${message}</div>
        </div>
    `;
    
    // Add to the top of the list
    notificationBody.insertBefore(notificationElement, notificationBody.firstChild);
}

function updateNotificationBadge() {
    const badge = document.getElementById('notificationBadge');
    if (badge) {
        let currentCount = parseInt(badge.textContent) || 0;
        badge.textContent = currentCount + 1;
    }
}

function resetNotificationBadge() {
    const badge = document.getElementById('notificationBadge');
    if (badge) {
        badge.textContent = '0';
    }
}

function playNotificationSound() {
    // Create a simple notification sound
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
    } catch (error) {
        console.log('Audio context not supported');
    }
}

function sendTestNotification() {
    if (socket && socket.readyState === WebSocket.OPEN) {
        const testNotification = ["Test notification from WebSocket", 0, new Date().toISOString()];
        socket.send(JSON.stringify({
            type: 'test_notification',
            notification: testNotification
        }));
    }
}

// ====== Profile Modal Functions ======

function openProfileModal() {
    const overlay = document.getElementById('profileModalOverlay');
    const modal = document.getElementById('profileModal');
    
    if (overlay) overlay.style.display = 'block';
    if (modal) modal.classList.add('active');
    
    // Load profile data when opening modal
    loadProfileData();
}

function closeProfileModal() {
    const overlay = document.getElementById('profileModalOverlay');
    const modal = document.getElementById('profileModal');
    
    if (overlay) overlay.style.display = 'none';
    if (modal) modal.classList.remove('active');
}

function toggleEdit(section) {
    const display = document.getElementById(`${section}Display`);
    const edit = document.getElementById(`${section}Edit`);
    const saveContainer = document.getElementById(`${section}SaveContainer`);
    
    if (!display || !edit || !saveContainer) return;
    
    if (display.style.display === 'none') {
        // Switching from edit to display mode
        display.style.display = 'flex';
        edit.style.display = 'none';
        saveContainer.style.display = 'none';
    } else {
        // Switching from display to edit mode
        display.style.display = 'none';
        edit.style.display = 'flex';
        saveContainer.style.display = 'block';
        
        // Initialize the editable fields with current data
        if (section === 'skills') {
            initializeEditableFields('skills', currentSkills);
        } else if (section === 'tools') {
            initializeEditableFields('tools', currentTools);
        }
    }
}

function initializeEditableFields(section, data) {
    const editContainer = document.getElementById(`${section}Edit`);
    if (!editContainer) return;
    
    // Clear existing inputs except the add button
    editContainer.innerHTML = '';
    
    // Add input fields for each item
    data.forEach(item => {
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'editable-input';
        input.value = item;
        input.placeholder = `Add ${section === 'skills' ? 'skill' : 'tool'}`;
        editContainer.appendChild(input);
    });
    
    // Add the add button
    const newAddButton = document.createElement('button');
    newAddButton.className = 'add-tag-btn';
    newAddButton.textContent = '+ Add';
    newAddButton.onclick = function() { addNewInput(section); };
    editContainer.appendChild(newAddButton);
}

function addNewInput(section) {
    const editContainer = document.getElementById(`${section}Edit`);
    if (!editContainer) return;
    
    const addButton = editContainer.querySelector('.add-tag-btn');
    
    // Create new input field
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'editable-input';
    input.placeholder = `Add ${section === 'skills' ? 'skill' : 'tool'}`;
    
    // Insert before the add button
    editContainer.insertBefore(input, addButton);
}

// ====== Navigation Functions ======

function showSection(sectionId, title) {
    // Hide all sections
    const sections = ["dashboardContent", "projectsSection", "tasksSection", "communitySection"];
    sections.forEach(id => {
        const section = document.getElementById(id);
        if (section) section.style.display = "none";
    });
    
    // Show selected section
    const selectedSection = document.getElementById(sectionId);
    const pageTitle = document.getElementById("pageTitle");
    
    if (selectedSection) selectedSection.style.display = "block";
    if (pageTitle) pageTitle.textContent = title;
    
    // Update active menu item
    document.querySelectorAll('.sidebar-menu li').forEach(item => {
        item.classList.remove('active');
    });
    
    // Activate the corresponding menu item
    const buttonMap = {
        "dashboardContent": "dashboardBtn",
        "projectsSection": "projectsBtn",
        "tasksSection": "tasksBtn",
        "communitySection": "communityBtn"
    };
    
    const activeButtonId = buttonMap[sectionId];
    if (activeButtonId) {
        const activeButton = document.getElementById(activeButtonId);
        if (activeButton) activeButton.classList.add('active');
    }
    
    // Load content for the selected section
    if (sectionId === "dashboardContent") {
        loadDashboardData();
    } else if (sectionId === "projectsSection") {
        loadProjects();
    } else if (sectionId === "tasksSection") {
        loadTasks();
    } else if (sectionId === "communitySection") {
        loadCommunityChat();
        initializeCommunityWebSocket();
    }
}

// ====== Dashboard Functions ======

async function loadDashboardData() {
    try {
        // Send POST request to FastAPI server
        const response = await fetch('/client-dashboard', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ x: 'any string value' })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Received dashboard data:', data);
        
        // Update the dashboard UI with received data
        updateDashboardUI(data);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

function updateDashboardUI(data) {
    // Update card values
    const totalProjects = document.getElementById('totalProjects');
    const completedProjects = document.getElementById('completedProjects');
    const totalTasks = document.getElementById('totalTasks');
    const completedTasks = document.getElementById('completedTasks');
    
    if (totalProjects) totalProjects.textContent = data['total assigned projects'] || 0;
    if (completedProjects) completedProjects.textContent = data['completed projects'] || 0;
    if (totalTasks) totalTasks.textContent = data['total assigned tasks'] || data['total assigned task'] || 0;
    if (completedTasks) completedTasks.textContent = data['completed tasks'] || data['completed task'] || 0;
    
    // Update recent projects table
    const recentProjects = data['recent projects'] || [];
    const projectsTable = document.getElementById('recentProjectsTable');
    
    if (projectsTable) {
        if (recentProjects.length > 0) {
            projectsTable.innerHTML = recentProjects.slice(0, 3).map(project => `
                <tr>
                    <td>${project.project_name || 'N/A'}</td>
                    <td><span class="status ${getStatusClass(project.Status)}">${getStatusText(project.Status)}</span></td>
                    <td>${project.due_date || 'N/A'}</td>
                </tr>
            `).join('');
        } else {
            projectsTable.innerHTML = '<tr><td colspan="3" style="text-align: center;">No recent projects</td></tr>';
        }
    }
    
    // Update recent tasks table
    const recentTasks = data['recent tasks'] || data['recent task'] || [];
    const tasksTable = document.getElementById('recentTasksTable');
    
    if (tasksTable) {
        if (recentTasks.length > 0) {
            tasksTable.innerHTML = recentTasks.slice(0, 3).map(task => `
                <tr>
                    <td>${task.task_name || 'N/A'}</td>
                    <td><span class="status ${getStatusClass(task.Status)}">${getStatusText(task.Status)}</span></td>
                    <td>${task.due_date || 'N/A'}</td>
                </tr>
            `).join('');
        } else {
            tasksTable.innerHTML = '<tr><td colspan="3" style="text-align: center;">No recent tasks</td></tr>';
        }
    }
}

function getStatusClass(status) {
    switch(status) {
        case 1: return 'status-completed';
        case 0: return 'status-ongoing';
        default: return 'status-ongoing';
    }
}

function getStatusText(status) {
    switch(status) {
        case 1: return 'Completed';
        case 0: return 'Ongoing';
        default: return 'Ongoing';
    }
}

// ====== Checkbox Functions ======

function toggleCheckbox(checkbox) {
    // Store the current state before toggling
    const wasChecked = checkbox.classList.contains('checked');
    
    // If this is a project completion checkbox, send update to server
    if (checkbox.classList.contains('project-completion-checkbox')) {
        const projectId = checkbox.getAttribute('data-project-id');
        const newStatus = wasChecked ? 0 : 1; // Toggle the status
        
        // Update the checkbox visually immediately for better UX
        checkbox.classList.toggle('checked');
        
        updateProjectStatus(projectId, newStatus, checkbox, wasChecked);
    } 
    // If this is a task completion checkbox, send update to server
    else if (checkbox.classList.contains('task-completion-checkbox')) {
        const taskId = checkbox.getAttribute('data-task-id');
        const newStatus = wasChecked ? 0 : 1; // Toggle the status
        
        // Update the checkbox visually immediately for better UX
        checkbox.classList.toggle('checked');
        
        updateTaskStatus(taskId, newStatus, checkbox, wasChecked);
    } else {
        // For regular checkboxes, just toggle
        checkbox.classList.toggle('checked');
    }
}

async function updateProjectStatus(projectId, status, checkbox, previousState) {
    try {
        const response = await fetch('/project-checkbox', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                project_id: projectId,
                status: status
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Project status updated:', result);
        
        // Update the status badge
        const projectCard = document.querySelector(`[data-project-id="${projectId}"]`)?.closest('.project-card');
        if (projectCard) {
            const statusBadge = projectCard.querySelector('.status');
            if (statusBadge) {
                if (status === 1) {
                    statusBadge.className = 'status status-completed';
                    statusBadge.textContent = 'Completed';
                } else {
                    statusBadge.className = 'status status-ongoing';
                    statusBadge.textContent = 'Ongoing';
                }
            }
        }
        
    } catch (error) {
        console.error('Error updating project status:', error);
        
        // Revert the checkbox to its previous state
        if (previousState) {
            checkbox.classList.add('checked');
        } else {
            checkbox.classList.remove('checked');
        }
        
        alert('Error updating project status. Please try again.');
    }
}

async function updateTaskStatus(taskId, status, checkbox, previousState) {
    try {
        const response = await fetch('/task-checkbox', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                task_id: taskId,
                status: status
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Task status updated:', result);
        
        // Update the status badge
        const taskCard = document.querySelector(`[data-task-id="${taskId}"]`)?.closest('.task-card');
        if (taskCard) {
            const statusBadge = taskCard.querySelector('.status');
            if (statusBadge) {
                if (status === 1) {
                    statusBadge.className = 'status status-completed';
                    statusBadge.textContent = 'Completed';
                } else {
                    statusBadge.className = 'status status-ongoing';
                    statusBadge.textContent = 'Ongoing';
                }
            }
        }
        
    } catch (error) {
        console.error('Error updating task status:', error);
        
        // Revert the checkbox to its previous state
        if (previousState) {
            checkbox.classList.add('checked');
        } else {
            checkbox.classList.remove('checked');
        }
        
        alert('Error updating task status. Please try again.');
    }
}

// ====== Component Functions ======

function toggleComponentDetails(component) {
    const details = component.nextElementSibling;
    if (details) {
        if (details.style.display === "block") {
            details.style.display = "none";
        } else {
            details.style.display = "block";
        }
    }
}

// ====== Projects Functions ======

async function loadProjects() {
    const projectsContainer = document.getElementById('projectsContainer');
    const loadingSpinner = document.getElementById('projectsLoading');
    
    if (!projectsContainer || !loadingSpinner) return;
    
    // Show loading spinner
    projectsContainer.innerHTML = '';
    loadingSpinner.style.display = 'block';
    
    try {
        // Send POST request to FastAPI server
        const response = await fetch('/client-projects', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ x: 'any string value' })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const projects = await response.json();
        console.log('Received projects:', projects);
        
        // Hide loading spinner
        loadingSpinner.style.display = 'none';
        
        // Render projects
        let projectsArray = projects;
        if (projects && projects.projects) {
            projectsArray = projects.projects;
        }
        
        if (projectsArray && projectsArray.length > 0) {
            projectsContainer.innerHTML = projectsArray.map(project => createProjectCard(project)).join('');
        } else {
            projectsContainer.innerHTML = '<p>No projects found.</p>';
        }
        
    } catch (error) {
        console.error('Error loading projects:', error);
        loadingSpinner.style.display = 'none';
        projectsContainer.innerHTML = '<p>Error loading projects. Please try again.</p>';
    }
}

function createProjectCard(project) {
    const statusClass = project.Status === 1 ? 'status-completed' : 'status-ongoing';
    const statusText = project.Status === 1 ? 'Completed' : 'Ongoing';
    const isChecked = project.Status === 1 ? 'checked' : '';
    
    // Get assigned members usernames
    const assignedMembers = project.assigned_member ? 
        project.assigned_member.map(member => member[1]).join(', ') : '';
    
    // Get project manager username
    const projectManager = project.project_manager && project.project_manager.length > 0 ? 
        project.project_manager[0][1] : 'Not assigned';
    
    // Get project ID
    let projectId = project._id;
    if (projectId && typeof projectId === 'object' && projectId.$oid) {
        projectId = projectId.$oid;
    }
    
    // Create components HTML
    let componentsHTML = '';
    if (project.components && Object.keys(project.components).length > 0) {
        componentsHTML = Object.entries(project.components).map(([heading, details]) => `
            <div class="phase" onclick="toggleComponentDetails(this)">${heading}</div>
            <div class="sub-phases">
                <p>${details}</p>
            </div>
        `).join('');
    }
    
    return `
        <div class="project-card">
            <div class="project-header">
                <h3>${project.project_name || 'Unnamed Project'}</h3>
                <span class="status ${statusClass}">${statusText}</span>
            </div>
            <div class="project-meta">Initiated: ${project.initiated_date || 'N/A'} | Due: ${project.due_date || 'N/A'} | Team: ${project.team || 'N/A'} | Manager: ${projectManager}</div>
            <div class="project-meta">Assigned Members: ${assignedMembers || 'None'}</div>
            ${componentsHTML}
            <div class="checkbox-container project-checkbox">
                <div class="custom-checkbox project-completion-checkbox ${isChecked}" 
                     onclick="toggleCheckbox(this)" 
                     data-project-id="${projectId || ''}"></div>
                <span class="checkbox-label">Mark project as completed</span>
            </div>
        </div>
    `;
}

// ====== Tasks Functions ======

async function loadTasks() {
    const tasksContainer = document.getElementById('tasksContainer');
    const loadingSpinner = document.getElementById('tasksLoading');
    
    if (!tasksContainer || !loadingSpinner) return;
    
    // Show loading spinner
    tasksContainer.innerHTML = '';
    loadingSpinner.style.display = 'block';
    
    try {
        // Send POST request to FastAPI server
        const response = await fetch('/client-tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ x: 'any string value' })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const tasks = await response.json();
        console.log('Received tasks:', tasks);
        
        // Hide loading spinner
        loadingSpinner.style.display = 'none';
        
        // Render tasks
        let tasksArray = tasks;
        if (tasks && tasks.tasks) {
            tasksArray = tasks.tasks;
        }
        
        if (tasksArray && tasksArray.length > 0) {
            tasksContainer.innerHTML = tasksArray.map(task => createTaskCard(task)).join('');
        } else {
            tasksContainer.innerHTML = '<p>No tasks found.</p>';
        }
        
    } catch (error) {
        console.error('Error loading tasks:', error);
        loadingSpinner.style.display = 'none';
        tasksContainer.innerHTML = '<p>Error loading tasks. Please try again.</p>';
    }
}

function createTaskCard(task) {
    const statusClass = task.Status === 1 ? 'status-completed' : 'status-ongoing';
    const statusText = task.Status === 1 ? 'Completed' : 'Ongoing';
    const isChecked = task.Status === 1 ? 'checked' : '';
    
    // Get assigned members usernames
    const assignedMembers = task.assigned_member ? 
        task.assigned_member.map(member => member[1]).join(', ') : '';
    
    // Get task ID
    let taskId = task._id;
    if (taskId && typeof taskId === 'object' && taskId.$oid) {
        taskId = taskId.$oid;
    }
    
    return `
        <div class="task-card">
            <div class="task-header">
                <h3 class="task-title">${task.task_name || 'Unnamed Task'}</h3>
                <span class="status ${statusClass}">${statusText}</span>
            </div>
            <div class="task-meta">
                <div class="task-meta-item">
                    <i class="fas fa-calendar-plus"></i>
                    <span>Initiated: ${task.initiated_date || 'N/A'}</span>
                </div>
                <div class="task-meta-item">
                    <i class="fas fa-calendar-check"></i>
                    <span>Due: ${task.due_date || 'N/A'}</span>
                </div>
            </div>
            <div class="task-description">
                ${task.desc || 'No description provided'}
            </div>
            <div class="assigned-members">
                <span style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">Assigned to: ${assignedMembers || 'None'}</span>
            </div>
            <div class="checkbox-container" style="margin-top: 15px;">
                <div class="custom-checkbox task-completion-checkbox ${isChecked}" 
                     onclick="toggleCheckbox(this)" 
                     data-task-id="${taskId || ''}"></div>
                <span class="checkbox-label">Completed</span>
            </div>
        </div>
    `;
}

// ====== Profile Functions ======

async function loadProfileData() {
    try {
        // Send POST request to FastAPI server
        const response = await fetch('/client-profile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ x: 'any string value' })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const profileData = await response.json();
        console.log('Received profile data:', profileData);
        
        // Update the profile modal with received data
        updateProfileModal(profileData);
        
    } catch (error) {
        console.error('Error loading profile data:', error);
    }
}

function updateProfileModal(data) {
    // Update email
    const profileEmail = document.getElementById('profileEmail');
    if (profileEmail && data.email) {
        profileEmail.textContent = data.email;
    }
    
    // Update team
    const teamContainer = document.getElementById('teamContainer');
    if (teamContainer && data.team) {
        teamContainer.innerHTML = `<span class="tag">${data.team}</span>`;
    }
    
    // Update skills
    const skillsDisplay = document.getElementById('skillsDisplay');
    if (skillsDisplay) {
        if (data.skills && data.skills.length > 0) {
            currentSkills = [...data.skills];
            skillsDisplay.innerHTML = data.skills.map(skill => `
                <span class="tag">${skill}</span>
            `).join('');
        } else {
            currentSkills = [];
            skillsDisplay.innerHTML = '<span>No skills added yet</span>';
        }
    }
    
    // Update tools & platform
    const toolsDisplay = document.getElementById('toolsDisplay');
    if (toolsDisplay) {
        if (data.tnp && data.tnp.length > 0) {
            currentTools = [...data.tnp];
            toolsDisplay.innerHTML = data.tnp.map(tool => `
                <span class="tag tag-tools">${tool}</span>
            `).join('');
        } else {
            currentTools = [];
            toolsDisplay.innerHTML = '<span>No tools added yet</span>';
        }
    }
}

async function saveProfileData(section) {
    try {
        // Get the current values from input fields
        const editContainer = document.getElementById(`${section}Edit`);
        if (!editContainer) return;
        
        const inputs = editContainer.querySelectorAll('.editable-input');
        
        // Extract values from inputs, filtering out empty ones
        const values = Array.from(inputs)
            .map(input => input.value.trim())
            .filter(value => value !== '');
        
        // Prepare data for the request
        let requestData = {};
        
        if (section === 'skills') {
            requestData = {
                skills: values,
                tnp: []
            };
        } else if (section === 'tools') {
            requestData = {
                skills: [],
                tnp: values
            };
        }
        
        console.log('Saving profile data:', requestData);
        
        // Send POST request to FastAPI server
        const response = await fetch('/update-profile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Profile update response:', result);
        
        // Show appropriate toast message based on response
        if (result === 0) {
            showToast('Updated successfully!', 'success');
            
            // Update the current data and display
            if (section === 'skills') {
                currentSkills = values;
                updateSkillsDisplay(values);
            } else if (section === 'tools') {
                currentTools = values;
                updateToolsDisplay(values);
            }
            
            // Switch back to display mode
            toggleEdit(section);
            
        } else if (result === 1) {
            showToast('Update unsuccessful!', 'error');
        }
        
    } catch (error) {
        console.error('Error saving profile data:', error);
        showToast('Error updating profile. Please try again.', 'error');
    }
}

function updateSkillsDisplay(skills) {
    const skillsDisplay = document.getElementById('skillsDisplay');
    if (!skillsDisplay) return;
    
    if (skills && skills.length > 0) {
        skillsDisplay.innerHTML = skills.map(skill => `
            <span class="tag">${skill}</span>
        `).join('');
    } else {
        skillsDisplay.innerHTML = '<span>No skills added yet</span>';
    }
}

function updateToolsDisplay(tools) {
    const toolsDisplay = document.getElementById('toolsDisplay');
    if (!toolsDisplay) return;
    
    if (tools && tools.length > 0) {
        toolsDisplay.innerHTML = tools.map(tool => `
            <span class="tag tag-tools">${tool}</span>
        `).join('');
    } else {
        toolsDisplay.innerHTML = '<span>No tools added yet</span>';
    }
}

// ====== Toast Notification ======

function showToast(message, type) {
    const toast = document.getElementById('toastNotification');
    if (!toast) return;
    
    toast.textContent = message;
    toast.className = `toast ${type === 'success' ? 'toast-success' : 'toast-error'}`;
    
    // Show the toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    // Hide the toast after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ====== Notification Modal Functions ======

function toggleNotificationModal() {
    const modal = document.getElementById('notificationModal');
    if (!modal) return;
    
    if (modal.classList.contains('active')) {
        closeNotificationModal();
    } else {
        openNotificationModal();
    }
}

function openNotificationModal() {
    const modal = document.getElementById('notificationModal');
    if (!modal) return;
    
    modal.classList.add('active');
    
    // Reset notification badge to zero when modal is opened
    resetNotificationBadge();
    
    // Load notifications
    loadNotifications();
}

function closeNotificationModal() {
    const modal = document.getElementById('notificationModal');
    if (modal) modal.classList.remove('active');
}

async function loadNotifications() {
    const notificationBody = document.getElementById('notificationBody');
    if (!notificationBody) return;
    
    try {
        // Send POST request to FastAPI server
        const response = await fetch('/notification-user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ x: 'any string value' })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const notifications = await response.json();
        console.log('Received notifications:', notifications);
        
        // Render notifications
        if (notifications && notifications.length > 0) {
            notificationBody.innerHTML = notifications.map((notification, index) => {
                const [message, status] = notification;
                const isUnread = status === 0;
                
                return `
                    <div class="notification-item ${isUnread ? 'notification-unread' : ''}">
                        <div class="notification-icon-container ${isUnread ? 'notification-warning' : 'notification-success'}">
                            <i class="fas ${isUnread ? 'fa-exclamation' : 'fa-check'}"></i>
                        </div>
                        <div class="notification-content">
                            <div class="notification-message">${message}</div>
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            notificationBody.innerHTML = `
                <div class="notification-empty">
                    <i class="fas fa-bell-slash" style="font-size: 2rem; margin-bottom: 10px;"></i>
                    <p>No notifications</p>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Error loading notifications:', error);
        notificationBody.innerHTML = `
            <div class="notification-empty">
                <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 10px;"></i>
                <p>Error loading notifications</p>
            </div>
        `;
    }
}

// ====== Community Chat Functions ======

async function loadCommunityChat() {
    const chatArea = document.getElementById('chatArea');
    const loadingSpinner = document.getElementById('communityLoading');
    
    if (!chatArea || !loadingSpinner) return;
    
    // Show loading spinner
    chatArea.innerHTML = '';
    loadingSpinner.style.display = 'block';
    
    try {
        // Send POST request to FastAPI server
        const response = await fetch('/community', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ x: 'any string value' })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const chats = await response.json();
        console.log('Received community chats:', chats);
        
        // Hide loading spinner
        loadingSpinner.style.display = 'none';
        
        // Render chats
        if (chats && chats.length > 0) {
            renderChatMessages(chats);
        } else {
            chatArea.innerHTML = `
                <div class="chat-empty">
                    <i class="fas fa-comments"></i>
                    <p>No messages yet. Start the conversation!</p>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Error loading community chat:', error);
        loadingSpinner.style.display = 'none';
        chatArea.innerHTML = `
            <div class="chat-empty">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Error loading messages. Please try again.</p>
            </div>
        `;
    }
}

function renderChatMessages(chats) {
    const chatArea = document.getElementById('chatArea');
    if (!chatArea) return;
    
    chatArea.innerHTML = chats.map(chat => {
        const isOwnMessage = chat.user === currentUserId;
        const messageClass = isOwnMessage ? 'own-message' : 'other-message';
        
        return `
            <div class="message-container ${messageClass}">
                <div class="message-bubble">
                    <div class="message-header">${chat.username || 'Unknown User'}</div>
                    <div class="message-content">${chat.message}</div>
                    <div class="message-time">${chat.time}</div>
                </div>
            </div>
        `;
    }).join('');
    
    // Scroll to bottom
    scrollToBottom();
}

function formatTime(timeString) {
    if (!timeString) return '';
    
    try {
        const date = new Date(timeString);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (e) {
        return timeString;
    }
}

function scrollToBottom() {
    const chatArea = document.getElementById('chatArea');
    if (chatArea) {
        chatArea.scrollTop = chatArea.scrollHeight;
    }
}

function initializeCommunityWebSocket() {
    if (!currentUserId) {
        console.error('User ID not found for Community WebSocket connection');
        return;
    }
    
    try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/community/${currentUserId}`;
        
        communitySocket = new WebSocket(wsUrl);
        
        communitySocket.onopen = function(event) {
            console.log('Unified Community WebSocket connected successfully');
        };
        
        communitySocket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            console.log('Unified Community WebSocket message received:', data);
            
            if (data.type === 'chat_message') {
                handleNewChatMessage(data.message);
            } else if (data.type === 'user_joined') {
                showSystemMessage(`${data.username} joined the chat`);
            } else if (data.type === 'user_left') {
                showSystemMessage(`${data.username} left the chat`);
            }
        };
        
        communitySocket.onclose = function(event) {
            console.log('Community WebSocket disconnected:', event);
        };
        
        communitySocket.onerror = function(error) {
            console.error('Community WebSocket error:', error);
        };
        
    } catch (error) {
        console.error('Error initializing Community WebSocket:', error);
    }
}

function handleNewChatMessage(messageData) {
    const chatArea = document.getElementById('chatArea');
    if (!chatArea) return;
    
    // Remove empty state if it exists
    const emptyState = chatArea.querySelector('.chat-empty');
    if (emptyState) {
        emptyState.remove();
    }
    
    const isOwnMessage = messageData.user === currentUserId;
    const messageClass = isOwnMessage ? 'own-message' : 'other-message';
    
    const messageElement = document.createElement('div');
    messageElement.className = `message-container ${messageClass}`;
    messageElement.innerHTML = `
        <div class="message-bubble">
            <div class="message-header">${messageData.username || 'Unknown User'}</div>
            <div class="message-content">${messageData.message}</div>
            <div class="message-time">${messageData.time}</div>
        </div>
    `;
    
    chatArea.appendChild(messageElement);
    scrollToBottom();
}

function showSystemMessage(message) {
    const chatArea = document.getElementById('chatArea');
    if (!chatArea) return;
    
    // Remove empty state if it exists
    const emptyState = chatArea.querySelector('.chat-empty');
    if (emptyState) {
        emptyState.remove();
    }
    
    const systemElement = document.createElement('div');
    systemElement.className = 'message-container';
    systemElement.style.justifyContent = 'center';
    systemElement.innerHTML = `
        <div style="background-color: rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.7); padding: 5px 15px; border-radius: 15px; font-size: 0.8rem;">
            ${message}
        </div>
    `;
    
    chatArea.appendChild(systemElement);
    scrollToBottom();
}

async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    if (!messageInput) return;
    
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Get username from template data or use default
    const username = window.fullname || 'User';
    
    if (communitySocket && communitySocket.readyState === WebSocket.OPEN) {
        // Send via WebSocket with user info
        communitySocket.send(JSON.stringify({
            type: 'chat_message',
            message: message,
            user_id: currentUserId,
            username: username,
            user_type: "client"
        }));
        
        // Clear input
        messageInput.value = '';
    } else {
        // Fallback: Send via HTTP POST with user info
        try {
            const response = await fetch('/send-message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    message: message,
                    user_id: currentUserId,
                    username: username,
                    user_type: "client"
                })
            });
            
            if (response.ok) {
                messageInput.value = '';
            } else {
                alert('Error sending message. Please try again.');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            alert('Error sending message. Please try again.');
        }
    }
}

function closeCommunityWebSocket() {
    if (communitySocket) {
        communitySocket.close();
        communitySocket = null;
    }
}

function refreshCommunity() {
    loadCommunityChat();
}

// ====== Event Listeners Initialization ======

function initializeEventListeners() {
    // Notification icon
    const notificationIcon = document.getElementById('notificationIcon');
    if (notificationIcon) {
        notificationIcon.addEventListener('click', toggleNotificationModal);
    }
    
    // Notification modal close
    const notificationClose = document.getElementById('notificationClose');
    if (notificationClose) {
        notificationClose.addEventListener('click', closeNotificationModal);
    }
    
    // Profile modal
    const userProfileBtn = document.getElementById('userProfileBtn');
    if (userProfileBtn) {
        userProfileBtn.addEventListener('click', openProfileModal);
    }
    
    const profileModalOverlay = document.getElementById('profileModalOverlay');
    if (profileModalOverlay) {
        profileModalOverlay.addEventListener('click', closeProfileModal);
    }
    
    // Sidebar navigation
    const dashboardBtn = document.getElementById('dashboardBtn');
    if (dashboardBtn) {
        dashboardBtn.addEventListener('click', function(e) {
            e.preventDefault();
            showSection('dashboardContent', 'Dashboard');
        });
    }
    
    const projectsBtn = document.getElementById('projectsBtn');
    if (projectsBtn) {
        projectsBtn.addEventListener('click', function(e) {
            e.preventDefault();
            showSection('projectsSection', 'Projects');
        });
    }
    
    const tasksBtn = document.getElementById('tasksBtn');
    if (tasksBtn) {
        tasksBtn.addEventListener('click', function(e) {
            e.preventDefault();
            showSection('tasksSection', 'Tasks');
        });
    }
    
    const communityBtn = document.getElementById('communityBtn');
    if (communityBtn) {
        communityBtn.addEventListener('click', function(e) {
            e.preventDefault();
            showSection('communitySection', 'Community');
        });
    }
    
    // Refresh buttons
    const refreshProjects = document.getElementById('refreshProjects');
    if (refreshProjects) {
        refreshProjects.addEventListener('click', function(e) {
            e.preventDefault();
            loadProjects();
        });
    }
    
    const refreshTasks = document.getElementById('refreshTasks');
    if (refreshTasks) {
        refreshTasks.addEventListener('click', function(e) {
            e.preventDefault();
            loadTasks();
        });
    }
    
    const refreshCommunity = document.getElementById('refreshCommunity');
    if (refreshCommunity) {
        refreshCommunity.addEventListener('click', function(e) {
            e.preventDefault();
            loadCommunityChat();
        });
    }
    
    // Community chat
    const sendMessageBtn = document.getElementById('sendMessageBtn');
    if (sendMessageBtn) {
        sendMessageBtn.addEventListener('click', sendMessage);
    }
    
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    // Profile save buttons
    const saveSkillsBtn = document.getElementById('saveSkillsBtn');
    if (saveSkillsBtn) {
        saveSkillsBtn.addEventListener('click', function() {
            saveProfileData('skills');
        });
    }
    
    const saveToolsBtn = document.getElementById('saveToolsBtn');
    if (saveToolsBtn) {
        saveToolsBtn.addEventListener('click', function() {
            saveProfileData('tools');
        });
    }
    
    // Profile edit buttons
    const editSkillsBtn = document.getElementById('editSkillsBtn');
    if (editSkillsBtn) {
        editSkillsBtn.addEventListener('click', function() {
            toggleEdit('skills');
        });
    }
    
    const editToolsBtn = document.getElementById('editToolsBtn');
    if (editToolsBtn) {
        editToolsBtn.addEventListener('click', function() {
            toggleEdit('tools');
        });
    }
    
    // Profile cancel buttons
    const cancelSkillsBtn = document.getElementById('cancelSkillsBtn');
    if (cancelSkillsBtn) {
        cancelSkillsBtn.addEventListener('click', function() {
            toggleEdit('skills');
        });
    }
    
    const cancelToolsBtn = document.getElementById('cancelToolsBtn');
    if (cancelToolsBtn) {
        cancelToolsBtn.addEventListener('click', function() {
            toggleEdit('tools');
        });
    }
}

// ====== Make Functions Available Globally ======

window.toggleCheckbox = toggleCheckbox;
window.toggleComponentDetails = toggleComponentDetails;
window.toggleEdit = toggleEdit;
window.addNewInput = addNewInput;
window.saveProfileData = saveProfileData;
window.openProfileModal = openProfileModal;
window.closeProfileModal = closeProfileModal;
window.showSection = showSection;
window.loadDashboardData = loadDashboardData;
window.loadProjects = loadProjects;
window.loadTasks = loadTasks;
window.loadCommunityChat = loadCommunityChat;
window.refreshCommunity = refreshCommunity;
window.sendMessage = sendMessage;
window.toggleNotificationModal = toggleNotificationModal;
window.openNotificationModal = openNotificationModal;
window.closeNotificationModal = closeNotificationModal;
window.initializeCommunityWebSocket = initializeCommunityWebSocket;
window.closeCommunityWebSocket = closeCommunityWebSocket;
window.sendTestNotification = sendTestNotification;