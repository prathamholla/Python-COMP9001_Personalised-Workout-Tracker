# Personal Fitness & Volume Tracker

A compact Tkinter + NumPy desktop app to log workout sets and compute total training volume.

## How to Run

### 1) Requirements
- Python **3.9+**
- `numpy`
- Tkinter (bundled on Windows/macOS; on Linux install `python3-tk`)

Install NumPy:
```bash
python -m pip install --upgrade pip
pip install numpy
# Linux only (if Tkinter missing):
# Debian/Ubuntu: sudo apt-get install python3-tk
# Fedora:        sudo dnf install python3-tkinter
```

### 2) Get the project
- Save the main script as **fitness_tracker_app.py** in a folder.
- *(Optional)* Add **gym_background.gif** (GIF only) in the same folder.
- **workout_log.csv** will be created automatically on first save/exit.

### 3) Run
```bash
python fitness_tracker_app.py
```

### 4) Use
1. Fill **Date, Exercise, Sets, Reps, Weight (kg)** → **Add Set**.
2. To edit/delete: select a row in the table → **Load Selected** → edit → **Update Selected**, or **Delete Selected**.
3. **Recalculate Summary** updates totals (also auto-updates on changes).

### 5) Save
- Data auto-saves to **workout_log.csv** when you close the app.

### (Optional) Resize UI
Open `fitness_tracker_app.py` and tweak:
```python
self._set_ui_scale(0.85)  # 0.75 smaller, 1.0 normal
self.geometry("720x520")  # initial window size
```
