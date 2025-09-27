import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from PIL import Image, ImageTk, ImageDraw
import os
import json
import time
from datetime import datetime
import colorsys
import math
from collections import deque
from pypresence import Presence
import threading
import queue

ctk.set_appearance_mode("dark")

class EclipseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Eclipse")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1E1E1E")
        
        if os.path.exists("eclipse.ico"):
            self.root.iconbitmap("eclipse.ico")
        
        self.bg_color = "#1E1E1E"
        self.fg_color = "#2D2D2D"
        self.hover_color = "#4A4A4A"
        self.text_color = "#D0D0D0"
        self.border_color = "#404040"
        self.canvas_bg = "white"
        
        self.current_color = "#000000"
        self.brush_size = 5
        self.current_tool = "pencil"
        self.last_x, self.last_y = None, None
        self.start_x, self.start_y = None, None
        self.commands = []
        
        self.color_picker_open = False
        self.details_visible = False
        self.canvas_details_visible = False
        self.canvas = None
        self.main_frame = None
        self.canvas_image = None
        self.pil_image = None
        self.color_wheel_image = None
        self.color_wheel_pil = None
        self.canvas_details_var = tk.BooleanVar(value=False)
        
        self.current_file = None
        self.file_name = "Untitled"
        self.file_path = "N/A"
        self.last_edited = "N/A"
        self.file_size = "N/A"
        
        self.discord_rpc = None
        self.rpc_connected = False
        self.rpc_queue = queue.Queue()
        self.rpc_thread = None
        self.rpc_running = True
        self.client_id = "1373063151297368236"
        self.init_discord_rpc()
        
        self.show_splash_screen()
        self.root.after(3000, self.show_starting_page)

    def init_discord_rpc(self):
        try:
            self.discord_rpc = Presence(self.client_id)
            self.discord_rpc.connect()
            self.rpc_connected = True
            self.rpc_thread = threading.Thread(target=self.rpc_update_loop, daemon=True)
            self.rpc_thread.start()
        except Exception as e:
            self.rpc_connected = False

    def update_discord_presence(self, details, state, large_image="eclipse", large_text="Eclipse"):
        if self.rpc_connected:
            self.rpc_queue.put({
                "details": details,
                "state": state,
                "large_image": large_image,
                "large_text": large_text,
                "start": int(time.time())
            })

    def rpc_update_loop(self):
        while self.rpc_running:
            try:
                while not self.rpc_queue.empty():
                    presence_data = self.rpc_queue.get()
                    self.discord_rpc.update(**presence_data)
                time.sleep(15)
            except Exception as e:
                self.rpc_connected = False
                break

    def cleanup_rpc(self):
        self.rpc_running = False
        if self.rpc_connected:
            try:
                self.discord_rpc.close()
            except Exception:
                pass

    def load_logo(self, opacity=1.0):
        logo_path = "eclipse.png"
        if not os.path.exists(logo_path):
            img = Image.new("RGBA", (500, 500), (45, 45, 45, 0))
            draw = ImageDraw.Draw(img)
            draw.text((150, 250), "Eclipse", fill=(208, 208, 208, 255), font_size=50)
        else:
            img = Image.open(logo_path).convert("RGBA")
        
        img_width, img_height = img.size
        max_size = 500
        ratio = min(max_size / img_width, max_size / img_height)
        new_size = (int(img_width * ratio), int(img_height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        data = img.getdata()
        new_data = [(r, g, b, int(a * opacity)) for r, g, b, a in data]
        img.putdata(new_data)
        
        return ctk.CTkImage(img, size=new_size)

    def load_color_wheel(self):
        color_wheel_path = "colorwheel.png"
        if not os.path.exists(color_wheel_path):
            img = Image.new("RGB", (200, 200), color="#2D2D2D")
            draw = ImageDraw.Draw(img)
            center = (100, 100)
            for x in range(200):
                for y in range(200):
                    dx, dy = x - center[0], y - center[1]
                    distance = math.sqrt(dx**2 + dy**2)
                    if 80 <= distance <= 100:
                        angle = (math.atan2(dy, dx) + math.pi) / (2 * math.pi)
                        rgb = colorsys.hls_to_rgb(angle, 0.5, distance / 100)
                        img.putpixel((x, y), tuple(int(255 * c) for c in rgb))
        else:
            img = Image.open(color_wheel_path).resize((200, 200), Image.Resampling.LANCZOS)
        return img

    def show_splash_screen(self):
        self.splash_frame = ctk.CTkFrame(self.root, fg_color=self.bg_color)
        self.splash_frame.pack(fill="both", expand=True)
        
        logo_images = [self.load_logo(opacity=i/10) for i in range(11)]
        self.logo_label = ctk.CTkLabel(self.splash_frame, image=logo_images[0], text="")
        self.logo_label.place(relx=0.5, rely=0.45, anchor="center")
        
        ctk.CTkLabel(
            self.splash_frame,
            text="Welcome to Eclipse\nUnleash Your Creativity",
            font=("Arial", 28, "bold"),
            text_color=self.text_color,
            wraplength=500
        ).place(relx=0.5, rely=0.75, anchor="center")
        
        for i in range(1, 11):
            self.logo_label.configure(image=logo_images[i])
            self.root.update()
            time.sleep(0.2)
        self.update_discord_presence("On Splash Screen", "Starting Eclipse", "logo", "Eclipse")

    def show_starting_page(self):
        self.splash_frame.destroy()
        self.start_frame = ctk.CTkFrame(self.root, fg_color=self.bg_color)
        self.start_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(self.start_frame, image=self.load_logo(), text="").place(relx=0.5, rely=0.5, anchor="center")
        
        overlay_frame = ctk.CTkFrame(
            self.start_frame, fg_color=self.fg_color, corner_radius=12, width=500, height=550,
            border_width=1, border_color=self.border_color
        )
        overlay_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(
            overlay_frame, text="Eclipse\nYour Creative Canvas", font=("Arial", 32, "bold"),
            text_color=self.text_color, wraplength=400, justify="center"
        ).place(relx=0.5, rely=0.15, anchor="center")
        
        ctk.CTkButton(
            overlay_frame, text="New Canvas", command=self.start_new_canvas, fg_color=self.fg_color,
            hover_color=self.hover_color, text_color=self.text_color, width=300, height=50,
            corner_radius=8, font=("Arial", 20), border_width=1, border_color=self.border_color
        ).place(relx=0.5, rely=0.4, anchor="center")
        
        ctk.CTkButton(
            overlay_frame, text="Open File", command=self.open_file, fg_color=self.fg_color,
            hover_color=self.hover_color, text_color=self.text_color, width=300, height=50,
            corner_radius=8, font=("Arial", 20), border_width=1, border_color=self.border_color
        ).place(relx=0.5, rely=0.55, anchor="center")
        
        self.details_switch = ctk.CTkSwitch(
            overlay_frame, text="Show Details", command=self.toggle_details, fg_color=self.fg_color,
            progress_color=self.text_color, text_color=self.text_color, font=("Arial", 14)
        )
        self.details_switch.place(relx=0.5, rely=0.75, anchor="center")
        
        self.details_label = ctk.CTkLabel(
            overlay_frame, text="Made by HJr using Python", font=("Arial", 12), text_color=self.text_color
        )
        self.details_label.place(relx=0.5, rely=0.85, anchor="center")
        self.details_label.place_forget()
        self.update_discord_presence("On Start Page", "Ready to Create", "logo", "Eclipse")

    def setup_main_ui(self):
        self.main_frame = ctk.CTkFrame(self.root, fg_color=self.bg_color)
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        self.menubar = tk.Menu(self.root, bg=self.fg_color, fg=self.text_color,
                              activebackground=self.hover_color, activeforeground=self.text_color)
        self.root.config(menu=self.menubar)
        file_menu = tk.Menu(self.menubar, tearoff=0, bg=self.fg_color, fg=self.text_color,
                           activebackground=self.hover_color, activeforeground=self.text_color)
        self.menubar.add_cascade(label="File", menu=file_menu)
        for label, command in [
            ("New File", self.new_file), ("Save File", self.save_file),
            ("Export to PNG", self.export_to_png), ("Open File", self.open_file),
            ("Back to Start", self.back_to_start)
        ]:
            file_menu.add_command(label=label, command=command)
        
        self.context_menu = tk.Menu(
            self.root, tearoff=0, bg=self.fg_color, fg=self.text_color,
            activebackground=self.hover_color, activeforeground=self.text_color
        )
        self.context_menu.add_command(label="Change Color", command=self.toggle_color_picker)
        self.context_menu.add_command(label="Change Brush Size", command=self.prompt_brush_size)
        
        self.toolbar = ctk.CTkFrame(self.main_frame, fg_color=self.fg_color, corner_radius=5)
        self.toolbar.pack(side="left", fill="y", padx=15, pady=15)
        
        tools = [
            ("Pencil", "pencil", "✏️"), ("Brush", "brush", "🖌️"), ("Eraser", "eraser", "🧽"),
            ("Line", "line", "📏"), ("Rectangle", "rectangle", "⬛"), ("Ellipse", "ellipse", "⭕"),
            ("Text", "text", "🔤"), ("Fill", "fill", "🪣")
        ]
        self.tool_buttons = {}
        for name, tool, icon in tools:
            btn = ctk.CTkButton(
                self.toolbar, text=f"{icon}\n{name}", command=lambda t=tool: self.select_tool(t),
                fg_color=self.fg_color, hover_color=self.hover_color, text_color=self.text_color,
                width=80, height=60, corner_radius=5, font=("Arial", 16),
                border_width=1, border_color=self.border_color
            )
            btn.pack(pady=12, padx=8)
            self.tool_buttons[tool] = btn
            if tool == "brush":
                btn.bind("<Button-3>", lambda e: self.context_menu.post(e.x_root, e.y_root))
        
        self.color_button = ctk.CTkButton(
            self.toolbar, text="🎨\nColor", command=self.toggle_color_picker,
            fg_color=self.fg_color, hover_color=self.hover_color, text_color=self.text_color,
            width=80, height=60, corner_radius=5, font=("Arial", 16),
            border_width=1, border_color=self.border_color
        )
        self.color_button.pack(pady=12, padx=8)
        
        ctk.CTkLabel(self.toolbar, text="Brush Size", text_color=self.text_color, font=("Arial", 14)).pack(pady=8)
        self.brush_slider = ctk.CTkSlider(
            self.toolbar, from_=1, to=50, command=self.update_brush_size,
            progress_color=self.border_color, button_color=self.text_color,
            button_hover_color=self.hover_color, width=80, number_of_steps=49
        )
        self.brush_slider.set(self.brush_size)
        self.brush_slider.pack(pady=8, padx=8)
        
        self.canvas_frame = ctk.CTkFrame(self.main_frame, fg_color=self.fg_color, corner_radius=5)
        self.canvas_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        self.canvas = tk.Canvas(
            self.canvas_frame, bg=self.canvas_bg, width=800, height=600,
            highlightthickness=1, highlightbackground=self.border_color, bd=0
        )
        self.canvas.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.color_picker_frame = ctk.CTkFrame(self.main_frame, fg_color=self.fg_color, corner_radius=5, width=250)
        color_picker_inner = ctk.CTkFrame(self.color_picker_frame, fg_color=self.fg_color)
        color_picker_inner.pack(padx=10, pady=10)
        
        color_scroll = ctk.CTkScrollableFrame(color_picker_inner, fg_color=self.fg_color, width=210, height=300)
        color_scroll.pack(padx=10, pady=10, fill="both")
        
        self.color_wheel_pil = self.load_color_wheel()
        self.color_wheel_image = ImageTk.PhotoImage(self.color_wheel_pil)
        color_wheel_label = tk.Label(color_scroll, image=self.color_wheel_image)
        color_wheel_label.pack(pady=10)
        color_wheel_label.bind("<Button-1>", self.pick_color_from_wheel)
        
        self.hex_entry = ctk.CTkEntry(
            color_picker_inner, placeholder_text="Enter hex color (e.g., #FF0000)",
            fg_color=self.fg_color, text_color=self.text_color, border_color=self.border_color,
            width=200, corner_radius=5
        )
        self.hex_entry.pack(pady=5)
        
        ctk.CTkButton(
            color_picker_inner, text="Apply Hex", command=self.apply_hex_color,
            fg_color=self.fg_color, hover_color=self.hover_color, text_color=self.text_color,
            width=200, height=30, corner_radius=5, font=("Arial", 12),
            border_width=1, border_color=self.border_color
        ).pack(pady=5)
        
        self.color_preview = ctk.CTkLabel(
            color_picker_inner, text="", fg_color=self.current_color,
            width=200, height=30, corner_radius=5
        )
        self.color_preview.pack(pady=5)
        
        self.color_picker_frame.pack_forget()
        
        self.canvas_details_switch = ctk.CTkSwitch(
            self.main_frame, text="Show Details", command=self.toggle_canvas_details,
            fg_color=self.fg_color, progress_color=self.text_color, text_color=self.text_color,
            font=("Arial", 14)
        )
        self.canvas_details_switch.place(relx=0.95, rely=0.05, anchor="ne")
        
        self.canvas_details_label = ctk.CTkLabel(
            self.main_frame, text=self.get_canvas_details(), font=("Arial", 12),
            text_color=self.text_color, justify="right"
        )
        self.canvas_details_label.place_forget()
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        self.update_discord_presence(f"Drawing on {self.file_name}", f"Using {self.current_tool.capitalize()}", self.current_tool, f"Eclipse - {self.current_tool.capitalize()}")

    def toggle_details(self):
        self.details_visible = not self.details_visible
        if self.details_visible:
            self.details_label.place(relx=0.5, rely=0.85, anchor="center")
        else:
            self.details_label.place_forget()

    def toggle_canvas_details(self):
        self.canvas_details_visible = not self.canvas_details_visible
        if self.canvas_details_visible:
            self.canvas_details_label.configure(text=self.get_canvas_details())
            self.canvas_details_label.place(relx=0.95, rely=0.1, anchor="ne")
        else:
            self.canvas_details_label.place_forget()

    def toggle_color_picker(self):
        self.color_picker_open = not self.color_picker_open
        if self.color_picker_open:
            self.color_picker_frame.pack(side="right", fill="y", padx=15, pady=15)
            self.color_button.configure(text="🎨\nClose")
            self.update_discord_presence(f"Drawing on {self.file_name}", "Picking Color", "logo", "Eclipse - Color Picker")
        else:
            self.color_picker_frame.pack_forget()
            self.color_button.configure(text="🎨\nColor")
            self.update_discord_presence(f"Drawing on {self.file_name}", f"Using {self.current_tool.capitalize()}", self.current_tool, f"Eclipse - {self.current_tool.capitalize()}")

    def start_new_canvas(self):
        self.start_frame.destroy()
        self.current_file = None
        self.file_name = "Untitled"
        self.file_path = "N/A"
        self.last_edited = "N/A"
        self.file_size = "N/A"
        self.setup_main_ui()

    def back_to_start(self):
        if self.main_frame:
            self.main_frame.destroy()
            self.menubar.destroy()
            self.canvas = None
            self.commands = []
            self.canvas_image = None
            self.pil_image = None
            self.current_file = None
            self.file_name = "Untitled"
            self.file_path = "N/A"
            self.last_edited = "N/A"
            self.file_size = "N/A"
            self.show_starting_page()

    def select_tool(self, tool):
        self.current_tool = tool
        self.canvas.bind("<Button-1>", self.place_text if tool == "text" else self.on_press)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.update_discord_presence(f"Drawing on {self.file_name}", f"Using {self.current_tool.capitalize()}", self.current_tool, f"Eclipse - {self.current_tool.capitalize()}")

    def place_text(self, event):
        text = simpledialog.askstring("Input", "Enter text:", parent=self.root)
        if text:
            coords = (event.x, event.y)
            self.canvas.create_text(
                coords, text=text, fill=self.current_color, font=("Arial", self.brush_size * 2)
            )
            self.commands.append({
                'type': 'text', 'coords': list(coords), 'text': text,
                'fill': self.current_color, 'font': ("Arial", self.brush_size * 2)
            })

    def flood_fill(self, image, x, y, fill_color, tolerance=10):
        if not (0 <= x < image.width and 0 <= y < image.height):
            return image
        target_color = image.getpixel((x, y))
        if target_color == fill_color:
            return image
        width, height = image.size
        queue = deque([(x, y)])
        visited = set()
        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))
            if 0 <= cx < width and 0 <= cy < height:
                current = image.getpixel((cx, cy))
                if all(abs(a - b) <= tolerance for a, b in zip(target_color[:3], current[:3])):
                    image.putpixel((cx, cy), fill_color)
                    queue.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])
        return image

    def on_press(self, event):
        if self.current_tool in ["pencil", "brush", "eraser", "line", "rectangle", "ellipse"]:
            self.start_x, self.start_y = event.x, event.y
            self.last_x, self.last_y = event.x, event.y

    def on_motion(self, event):
        if self.last_x is None or self.last_y is None:
            return
        if self.current_tool == "pencil":
            coords = (self.last_x, self.last_y, event.x, event.y)
            self.canvas.create_line(
                coords, fill=self.current_color, width=self.brush_size, capstyle="round", smooth=True
            )
            self.commands.append({
                'type': 'line', 'coords': list(coords), 'fill': self.current_color,
                'width': self.brush_size, 'capstyle': 'round', 'smooth': True
            })
        elif self.current_tool == "brush":
            coords = (self.last_x, self.last_y, event.x, event.y)
            self.canvas.create_line(
                coords, fill=self.current_color, width=self.brush_size * 1.5,
                capstyle="round", smooth=True, stipple="gray50"
            )
            self.commands.append({
                'type': 'brush', 'coords': list(coords), 'fill': self.current_color,
                'width': self.brush_size * 1.5, 'capstyle': 'round', 'smooth': True,
                'stipple': 'gray50'
            })
        elif self.current_tool == "eraser":
            coords = (self.last_x, self.last_y, event.x, event.y)
            self.canvas.create_line(
                coords, fill=self.canvas_bg, width=self.brush_size, capstyle="round", smooth=True
            )
            self.commands.append({
                'type': 'line', 'coords': list(coords), 'fill': self.canvas_bg,
                'width': self.brush_size, 'capstyle': 'round', 'smooth': True
            })
        self.last_x, self.last_y = event.x, event.y

    def on_release(self, event):
        if self.start_x is None or self.start_y is None:
            return
        if self.current_tool == "line":
            coords = (self.start_x, self.start_y, event.x, event.y)
            self.canvas.create_line(coords, fill=self.current_color, width=self.brush_size)
            self.commands.append({
                'type': 'line', 'coords': list(coords), 'fill': self.current_color,
                'width': self.brush_size, 'capstyle': 'projecting', 'smooth': False
            })
        elif self.current_tool == "rectangle":
            coords = (self.start_x, self.start_y, event.x, event.y)
            self.canvas.create_rectangle(coords, outline=self.current_color, width=self.brush_size)
            self.commands.append({
                'type': 'rectangle', 'coords': list(coords), 'outline': self.current_color,
                'width': self.brush_size
            })
        elif self.current_tool == "ellipse":
            coords = (self.start_x, self.start_y, event.x, event.y)
            self.canvas.create_oval(coords, outline=self.current_color, width=self.brush_size)
            self.commands.append({
                'type': 'ellipse', 'coords': list(coords), 'outline': self.current_color,
                'width': self.brush_size
            })
        elif self.current_tool == "fill":
            composite = self.get_composite()
            x, y = event.x, event.y
            fill_rgb = tuple(int(self.current_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            fill_color = fill_rgb + (255,)
            try:
                composite = self.flood_fill(composite, x, y, fill_color, tolerance=10)
                self.pil_image = composite
                self.canvas.delete("all")
                self.canvas_image = ImageTk.PhotoImage(composite.convert("RGB"))
                self.canvas.create_image(0, 0, anchor="nw", image=self.canvas_image)
                self.canvas.image = self.canvas_image
                self.commands = []
                messagebox.showinfo("Success", "Fill applied")
            except Exception as e:
                messagebox.showerror("Error", f"Fill error: {e}")
        self.last_x, self.last_y = None, None
        self.start_x, self.start_y = None, None

    def pick_color_from_wheel(self, event):
        x, y = event.x, event.y
        try:
            pixel = self.color_wheel_pil.getpixel((x, y))
            hex_color = '#{:02x}{:02x}{:02x}'.format(*pixel)
            if hex_color != "#2d2d2d":
                self.set_color(hex_color)
                self.hex_entry.delete(0, tk.END)
                self.hex_entry.insert(0, hex_color)
                self.update_discord_presence(f"Drawing on {self.file_name}", "Picking Color", "logo", "Eclipse - Color Picker")
        except Exception:
            pass

    def set_color(self, color):
        self.current_color = color
        self.color_preview.configure(fg_color=self.current_color)
        if not self.color_picker_open:
            self.update_discord_presence(f"Drawing on {self.file_name}", f"Using {self.current_tool.capitalize()}", self.current_tool, f"Eclipse - {self.current_tool.capitalize()}")

    def apply_hex_color(self):
        hex_color = self.hex_entry.get().strip()
        if len(hex_color) == 7 and hex_color.startswith("#") and all(c in "0123456789ABCDEFabcdef" for c in hex_color[1:]):
            self.set_color(hex_color)

    def prompt_brush_size(self):
        size = simpledialog.askinteger("Brush Size", "Enter brush size (1-50):", parent=self.root, minvalue=1, maxvalue=50)
        if size is not None:
            self.brush_size = size
            self.brush_slider.set(size)
            self.update_discord_presence(f"Drawing on {self.file_name}", f"Using {self.current_tool.capitalize()} (Size: {self.brush_size})", self.current_tool, f"Eclipse - {self.current_tool.capitalize()}")

    def update_brush_size(self, value):
        self.brush_size = int(value)
        self.update_discord_presence(f"Drawing on {self.file_name}", f"Using {self.current_tool.capitalize()} (Size: {self.brush_size})", self.current_tool, f"Eclipse - {self.current_tool.capitalize()}")

    def get_canvas_details(self):
        return f"Image: {self.file_name}\nPath: {self.file_path}\nLast Edited: {self.last_edited}\nSize: {self.file_size}"

    def update_file_details(self, file_path):
        self.current_file = file_path
        self.file_name = os.path.basename(file_path)
        self.file_path = file_path
        try:
            stat = os.stat(file_path)
            self.last_edited = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            size_bytes = stat.st_size
            self.file_size = f"{size_bytes / 1024:.2f} KB" if size_bytes < 1024 * 1024 else f"{size_bytes / (1024 * 1024):.2f} MB"
        except Exception:
            self.last_edited = "N/A"
            self.file_size = "N/A"
        self.update_discord_presence(f"Drawing on {self.file_name}", f"Using {self.current_tool.capitalize()}", self.current_tool, f"Eclipse - {self.current_tool.capitalize()}")

    def new_file(self):
        if self.canvas:
            self.canvas.delete("all")
            self.commands = []
            self.canvas_image = None
            self.pil_image = None
            self.current_file = None
            self.file_name = "Untitled"
            self.file_path = "N/A"
            self.last_edited = "N/A"
            self.file_size = "N/A"
            self.canvas_details_label.configure(text=self.get_canvas_details())
            self.update_discord_presence(f"Drawing on {self.file_name}", f"Using {self.current_tool.capitalize()}", self.current_tool, f"Eclipse - {self.current_tool.capitalize()}")

    def save_file(self):
        if not self.canvas:
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".ecp", filetypes=[("Eclipse files", "*.ecp"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.commands, f, indent=2)
                self.update_file_details(file_path)
                self.canvas_details_label.configure(text=self.get_canvas_details())
                messagebox.showinfo("Success", f"Saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Save error: {e}")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Eclipse files", "*.ecp"), ("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            if not self.canvas:
                self.start_frame.destroy()
                self.setup_main_ui()
            self.canvas.delete("all")
            self.commands = []
            self.canvas_image = None
            self.pil_image = None
            try:
                if file_path.endswith('.png'):
                    img = Image.open(file_path).resize((800, 600), Image.Resampling.LANCZOS)
                    self.pil_image = img
                    self.canvas_image = ImageTk.PhotoImage(img)
                    self.canvas.create_image(0, 0, anchor="nw", image=self.canvas_image)
                    self.canvas.image = self.canvas_image
                else:
                    with open(file_path, 'r') as f:
                        self.commands = json.load(f)
                    self.replay_commands()
                self.update_file_details(file_path)
                self.canvas_details_label.configure(text=self.get_canvas_details())
                messagebox.showinfo("Success", f"Opened {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Open error: {e}")

    def export_to_png(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            try:
                composite = self.get_composite().convert("RGB")
                composite.save(file_path, "PNG")
                self.update_file_details(file_path)
                messagebox.showinfo("Success", f"Exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Export PNG error: {e}")

    def get_composite(self):
        if not self.pil_image:
            self.pil_image = Image.new("RGBA", (800, 600), (255, 255, 255, 255))
        
        draw = ImageDraw.Draw(self.pil_image)
        for cmd in self.commands:
            if cmd['type'] in ['line', 'brush']:
                x1, y1, x2, y2 = cmd['coords']
                fill_rgb = tuple(int(cmd['fill'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                draw.line(
                    [(x1, y1), (x2, y2)], fill=fill_rgb + (255,),
                    width=int(cmd['width']), joint="curve" if cmd.get('smooth', False) else None
                )
            elif cmd['type'] == 'rectangle':
                x1, y1, x2, y2 = cmd['coords']
                outline_rgb = tuple(int(cmd['outline'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                draw.rectangle(
                    [(min(x1, x2), min(y1, y2)), (max(x1, x2), max(y1, y2))],
                    outline=outline_rgb + (255,), width=int(cmd['width'])
                )
            elif cmd['type'] == 'ellipse':
                x1, y1, x2, y2 = cmd['coords']
                outline_rgb = tuple(int(cmd['outline'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                draw.ellipse(
                    [(min(x1, x2), min(y1, y2)), (max(x1, x2), max(y1, y2))],
                    outline=outline_rgb + (255,), width=int(cmd['width'])
                )
            elif cmd['type'] == 'text':
                x, y = cmd['coords']
                fill_rgb = tuple(int(cmd['fill'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                try:
                    draw.text((x, y), cmd['text'], fill=fill_rgb + (255,), font_size=cmd['font'][1])
                except TypeError:
                    draw.text((x, y), cmd['text'], fill=fill_rgb + (255,))
        return self.pil_image

    def replay_commands(self):
        try:
            for cmd in self.commands:
                if not isinstance(cmd, dict) or 'type' not in cmd or 'coords' not in cmd:
                    continue
                if cmd['type'] in ['line', 'brush']:
                    self.canvas.create_line(
                        cmd['coords'], fill=cmd.get('fill', '#000000'), width=cmd.get('width', 1),
                        capstyle=cmd.get('capstyle', 'projecting'), smooth=cmd.get('smooth', False),
                        stipple=cmd.get('stipple', '')
                    )
                elif cmd['type'] == 'rectangle':
                    self.canvas.create_rectangle(
                        cmd['coords'], outline=cmd.get('outline', '#000000'), width=cmd.get('width', 1)
                    )
                elif cmd['type'] == 'ellipse':
                    self.canvas.create_oval(
                        cmd['coords'], outline=cmd.get('outline', '#000000'), width=cmd.get('width', 1)
                    )
                elif cmd['type'] == 'text':
                    self.canvas.create_text(
                        cmd['coords'], text=cmd.get('text', ''), fill=cmd.get('fill', '#000000'),
                        font=cmd.get('font', ("Arial", 10))
                    )
        except Exception as e:
            messagebox.showerror("Error", f"Replay error: {e}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = EclipseApp(root)
    try:
        root.mainloop()
    finally:
        app.cleanup_rpc()
