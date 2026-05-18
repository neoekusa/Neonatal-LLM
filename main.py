from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk
except ModuleNotFoundError as exc:  # pragma: no cover - depends on system Python build.
    print("Tkinter is not available in this Python build.")
    print("Run setup_linux.sh or setup_macos.sh for platform-specific guidance.")
    raise SystemExit(1) from exc

try:
    from PIL import Image, ImageTk
except ImportError:  # pragma: no cover - exercised only when setup has not run.
    Image = None
    ImageTk = None


ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = ROOT / "scripts"
OUTPUTS_DIR = ROOT / "outputs"


class AnalysisApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Neonatology LLM Benchmark Analysis")
        self.geometry("1240x820")
        self.minsize(1040, 700)
        self.configure(bg="#f5f7f8")

        self.output_queue: queue.Queue[str | tuple[str, int]] = queue.Queue()
        self.process: subprocess.Popen[str] | None = None
        self.worker: threading.Thread | None = None
        self.preview_image = None
        self.figure_paths: list[Path] = []

        self._configure_style()
        self._build_layout()
        self.refresh_figures()
        self.after(120, self._drain_output_queue)

    def _configure_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f5f7f8")
        style.configure("Panel.TFrame", background="#ffffff", relief="flat")
        style.configure("TLabel", background="#f5f7f8", foreground="#17202a", font=("Helvetica", 11))
        style.configure("Muted.TLabel", background="#ffffff", foreground="#62717d", font=("Helvetica", 10))
        style.configure("Title.TLabel", background="#f5f7f8", foreground="#102027", font=("Helvetica", 22, "bold"))
        style.configure("Subtitle.TLabel", background="#f5f7f8", foreground="#52616b", font=("Helvetica", 11))
        style.configure("CardTitle.TLabel", background="#ffffff", foreground="#102027", font=("Helvetica", 12, "bold"))
        style.configure("Status.TLabel", background="#ffffff", foreground="#34515e", font=("Helvetica", 10, "bold"))
        style.configure("TButton", font=("Helvetica", 10, "bold"), padding=(14, 9))
        style.map("TButton", background=[("active", "#dfe7ea")])
        style.configure("Primary.TButton", background="#12343b", foreground="#ffffff")
        style.map("Primary.TButton", background=[("active", "#1d4b54")], foreground=[("active", "#ffffff")])
        style.configure("Secondary.TButton", background="#e8eef0", foreground="#12343b")

    def _build_layout(self):
        header = ttk.Frame(self, padding=(28, 24, 28, 12))
        header.pack(fill="x")
        ttk.Label(header, text="Neonatology LLM Benchmark", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Reproduce clustered GEE analyses, regenerate manuscript figures, and inspect outputs.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(5, 0))

        body = ttk.Frame(self, padding=(28, 8, 28, 24))
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=0, minsize=390)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        left = ttk.Frame(body, style="Panel.TFrame", padding=18)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        left.columnconfigure(0, weight=1)

        right = ttk.Frame(body, style="Panel.TFrame", padding=18)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        right.rowconfigure(3, weight=1)

        ttk.Label(left, text="Analysis Controls", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(left, textvariable=self.status_var, style="Status.TLabel").grid(row=1, column=0, sticky="w", pady=(3, 18))

        self.buttons: list[ttk.Button] = []
        self._add_action(
            left,
            row=2,
            title="Run",
            description="Runs core analysis first, then regenerates figures and submission inventory.",
            command=lambda: self.run_pipeline(["run_core_pipeline.py", "run_figure_pipeline.py"]),
            primary=True,
        )
        self._add_action(
            left,
            row=3,
            title="Run Core Only",
            description="Rebuilds model accuracy, GEE/LPM tables, QIC comparisons, Wald tests, and marginal estimates.",
            command=lambda: self.run_pipeline(["run_core_pipeline.py"]),
        )
        self._add_action(
            left,
            row=4,
            title="Run Figure Only",
            description="Regenerates clustering, heatmaps, collinearity plots, question matrices, and package inventory.",
            command=lambda: self.run_pipeline(["run_figure_pipeline.py"]),
        )

        ttk.Separator(left).grid(row=5, column=0, sticky="ew", pady=18)
        ttk.Button(left, text="Refresh Figures", style="Secondary.TButton", command=self.refresh_figures).grid(
            row=6, column=0, sticky="ew"
        )
        ttk.Label(
            left,
            text="Tip: run the core pipeline before figure-only if outputs were removed.",
            style="Muted.TLabel",
            wraplength=330,
        ).grid(row=7, column=0, sticky="w", pady=(12, 0))

        ttk.Label(right, text="Console", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        console_frame = ttk.Frame(right)
        console_frame.grid(row=1, column=0, sticky="nsew", pady=(8, 18))
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        self.console = tk.Text(
            console_frame,
            bg="#0f1720",
            fg="#d8e4e8",
            insertbackground="#d8e4e8",
            relief="flat",
            wrap="word",
            font=("Menlo", 10),
            height=12,
        )
        self.console.grid(row=0, column=0, sticky="nsew")
        console_scroll = ttk.Scrollbar(console_frame, command=self.console.yview)
        console_scroll.grid(row=0, column=1, sticky="ns")
        self.console.configure(yscrollcommand=console_scroll.set)

        ttk.Label(right, text="Figure Viewer", style="CardTitle.TLabel").grid(row=2, column=0, sticky="w")
        viewer = ttk.Frame(right)
        viewer.grid(row=3, column=0, sticky="nsew", pady=(8, 0))
        viewer.columnconfigure(1, weight=1)
        viewer.rowconfigure(0, weight=1)

        list_frame = ttk.Frame(viewer)
        list_frame.grid(row=0, column=0, sticky="ns", padx=(0, 14))
        self.figure_list = tk.Listbox(
            list_frame,
            width=36,
            activestyle="none",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#d4dde1",
            font=("Helvetica", 10),
            exportselection=False,
        )
        self.figure_list.pack(side="left", fill="both", expand=True)
        self.figure_list.bind("<<ListboxSelect>>", lambda _event: self.show_selected_figure())
        figure_scroll = ttk.Scrollbar(list_frame, command=self.figure_list.yview)
        figure_scroll.pack(side="right", fill="y")
        self.figure_list.configure(yscrollcommand=figure_scroll.set)

        preview_frame = ttk.Frame(viewer, style="Panel.TFrame")
        preview_frame.grid(row=0, column=1, sticky="nsew")
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        self.preview = ttk.Label(preview_frame, text="Select a PNG from outputs/", anchor="center", style="Muted.TLabel")
        self.preview.grid(row=0, column=0, sticky="nsew")

    def _add_action(self, parent, row: int, title: str, description: str, command, primary: bool = False):
        card = ttk.Frame(parent, style="Panel.TFrame", padding=(0, 0, 0, 14))
        card.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        card.columnconfigure(1, weight=1)
        button = ttk.Button(
            card,
            text=title,
            style="Primary.TButton" if primary else "Secondary.TButton",
            command=command,
        )
        button.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.buttons.append(button)
        ttk.Label(card, text=description, style="Muted.TLabel", wraplength=225).grid(row=0, column=1, sticky="w")

    def project_python(self) -> Path:
        if os.name == "nt":
            candidate = ROOT / ".venv" / "Scripts" / "python.exe"
        else:
            candidate = ROOT / ".venv" / "bin" / "python"
        return candidate if candidate.exists() else Path(sys.executable)

    def run_pipeline(self, scripts: list[str]):
        if self.worker and self.worker.is_alive():
            self._write_console("A pipeline is already running.\n")
            return
        self.console.delete("1.0", "end")
        self.status_var.set("Running")
        self._set_buttons_enabled(False)
        self.worker = threading.Thread(target=self._run_scripts, args=(scripts,), daemon=True)
        self.worker.start()

    def _run_scripts(self, scripts: list[str]):
        python = self.project_python()
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SCRIPTS_DIR)
        exit_code = 0
        for script in scripts:
            self.output_queue.put(f"\n$ {python} scripts/{script}\n")
            self.process = subprocess.Popen(
                [str(python), str(SCRIPTS_DIR / script)],
                cwd=ROOT,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            assert self.process.stdout is not None
            for line in self.process.stdout:
                self.output_queue.put(line)
            exit_code = self.process.wait()
            if exit_code != 0:
                break
        self.process = None
        self.output_queue.put(("done", exit_code))

    def _drain_output_queue(self):
        try:
            while True:
                item = self.output_queue.get_nowait()
                if isinstance(item, tuple):
                    _, exit_code = item
                    self.status_var.set("Complete" if exit_code == 0 else f"Failed: exit {exit_code}")
                    self._set_buttons_enabled(True)
                    self.refresh_figures()
                else:
                    self._write_console(item)
        except queue.Empty:
            pass
        self.after(120, self._drain_output_queue)

    def _write_console(self, text: str):
        self.console.insert("end", text)
        self.console.see("end")

    def _set_buttons_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for button in self.buttons:
            button.configure(state=state)

    def refresh_figures(self):
        self.figure_paths = sorted(OUTPUTS_DIR.glob("*.png"), key=lambda path: path.name.lower())
        self.figure_list.delete(0, "end")
        for path in self.figure_paths:
            self.figure_list.insert("end", path.name)
        if self.figure_paths:
            self.figure_list.selection_set(0)
            self.show_selected_figure()
        else:
            self.preview.configure(text="No PNG figures found in outputs/", image="")

    def show_selected_figure(self):
        selection = self.figure_list.curselection()
        if not selection:
            return
        path = self.figure_paths[selection[0]]
        if Image is None or ImageTk is None:
            self.preview.configure(text=f"{path.name}\n\nInstall Pillow to enable previews.", image="")
            return
        image = Image.open(path)
        max_w, max_h = 650, 360
        image.thumbnail((max_w, max_h))
        self.preview_image = ImageTk.PhotoImage(image)
        self.preview.configure(image=self.preview_image, text="")


def main():
    app = AnalysisApp()
    app.mainloop()


if __name__ == "__main__":
    main()
