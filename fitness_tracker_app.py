import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import csv
import os
from datetime import datetime

# --- CORE NUMPY CALCULATION (Testable Logic) ---

def calculate_total_volume(workout_array):
    """
    Calculates the total weight lifted using NumPy's vectorized operations.
    Formula: SUM(Sets * Reps * Weight)
    """
    if workout_array.size == 0:
        return 0.0
    return np.sum(workout_array['sets'] * workout_array['reps'] * workout_array['weight'])

# --- TKINTER APPLICATION CLASS ---

class FitnessTrackerApp(tk.Tk):
    EMBEDDED_DARK_GIF_DATA = "R0lGODlhAQABAIAAAOjo6AAAACwAAAAAAQABAAACAkQBADs="

    def __init__(self, log_path="workout_log.csv", image_path="gym_background.gif"):
        super().__init__()
        self.title("Personal Fitness & Volume Tracker")
        self.log_path = log_path
        self.image_path = image_path

        # ========= Compact mode tweaks =========
        self._set_ui_scale(0.85)             # <— smaller overall UI (fonts/layout)
        self.geometry("720x520")             # <— smaller default window
        self.minsize(620, 480)
        # ======================================

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._setup_styles()
        self._setup_data_structure()

        # Background Image and Canvas Setup
        self.bg_image = None
        self._load_background_image()
        self._setup_canvas_and_main_frame()

        # Load data
        self.session_log = self._load_data()

        # Selection
        self.selected_index = None

        # Build UI
        self._build_header()
        self._build_summary_frame()
        self._build_input_frame()
        self._build_log_frame()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.update_all_displays()

    # ---------- Compact scaling ----------
    def _set_ui_scale(self, scale: float):
        """
        Globally scales Tk's internal pixels-per-point.
        1.0 ≈ 96 DPI. Values < 1 make the UI smaller.
        """
        try:
            self.tk.call('tk', 'scaling', scale)
        except Exception:
            pass
    # ------------------------------------

    def _load_background_image(self):
        try:
            if os.path.exists(self.image_path):
                self.bg_image = tk.PhotoImage(file=self.image_path)
                return
            else:
                print(f"External image not found: '{self.image_path}'. Using embedded fallback.")
        except Exception as e:
            messagebox.showwarning(
                "Image Format Error",
                f"External image failed to load. Tkinter requires GIF/PPM natively. Error: {e}. Using fallback."
            )
        try:
            self.bg_image = tk.PhotoImage(data=self.EMBEDDED_DARK_GIF_DATA)
        except Exception as e:
            messagebox.showerror(
                "Image Fatal Error",
                f"Cannot load any image data. Error: {e}"
            )

    def _setup_canvas_and_main_frame(self):
        self.canvas = tk.Canvas(self, bg='#1c1e21', highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        if self.bg_image and self.bg_image.width() > 10 and self.bg_image.height() > 10:
            self.canvas.create_image(360, 260, image=self.bg_image, anchor="center")

        self.main_frame = ttk.Frame(self.canvas, style='TFrame')
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(3, weight=1)

        self.main_frame_id = self.canvas.create_window(360, 260, window=self.main_frame, anchor="center")
        self.bind('<Configure>', self._on_resize)

    def _on_resize(self, event):
        width = self.winfo_width()
        height = self.winfo_height()
        self.canvas.coords(self.main_frame_id, width / 2, height / 2)
        if self.bg_image and self.bg_image.width() > 10 and self.bg_image.height() > 10:
            try:
                self.canvas.coords(self.canvas.find_all()[0], width / 2, height / 2)
            except Exception:
                pass

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')

        base_font = ('Inter', 9)           # smaller font
        base_font_bold = ('Inter', 9, 'bold')

        style.configure('.', font=base_font, background='#282c34', foreground='#abb2bf')
        style.configure('TLabel', background='#282c34', foreground='#abb2bf', padding=(0, 0))
        style.configure('TFrame', background='#282c34')
        style.configure('TEntry', background='#3e4451', fieldbackground='#3e4451', foreground='#ffffff', borderwidth=0, padding=2)

        style.configure('Accent.TButton', font=base_font_bold, padding=6, background='#61afef', foreground='#ffffff', borderwidth=0)
        style.map('Accent.TButton', background=[('active', '#569cd6')])

        style.configure("Treeview", background="#3e4451", foreground="#ffffff", fieldbackground="#3e4451", borderwidth=0)
        style.configure("Treeview.Heading", font=base_font_bold, background='#3e4451', foreground='#61afef')
        style.map("Treeview.Heading", background=[('active', '#4e5562')])

        self._fonts = {"base": base_font, "bold": base_font_bold}

    def _setup_data_structure(self):
        self.DTYPE = np.dtype([
            ('date', 'U10'), ('exercise', 'U30'), ('sets', 'i4'),
            ('reps', 'i4'), ('weight', 'f4')
        ])

    def _load_data(self):
        if not os.path.exists(self.log_path):
            return np.empty(0, dtype=self.DTYPE)
        data_list = []
        try:
            with open(self.log_path, mode='r', newline='') as file:
                reader = csv.reader(file)
                next(reader, None)
                for row in reader:
                    if len(row) == 5:
                        data_list.append((row[0], row[1], int(row[2]), int(row[3]), float(row[4])))
            return np.array(data_list, dtype=self.DTYPE)
        except Exception as e:
            messagebox.showerror("Data Load Error", f"Failed to load data: {e}. Starting with an empty log.")
            return np.empty(0, dtype=self.DTYPE)

    def on_closing(self):
        if messagebox.askyesno(
            "Exit Fitness Tracker",
            "Do you really want to close the Fitness Tracker? All data will be saved to the CSV file."
        ):
            self._save_data()
            self.destroy()

    def _save_data(self):
        try:
            data_to_write = self.session_log.tolist()
            with open(self.log_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['date', 'exercise', 'sets', 'reps', 'weight'])
                for row in data_to_write:
                    writer.writerow([row[0], row[1], row[2], row[3], f"{row[4]:.2f}"])
        except Exception as e:
            messagebox.showerror("Data Save Error", f"Failed to save data: {e}")

    # --- GUI CONSTRUCTION ---

    def _build_header(self):
        header_frame = ttk.Frame(self.main_frame, style='TFrame')
        header_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(10, 0))
        header_frame.columnconfigure(0, weight=1)

        header_label = ttk.Label(
            header_frame,
            text="🏋️ PERSONAL STRENGTH & VOLUME LOG 📈",
            font=('Inter', 12, 'bold'),   # smaller
            foreground='#98c379',
            background='#282c34'
        )
        header_label.pack(pady=4)

    def _build_summary_frame(self):
        summary_frame = ttk.LabelFrame(self.main_frame, text="Performance Summary", padding="10", style='TFrame')
        summary_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(6, 6))
        summary_frame.columnconfigure((0, 1), weight=1)

        self.volume_var = tk.StringVar(value="Total Volume: 0.00 kg")
        volume_label = ttk.Label(summary_frame, textvariable=self.volume_var,
                                 font=self._fonts["bold"], foreground='#98c379')
        volume_label.grid(row=0, column=0, padx=6, sticky='w')

        self.entries_var = tk.StringVar(value="Total Sets Logged: 0")
        entries_label = ttk.Label(summary_frame, textvariable=self.entries_var,
                                  font=self._fonts["bold"], foreground='#e5c07b')
        entries_label.grid(row=0, column=1, padx=6, sticky='e')

    def _build_input_frame(self):
        input_frame = ttk.LabelFrame(self.main_frame, text="Log New Workout Set", padding="10", style='TFrame')
        input_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=6)

        labels = ['Date:', 'Exercise:', 'Sets:', 'Reps:', 'Weight (kg):']
        self.entries = {}
        current_date = datetime.now().strftime('%Y-%m-%d')

        for i, text in enumerate(labels):
            input_frame.columnconfigure(i, weight=1)
            ttk.Label(input_frame, text=text).grid(row=0, column=i, padx=4, pady=1, sticky='w')
            entry = ttk.Entry(input_frame)
            entry.grid(row=1, column=i, padx=4, pady=3, sticky='ew')
            key = text.split(':')[0].lower()
            if key == 'weight (kg)':
                self.entries['weight (kg)'] = entry
            else:
                self.entries[key] = entry

        self.entries['date'].insert(0, current_date)

        # Buttons in two rows to avoid overflow on smaller widths
        button_frame_top = ttk.Frame(input_frame, style='TFrame')
        button_frame_top.grid(row=2, column=0, columnspan=5, sticky='ew', pady=(4, 0))
        button_frame_top.columnconfigure((0,1,2,3), weight=1)

        btn_add = ttk.Button(button_frame_top, text="Add Set", command=self.add_workout_entry, style='Accent.TButton')
        btn_add.grid(row=0, column=0, padx=3, sticky='ew')

        btn_recalc = ttk.Button(button_frame_top, text="Recalculate Summary", command=self.analyze_performance, style='Accent.TButton')
        btn_recalc.grid(row=0, column=1, padx=3, sticky='ew')

        self.load_btn = ttk.Button(button_frame_top, text="Load Selected", command=self.load_selected_into_inputs, style='Accent.TButton')
        self.load_btn.grid(row=0, column=2, padx=3, sticky='ew')

        self.update_btn = ttk.Button(button_frame_top, text="Update Selected", command=self.update_selected_entry, style='Accent.TButton')
        self.update_btn.grid(row=0, column=3, padx=3, sticky='ew')

        button_frame_bottom = ttk.Frame(input_frame, style='TFrame')
        button_frame_bottom.grid(row=3, column=0, columnspan=5, sticky='ew', pady=(4, 2))
        button_frame_bottom.columnconfigure(0, weight=1)

        self.delete_btn = ttk.Button(button_frame_bottom, text="Delete Selected", command=self.delete_selected, style='Accent.TButton')
        self.delete_btn.grid(row=0, column=0, padx=3, sticky='ew')

        for b in (self.load_btn, self.update_btn, self.delete_btn):
            b.state(['disabled'])

    def _build_log_frame(self):
        log_frame = ttk.LabelFrame(self.main_frame, text="Detailed Set History", padding="8", style='TFrame')
        log_frame.grid(row=3, column=0, sticky="nsew", padx=16, pady=(4, 12))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        cols = ('Date', 'Exercise', 'Sets', 'Reps', 'Weight')
        # height=12 limits visible rows so the table doesn't dominate small windows
        self.log_tree = ttk.Treeview(log_frame, columns=cols, show='headings', height=12)

        # Narrower columns
        widths = {'Date': 95, 'Exercise': 150, 'Sets': 70, 'Reps': 70, 'Weight': 80}
        for col in cols:
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, anchor='center', minwidth=70, width=widths[col], stretch=True)

        vsb = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_tree.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        self.log_tree.configure(yscrollcommand=vsb.set)
        self.log_tree.grid(row=0, column=0, sticky="nsew")

        self.log_tree.bind("<<TreeviewSelect>>", self._on_row_select)

    # --- LOGIC & UPDATE FUNCTIONS ---

    def add_workout_entry(self):
        raw_data = {key: self.entries[key].get().strip() for key in self.entries}
        try:
            sets = int(raw_data['sets'])
            reps = int(raw_data['reps'])
            weight = float(raw_data['weight (kg)'])
            exercise = raw_data['exercise']
            date = raw_data['date']

            if sets <= 0 or reps <= 0 or weight < 0 or not exercise:
                raise ValueError("Sets and Reps must be greater than 0. Weight must be 0 or positive. Exercise name is required.")

            new_entry = np.array([(date, exercise, sets, reps, weight)], dtype=self.DTYPE)
            self.session_log = np.concatenate([self.session_log, new_entry])

            self._clear_inputs()
            self.update_all_displays(scroll_to_end=True)

            messagebox.showinfo("Set Added Successfully",
                                f"New set for '{exercise}' added and tracked! Total Sets: {self.session_log.size}")

        except ValueError as e:
            messagebox.showerror(
                "Invalid Input",
                f"Please check all input fields. Sets, Reps, and Weight must be numbers, and no field can be left empty. Details: {e}"
            )

    def _clear_inputs(self):
        for key, entry in self.entries.items():
            if key not in ['date']:
                entry.delete(0, tk.END)

    def update_all_displays(self, scroll_to_end=False):
        self._update_log_display(scroll_to_end)
        self._update_summary_metrics()

    def _update_log_display(self, scroll_to_end=False):
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

        for idx, row in enumerate(self.session_log):
            display_row = (row['date'], row['exercise'], str(row['sets']), str(row['reps']), f"{row['weight']:.2f}")
            self.log_tree.insert('', 'end', iid=str(idx), values=display_row)

        if scroll_to_end and self.session_log.size > 0:
            last_item = self.log_tree.get_children()[-1]
            self.log_tree.see(last_item)

    def _update_summary_metrics(self):
        total_volume = calculate_total_volume(self.session_log)
        total_sets = self.session_log.size
        self.volume_var.set(f"Total Volume: {total_volume:,.2f} kg")
        self.entries_var.set(f"Total Sets Logged: {total_sets}")

    def analyze_performance(self):
        self._update_summary_metrics()
        messagebox.showinfo("Analysis Complete", "Performance Summary has been successfully updated.")

    # --- Selection & Edit/Delete Handlers ---

    def _on_row_select(self, event=None):
        selection = self.log_tree.selection()
        if not selection:
            self.selected_index = None
            for b in (self.load_btn, self.update_btn, self.delete_btn):
                b.state(['disabled'])
            return

        try:
            self.selected_index = int(selection[0])
            for b in (self.load_btn, self.update_btn, self.delete_btn):
                b.state(['!disabled'])
        except ValueError:
            self.selected_index = None
            for b in (self.load_btn, self.update_btn, self.delete_btn):
                b.state(['disabled'])

    def load_selected_into_inputs(self):
        if self.selected_index is None:
            messagebox.showwarning("No Selection", "Please select a row in the history table first.")
            return
        row = self.session_log[self.selected_index]
        self.entries['date'].delete(0, tk.END)
        self.entries['date'].insert(0, row['date'])
        self.entries['exercise'].delete(0, tk.END)
        self.entries['exercise'].insert(0, row['exercise'])
        self.entries['sets'].delete(0, tk.END)
        self.entries['sets'].insert(0, str(row['sets']))
        self.entries['reps'].delete(0, tk.END)
        self.entries['reps'].insert(0, str(row['reps']))
        self.entries['weight (kg)'].delete(0, tk.END)
        self.entries['weight (kg)'].insert(0, f"{row['weight']:.2f}")

    def update_selected_entry(self):
        if self.selected_index is None:
            messagebox.showwarning("No Selection", "Please select a row to update.")
            return

        raw_data = {key: self.entries[key].get().strip() for key in self.entries}
        try:
            sets = int(raw_data['sets'])
            reps = int(raw_data['reps'])
            weight = float(raw_data['weight (kg)'])
            exercise = raw_data['exercise']
            date = raw_data['date']

            if sets <= 0 or reps <= 0 or weight < 0 or not exercise:
                raise ValueError("Sets/Reps must be > 0, weight ≥ 0, and exercise required.")

            self.session_log[self.selected_index] = (date, exercise, sets, reps, weight)
            self.update_all_displays()
            messagebox.showinfo("Updated", "The selected set was updated successfully.")

        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please fix your inputs. Details: {e}")

    def delete_selected(self):
        if self.selected_index is None:
            messagebox.showwarning("No Selection", "Please select a row to delete.")
            return
        if not messagebox.askyesno("Delete Set", "Are you sure you want to delete the selected set?"):
            return
        try:
            self.session_log = np.delete(self.session_log, self.selected_index, axis=0)
            self.selected_index = None
            self.update_all_displays()
            for b in (self.load_btn, self.update_btn, self.delete_btn):
                b.state(['disabled'])
            messagebox.showinfo("Deleted", "The selected set was deleted.")
        except Exception as e:
            messagebox.showerror("Delete Error", f"Could not delete the selected row. Details: {e}")


if __name__ == "__main__":
    app = FitnessTrackerApp()
    app.mainloop()
