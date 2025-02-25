import threading
import queue
import time

from fastapi import FastAPI, status
from pydantic import BaseModel
import tkinter as tk

app = FastAPI(title="Help Popup Window (macOS)")

# -----------------------------
# Shared State and Concurrency
# -----------------------------
help_title = ""
help_text = ""
window_open = False

# We communicate with the Tkinter thread via a queue of callable actions.
action_queue = queue.Queue()

# The Tkinter-related references
root = None       # main Tkinter root
help_window = None
help_label = None


def run_tkinter_loop():
    """
    This function runs in its own thread to handle all Tkinter operations.
    """
    global root
    root = tk.Tk()

    # Hide the root window to avoid confusion (we will create a Toplevel window).
    root.withdraw()

    # Periodically process any queued actions from the FastAPI thread
    def process_actions():
        while not action_queue.empty():
            func = action_queue.get_nowait()
            func()
            action_queue.task_done()

        root.after(100, process_actions)

    # Kick off the recursive polling
    process_actions()

    # Start the Tkinter main event loop
    root.mainloop()


# Start the Tkinter thread
tk_thread = threading.Thread(target=run_tkinter_loop, daemon=True)
tk_thread.start()


# -----------------------------
# Tkinter Actions
# -----------------------------
def _create_help_window():
    """
    Create a new Toplevel help window with the current help_title and help_text.
    This runs inside the Tkinter thread.
    """
    global help_window, help_label, help_title, help_text

    if help_window is not None and tk.Toplevel.winfo_exists(help_window):
        # If already exists, just bring it to front
        help_window.lift()
        return

    help_window = tk.Toplevel(root)
    help_window.title(help_title or "Help Window")

    help_label = tk.Label(help_window, text=help_text or "No help text set.")
    help_label.pack(padx=20, pady=20)

def _update_help_window():
    """
    If the help window is open, update its title and label to reflect latest changes.
    Runs inside the Tkinter thread.
    """
    global help_window, help_label, help_title, help_text
    if help_window is not None and tk.Toplevel.winfo_exists(help_window):
        help_window.title(help_title or "Help Window")
        help_label.config(text=help_text or "No help text set.")

def _close_help_window():
    """
    Destroy the help window if it exists.
    Runs inside the Tkinter thread.
    """
    global help_window
    if help_window is not None and tk.Toplevel.winfo_exists(help_window):
        help_window.destroy()

    help_window = None


# -----------------------------
# FastAPI Models
# -----------------------------
class HelpTextRequest(BaseModel):
    help_text: str

class HelpTitleRequest(BaseModel):
    title: str


# -----------------------------
# FastAPI Endpoints
# -----------------------------
@app.post("/help-text", status_code=status.HTTP_200_OK)
async def set_help_text(request: HelpTextRequest):
    """
    Supply information to the help popup window in the form of a string.
    """
    global help_text
    help_text = request.help_text

    # If window is open, update its text from the Tkinter thread
    if window_open:
        action_queue.put(_update_help_window)

    return {"message": "Help text set successfully.", "help_text": help_text}


@app.post("/help-title", status_code=status.HTTP_200_OK)
async def set_help_title(request: HelpTitleRequest):
    """
    Provide the window title in the form of a string.
    """
    global help_title
    help_title = request.title

    # If window is open, update its title from the Tkinter thread
    if window_open:
        action_queue.put(_update_help_window)

    return {"message": "Help title set successfully.", "help_title": help_title}


@app.post("/open-help-window", status_code=status.HTTP_200_OK)
async def open_help_window():
    """
    Open the popup window on macOS.
    """
    global window_open
    if window_open:
        return {
            "message": "Help window is already open.",
            "title": help_title,
            "help_text": help_text
        }

    window_open = True

    # Put an action for the Tkinter thread to create the window
    action_queue.put(_create_help_window)

    return {
        "message": "Help window is now open.",
        "title": help_title,
        "help_text": help_text
    }


@app.post("/close-help-window", status_code=status.HTTP_200_OK)
async def close_help_window():
    """
    Force close the popup window.
    """
    global window_open
    if not window_open:
        return {"message": "Window is already closed."}

    window_open = False

    # Put an action to close the window in the Tkinter thread
    action_queue.put(_close_help_window)

    return {"message": "Help window is now closed."}
