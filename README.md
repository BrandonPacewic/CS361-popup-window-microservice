# CS361 Popup Window Microservice

Assignment Repository for Software Engineering I at Oregon State University.

## Help Popup Window Microservice (macOS)

This microservice opens a native popup window on macOS using Tkinter. It exposes four REST endpoints so you can set:
1. Help text
2. Help title
3. Open the popup window
4. Close the popup window

The GUI logic runs in a separate thread from the FastAPI app, ensuring the API remains responsive.

## Requirements

- macOS with a functioning GUI environment.
- Python 3 with Tkinter installed.
- [Homebrew](https://brew.sh) + `brew install tcl-tk`
  - Optional, if you lack Tkinter. Included by default on most systems. Try without first, if you get an error like `No module named '_tkinter'` you will need to install it manually.

## Installation & Usage

1. **Install dependencies**:

```bash
pip install -r requirements.txt
```

2. **Run the microservice**:

```bash
fastapi run popup/main.py
```

3. The API defaults to `http://localhost:8000`.

## API Endpoints

### 1. Set Help Text
- **Method**: `POST`
- **Endpoint**: `/help-text`
- **Payload**:
```json
{
"help_text": "This is the help text for the popup window."
}
```
- **Response**:
```json
{
  "message": "Help text set successfully.",
  "help_text": "This is the help text for the popup window."
}
```

### 2. Set Help Title
- **Method**: `POST`
- **Endpoint**: `/help-title`
- **Payload**:
```json
{
  "title": "My Help Window"
}
```
- **Response**:
```json
{
  "message": "Help title set successfully.",
  "help_title": "My Help Window"
}
```

### 3. Open Help Window
- **Method**: `POST`
- **Endpoint**: `/open-help-window`
- **Response**:
```json
{
  "message": "Help window is now open.",
  "title": "My Help Window",
  "help_text": "This is the help text for the popup window."
}
```

### 4. Close Help Window
- **Method**: `POST`
- **Endpoint**: `/close-help-window`
- **Response**:
```json
{
  "message": "Help window is now closed."
}
```

## Running the Tests

```
python tests/test.py
```

## UML Sequence Diagram

```mermaid
sequenceDiagram
    autonumber

    participant Client
    participant FastAPI_Thread
    participant Tkinter_Thread

    Note right of Tkinter_Thread: runs tkinter mainloop

    Client->>FastAPI_Thread: POST /help-text<br>{"help_text": "..."}
    FastAPI_Thread->>FastAPI_Thread: Save help_text<br>Queue update action
    FastAPI_Thread->>Tkinter_Thread: action_queue -> update label

    Client->>FastAPI_Thread: POST /help-title<br>{"title": "..."}
    FastAPI_Thread->>FastAPI_Thread: Save help_title<br>Queue update action
    FastAPI_Thread->>Tkinter_Thread: action_queue -> update window title

    Client->>FastAPI_Thread: POST /open-help-window
    FastAPI_Thread->>FastAPI_Thread: window_open = True<br>Queue create window
    FastAPI_Thread->>Tkinter_Thread: action_queue -> create Toplevel

    Client->>FastAPI_Thread: POST /close-help-window
    FastAPI_Thread->>FastAPI_Thread: window_open = False<br>Queue close window
    FastAPI_Thread->>Tkinter_Thread: action_queue -> destroy Toplevel
```
