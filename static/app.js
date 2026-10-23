const DEFAULT_PRIORITY = 'medium';


document.addEventListener('DOMContentLoaded', fetchTasks);


async function fetchTasks() {
    const response = await fetch('/api/tasks');
    const tasks = await response.json();
    const taskList = document.getElementById('task-list');
    taskList.innerHTML = '';

    tasks.forEach(task => {
        const li = document.createElement('li');
        const taskTitle = document.createElement('span');
        const prioritySelect = document.createElement('select');
        const deleteButton = document.createElement('button');
        const priority = task.priority || DEFAULT_PRIORITY;

        taskTitle.textContent = task.title;
        taskTitle.className = 'task-title';

        prioritySelect.className = `priority priority-${priority}`;
        prioritySelect.setAttribute('aria-label', 'Task priority');
        ['low', 'medium', 'high'].forEach(value => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = value.charAt(0).toUpperCase() + value.slice(1);
            option.selected = value === priority;
            prioritySelect.appendChild(option);
        });
        prioritySelect.addEventListener('change', () => {
            updatePriority(task.id, prioritySelect);
        });

        deleteButton.textContent = 'Delete';
        deleteButton.className = 'delete-btn';
        deleteButton.addEventListener('click', () => deleteTask(task.id));

        li.appendChild(taskTitle);
        li.appendChild(prioritySelect);
        li.appendChild(deleteButton);
        taskList.appendChild(li);
    });
}


async function addTask() {
    const titleInput = document.getElementById('task-title');
    const priorityInput = document.getElementById('task-priority');
    const title = titleInput.value.trim();

    if (!title) return;

    await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title,
            priority: priorityInput.value
        })
    });

    titleInput.value = '';
    priorityInput.value = DEFAULT_PRIORITY;
    fetchTasks();
}


async function updatePriority(id, prioritySelect) {
    const response = await fetch(`/api/tasks/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ priority: prioritySelect.value })
    });

    if (!response.ok) {
        fetchTasks();
        return;
    }

    prioritySelect.className = `priority priority-${prioritySelect.value}`;
}


async function deleteTask(id) {
    await fetch(`/api/tasks/${id}`, {
        method: 'DELETE'
    });
    fetchTasks();
}
