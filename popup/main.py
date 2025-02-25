import threading
import queue
import tkinter as tk
from fastapi import FastAPI, status
from pydantic import BaseModel
import uvicorn

# -----------------------------
# FastAPI App and Shared State
# -----------------------------
app = FastAPI(title="Help Popup Window (macOS)")

help_title = ""
help_text = ""
window_open = False

# We’ll communicate from the FastAPI thread to Tkinter thread with a queue of callables
action_queue = queue.Queue()

root = None         # Main Tk root
help_window = None  # Toplevel popup
help_label = None


# -----------------------------
# Tkinter / GUI Thread Code
# -----------------------------
def tkinter_mainloop():
    """Run Tkinter on the main thread (macOS requirement)."""
    global root
    root = tk.Tk()

    # We can keep the root window hidden if desired:
    root.withdraw()

    def process_actions():
        """Periodically process tasks enqueued from FastAPI."""
        while not action_queue.empty():
            func = action_queue.get_nowait()
            func()
            action_queue.task_done()
        root.after(100, process_actions)

    process_actions()  # start the polling loop
    root.mainloop()


def create_help_window():
    """Create a Toplevel help window with the current help_title & help_text."""
    global help_window, help_label
    if help_window is not None and tk.Toplevel.winfo_exists(help_window):
        # Already exists; just bring it to front
        help_window.lift()
        return

    help_window = tk.Toplevel(root)
    help_window.title(help_title or "Help Window")
    help_label = tk.Label(help_window, text=help_text or "No help text set.")
    help_label.pack(padx=20, pady=20)


def update_help_window():
    """If the window is open, update its title and label."""
    if help_window is not None and tk.Toplevel.winfo_exists(help_window):
        help_window.title(help_title or "Help Window")
        help_label.config(text=help_text or "No help text set.")


def close_help_window():
    """Destroy the Toplevel if it exists."""
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

    # If window is open, update the GUI on the Tkinter thread
    if window_open:
        action_queue.put(update_help_window)
    return {"message": "Help text set successfully.", "help_text": help_text}


@app.post("/help-title", status_code=status.HTTP_200_OK)
async def set_help_title(request: HelpTitleRequest):
    """
    Provide the window title in the form of a string.
    """
    global help_title
    help_title = request.title

    # If window is open, update the GUI on the Tkinter thread
    if window_open:
        action_queue.put(update_help_window)
    return {"message": "Help title set successfully.", "help_title": help_title}


@app.post("/open-help-window", status_code=status.HTTP_200_OK)
async def open_help_window():
    """
    Open the popup window (on the Tkinter main thread).
    """
    global window_open
    if window_open:
        return {"message": "Help window is already open.", "title": help_title, "help_text": help_text}

    window_open = True
    action_queue.put(create_help_window)
    return {"message": "Help window is now open.", "title": help_title, "help_text": help_text}


@app.post("/close-help-window", status_code=status.HTTP_200_OK)
async def close_help_window_api():
    """
    Force close the popup window.
    """
    global window_open
    if not window_open:
        return {"message": "Window is already closed."}
    window_open = False
    action_queue.put(close_help_window)
    return {"message": "Help window is now closed."}


# -----------------------------
# Launch Uvicorn in a Thread
# -----------------------------
def run_server():
    """Run the FastAPI/Uvicorn server in a background thread."""
    # Note: 'reload=True' won't work well from inside a thread; typically for dev, run from CLI
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


def main():
    """Main entry point: start the server in a thread, then run Tkinter on the main thread."""
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    tkinter_mainloop()


if __name__ == "__main__":
    main()
