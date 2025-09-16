import json

STATE_FILE = ".agent_state.json"

def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def load_state() -> dict:
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def set_project_id(project_id: str):
    state = load_state()
    state["project_id"] = project_id
    save_state(state)
    return f"Project ID set to {project_id}"

def get_project_id() -> str:
    state = load_state()
    return state.get("project_id")
