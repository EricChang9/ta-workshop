from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

DEFAULT_PRIORITY = "medium"
VALID_PRIORITIES = {"low", "medium", "high"}

tasks = [
    {"id": 1, "title": "Project-1 Report"},
    {"id": 2, "title": "Project-2 MMFs"}
]
next_id = 3


def normalize_task(task):
    """Ensure a task has a valid priority value."""
    if task.get("priority") not in VALID_PRIORITIES:
        task["priority"] = DEFAULT_PRIORITY
    return task


@app.route('/')
def index():
    """Render the task tracker page."""
    return render_template('index.html')


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Return all tasks with normalized priorities."""
    for task in tasks:
        normalize_task(task)
    return jsonify(tasks)


@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Create a task with a validated priority."""
    global next_id
    data = request.get_json(silent=True) or {}
    title = data.get('title', '').strip()
    priority = data.get('priority', DEFAULT_PRIORITY)

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if priority not in VALID_PRIORITIES:
        return jsonify({"error": "Invalid priority"}), 400

    new_task = {
        "id": next_id,
        "title": title,
        "priority": priority
    }
    tasks.append(new_task)
    next_id += 1

    return jsonify(new_task), 201


@app.route('/api/tasks/<int:task_id>', methods=['PATCH'])
def update_task(task_id):
    """Update a task's priority."""
    data = request.get_json(silent=True) or {}
    priority = data.get('priority')

    if priority not in VALID_PRIORITIES:
        return jsonify({"error": "Invalid priority"}), 400

    task = next((item for item in tasks if item['id'] == task_id), None)
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    task['priority'] = priority
    return jsonify(normalize_task(task))


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task by ID."""
    global tasks
    original_count = len(tasks)
    tasks = [task for task in tasks if task['id'] != task_id]

    if len(tasks) == original_count:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"result": "success"}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
