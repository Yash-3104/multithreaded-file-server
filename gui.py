import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("My Application")
        self.configure(bg="#F0F0F0")
        self.minsize(400, 300)

        # Color constants
        self.bg_color = "#F0F0F0"
        self.text_color = "#333333"
        self.button_color = "#4A90E2"
        self.button_hover = "#357ABD"

        # Title label
        title_label = tk.Label(self, text="My Application", font=("Arial", 16, "bold"),
                              bg=self.bg_color, fg=self.text_color)
        title_label.grid(row=0, column=0, columnspan=3, pady=10)

        # Input frame
        input_frame = ttk.LabelFrame(self, text="User Information", padding=10)
        input_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Input widgets
        tk.Label(input_frame, text="Name:", bg=self.bg_color, fg=self.text_color).grid(
            row=0, column=0, sticky="w", padx=5, pady=5)
        name_entry = tk.Entry(input_frame, bg="white", fg=self.text_color)
        name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(input_frame, text="Email:", bg=self.bg_color, fg=self.text_color).grid(
            row=1, column=0, sticky="w", padx=5, pady=5)
        email_entry = tk.Entry(input_frame, bg="white", fg=self.text_color)
        email_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        input_frame.grid_columnconfigure(1, weight=1)

        # Buttons frame
        buttons_frame = tk.Frame(self, bg=self.bg_color)
        buttons_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

        # Load icons
        self.save_icon = ImageTk.PhotoImage(Image.open("icons/save.png").resize((24, 24)))
        self.load_icon = ImageTk.PhotoImage(Image.open("icons/load.png").resize((24, 24)))
        self.process_icon = ImageTk.PhotoImage(Image.open("icons/process.png").resize((24, 24)))

        # Button hover effects
        def on_enter(e):
            e.widget["background"] = self.button_hover

        def on_leave(e):
            e.widget["background"] = self.button_color

        # Buttons
        save_button = tk.Button(buttons_frame, text="Save", image=self.save_icon, compound="left",
                               bg=self.button_color, fg="white", font=("Arial", 12),
                               padx=10, pady=5, relief="flat", command=lambda: self.update_status("Saved"))
        save_button.pack(side="left", padx=5)
        save_button.bind("<Enter>", on_enter)
        save_button.bind("<Leave>", on_leave)

        load_button = tk.Button(buttons_frame, text="Load", image=self.load_icon, compound="left",
                               bg=self.button_color, fg="white", font=("Arial", 12),
                               padx=10, pady=5, relief="flat", command=lambda: self.update_status("Loaded"))
        load_button.pack(side="left", padx=5)
        load_button.bind("<Enter>", on_enter)
        load_button.bind("<Leave>", on_leave)

        process_button = tk.Button(buttons_frame, text="Process", image=self.process_icon, compound="left",
                                  bg=self.button_color, fg="white", font=("Arial", 12),
                                  padx=10, pady=5, relief="flat", command=self.simulate_process)
        process_button.pack(side="left", padx=5)
        process_button.bind("<Enter>", on_enter)
        process_button.bind("<Leave>", on_leave)

        # Status frame
        status_frame = tk.Frame(self, bg=self.bg_color)
        status_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

        self.progress_bar = ttk.Progressbar(status_frame, orient="horizontal", mode="determinate", length=200)
        self.progress_bar.pack(side="left", padx=5)

        self.status_label = tk.Label(status_frame, text="Status: Idle", bg=self.bg_color, fg=self.text_color)
        self.status_label.pack(side="left", padx=5)

        # Configure grid for responsiveness
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def update_status(self, message):
        """Update the status label."""
        self.status_label.config(text=f"Status: {message}")

    def simulate_process(self):
        """Simulate a process with progress bar update."""
        self.update_status("Processing...")
        self.progress_bar["value"] = 0
        for i in range(101):
            self.progress_bar["value"] = i
            self.update()
            self.after(20)  # Simulate work
        self.update_status("Complete")

if __name__ == "__main__":
    app = GUI()
    app.mainloop()