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
    def __init__(self, window):
        self.window = window
        self.window.title("Eclipse")
        self.window.geometry("1200x800")
        self.window.configure(bg="#212121")
        
        if os.path.exists("eclipse.ico"):
            self.window.iconbitmap("eclipse.ico")
        
        self.main_bg = "#212121"
        self.panel_bg = "#2A2A2A"
        self.hover_shade = "#454545"
        self.text_shade = "#D4D4D4"
        self.border_shade = "#3C3C3C"
        self.drawing_surface = "white"
        
        self.active_color = "#000000"
        self.brush_thickness = 5
        self.active_tool = "pen"
        self.prev_x, self.prev_y = None, None
        self.start_x, self.start_y = None, None
        self.draw_history = []
        
        self.is_color_panel_open = False
        self.show_info = False
        self.show_canvas_info = False
        self.drawing_area = None
        self.main_container = None
        self.canvas_img = None
        self.image_data = None
        self.color_circle_img = None
        self.color_circle_data = None
        self.canvas_info_toggle = tk.BooleanVar(value=False)
        
        self.active_file = None
        self.file_title = "Unnamed"
        self.file_location = "N/A"
        self.last_modified = "N/A"
        self.file_size_info = "N/A"
        
        self.discord_client = None
        self.discord_active = False
        self.discord_queue = queue.Queue()
        self.discord_thread = None
        self.discord_running = True
        self.app_id = "1373063151297368236"
        self.start_discord()
        
        self.display_welcome()
        self.window.after(3000, self.show_home_page)

    def start_discord(self):
        try:
            self.discord_client = Presence(self.app_id)
            self.discord_client.connect()
            self.discord_active = True
            self.discord_thread = threading.Thread(target=self.discord_loop, daemon=True)
            self.discord_thread.start()
        except Exception:
            self.discord_active = False

    def update_discord_status(self, activity, status, icon="eclipse", icon_text="Eclipse"):
        if self.discord_active:
            self.discord_queue.put({
                "details": activity,
                "state": status,
                "large_image": icon,
                "large_text": icon_text,
                "start": int(time.time())
            })

    def discord_loop(self):
        while self.discord_running:
            try:
                while not self.discord_queue.empty():
                    status_data = self.discord_queue.get()
                    self.discord_client.update(**status_data)
                time.sleep(15)
            except Exception:
                self.discord_active = False
                break

    def shutdown_discord(self):
        self.discord_running = False
        if self.discord_active:
            try:
                self.discord_client.close()
            except Exception:
                pass

    def load_app_logo(self, fade=1.0):
        logo_file = "eclipse.png"
        if not os.path.exists(logo_file):
            img = Image.new("RGBA", (500, 500), (40, 40, 40, 0))
            draw = ImageDraw.Draw(img)
            draw.text((140, 240), "Eclipse", fill=(210, 210, 210, 255), font_size=48)
        else:
            img = Image.open(logo_file).convert("RGBA")
        
        img_w, img_h = img.size
        max_dim = 500
        scale = min(max_dim / img_w, max_dim / img_h)
        new_dims = (int(img_w * scale), int(img_h * scale))
        img = img.resize(new_dims, Image.Resampling.LANCZOS)
        
        pixels = img.getdata()
        updated_pixels = [(r, g, b, int(a * fade)) for r, g, b, a in pixels]
        img.putdata(updated_pixels)
        
        return ctk.CTkImage(img, size=new_dims)

    def load_color_circle(self):
        color_file = "colorcircle.png"
        if not os.path.exists(color_file):
            img = Image.new("RGB", (200, 200), color="#2A2A2A")
            draw = ImageDraw.Draw(img)
            center = (100, 100)
            for x in range(200):
                for y in range(200):
                    dx, dy = x - center[0], y - center[1]
                    dist = math.sqrt(dx**2 + dy**2)
                    if 80 <= dist <= 100:
                        angle = (math.atan2(dy, dx) + math.pi) / (2 * math.pi)
                        rgb = colorsys.hls_to_rgb(angle, 0.5, dist / 100)
                        img.putpixel((x, y), tuple(int(255 * c) for c in rgb))
        else:
            img = Image.open(color_file).resize((200, 200), Image.Resampling.LANCZOS)
        return img

    def display_welcome(self):
        self.welcome_panel = ctk.CTkFrame(self.window, fg_color=self.main_bg)
        self.welcome_panel.pack(fill="both", expand=True)
        
        logo_frames = [self.load_app_logo(fade=i/10) for i in range(11)]
        self.logo_display = ctk.CTkLabel(self.welcome_panel, image=logo_frames[0], text="")
        self.logo_display.place(relx=0.5, rely=0.45, anchor="center")
        
        ctk.CTkLabel(
            self.welcome_panel,
            text="Welcome to Eclipse\nUnleash Your Art",
            font=("Arial", 28, "bold"),
            text_color=self.text_shade,
            wraplength=500
        ).place(relx=0.5, rely=0.75, anchor="center")
        
        for i in range(1, 11):
            self.logo_display.configure(image=logo_frames[i])
            self.window.update()
            time.sleep(0.2)
        self.update_discord_status("On Welcome Screen", "Starting Eclipse", "logo", "Eclipse")

    def show_home_page(self):
        self.welcome_panel.destroy()
        self.home_panel = ctk.CTkFrame(self.window, fg_color=self.main_bg)
        self.home_panel.pack(fill="both", expand=True)
        
        ctk.CTkLabel(self.home_panel, image=self.load_app_logo(), text="").place(relx=0.5, rely=0.5, anchor="center")
        
        overlay = ctk.CTkFrame(
            self.home_panel, fg_color=self.panel_bg, corner_radius=12, width=500, height=550,
            border_width=1, border_color=self.border_shade
        )
        overlay.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(
            overlay, text="Eclipse\nYour Artistic Space", font=("Arial", 32, "bold"),
            text_color=self.text_shade, wraplength=400, justify="center"
        ).place(relx=0.5, rely=0.15, anchor="center")
        
        ctk.CTkButton(
            overlay, text="New Canvas", command=self.create_new_canvas, fg_color=self.panel_bg,
            hover_color=self.hover_shade, text_color=self.text_shade, width=300, height=50,
            corner_radius=8, font=("Arial", 20), border_width=1, border_color=self.border_shade
        ).place(relx=0.5, rely=0.4, anchor="center")
        
        ctk.CTkButton(
            overlay, text="Open Artwork", command=self.load_file, fg_color=self.panel_bg,
            hover_color=self.hover_shade, text_color=self.text_shade, width=300, height=50,
            corner_radius=8, font=("Arial", 20), border_width=1, border_color=self.border_shade
        ).place(relx=0.5, rely=0.55, anchor="center")
        
        self.info_toggle = ctk.CTkSwitch(
            overlay, text="Show Info", command=self.toggle_info, fg_color=self.panel_bg,
            progress_color=self.text_shade, text_color=self.text_shade, font=("Arial", 14)
        )
        self.info_toggle.place(relx=0.5, rely=0.75, anchor="center")
        
        self.info_label = ctk.CTkLabel(
            overlay, text="Crafted by HJr with Python", font=("Arial", 12), text_color=self.text_shade
        )
        self.info_label.place(relx=0.5, rely=0.85, anchor="center")
        self.info_label.place_forget()
        self.update_discord_status("On Home Page", "Ready to Create", "logo", "Eclipse")

    def setup_drawing_ui(self):
        self.main_container = ctk.CTkFrame(self.window, fg_color=self.main_bg)
        self.main_container.pack(fill="both", expand=True, padx=30, pady=30)
        
        self.menu_bar = tk.Menu(self.window, bg=self.panel_bg, fg=self.text_shade,
                              activebackground=self.hover_shade, activeforeground=self.text_shade)
        self.window.config(menu=self.menu_bar)
        file_menu = tk.Menu(self.menu_bar, tearoff=0, bg=self.panel_bg, fg=self.text_shade,
                           activebackground=self.hover_shade, activeforeground=self.text_shade)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        for name, action in [
            ("New Artwork", self.new_artwork), ("Save Artwork", self.save_artwork),
            ("Export as PNG", self.export_png), ("Open Artwork", self.load_file),
            ("Back to Home", self.return_to_home)
        ]:
            file_menu.add_command(label=name, command=action)
        
        self.right_click_menu = tk.Menu(
            self.window, tearoff=0, bg=self.panel_bg, fg=self.text_shade,
            activebackground=self.hover_shade, activeforeground=self.text_shade
        )
        self.right_click_menu.add_command(label="Pick Color", command=self.toggle_color_panel)
        self.right_click_menu.add_command(label="Adjust Brush", command=self.set_brush_size)
        
        self.tools_panel = ctk.CTkFrame(self.main_container, fg_color=self.panel_bg, corner_radius=5)
        self.tools_panel.pack(side="left", fill="y", padx=15, pady=15)
        
        toolset = [
            ("Pen", "pen", "✏️"), ("Brush", "brush", "🖌️"), ("Eraser", "eraser", "🧽"),
            ("Line", "line", "📏"), ("Box", "box", "⬛"), ("Circle", "circle", "⭕"),
            ("Text", "text", "🔤"), ("Fill", "fill", "🪣")
        ]
        self.tool_btns = {}
        for name, tool, icon in toolset:
            btn = ctk.CTkButton(
                self.tools_panel, text=f"{icon}\n{name}", command=lambda t=tool: self.choose_tool(t),
                fg_color=self.panel_bg, hover_color=self.hover_shade, text_color=self.text_shade,
                width=80, height=60, corner_radius=5, font=("Arial", 16),
                border_width=1, border_color=self.border_shade
            )
            btn.pack(pady=12, padx=8)
            self.tool_btns[tool] = btn
            if tool == "brush":
                btn.bind("<Button-3>", lambda e: self.right_click_menu.post(e.x_root, e.y_root))
        
        self.color_btn = ctk.CTkButton(
            self.tools_panel, text="🎨\nColor", command=self.toggle_color_panel,
            fg_color=self.panel_bg, hover_color=self.hover_shade, text_color=self.text_shade,
            width=80, height=60, corner_radius=5, font=("Arial", 16),
            border_width=1, border_color=self.border_shade
        )
        self.color_btn.pack(pady=12, padx=8)
        
        ctk.CTkLabel(self.tools_panel, text="Brush Size", text_color=self.text_shade, font=("Arial", 14)).pack(pady=8)
        self.brush_adjuster = ctk.CTkSlider(
            self.tools_panel, from_=1, to=50, command=self.adjust_brush,
            progress_color=self.border_shade, button_color=self.text_shade,
            button_hover_color=self.hover_shade, width=80, number_of_steps=49
        )
        self.brush_adjuster.set(self.brush_thickness)
        self.brush_adjuster.pack(pady=8, padx=8)
        
        self.canvas_container = ctk.CTkFrame(self.main_container, fg_color=self.panel_bg, corner_radius=5)
        self.canvas_container.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        self.drawing_area = tk.Canvas(
            self.canvas_container, bg=self.drawing_surface, width=800, height=600,
            highlightthickness=1, highlightbackground=self.border_shade, bd=0
        )
        self.drawing_area.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.color_panel = ctk.CTkFrame(self.main_container, fg_color=self.panel_bg, corner_radius=5, width=250)
        color_inner = ctk.CTkFrame(self.color_panel, fg_color=self.panel_bg)
        color_inner.pack(padx=10, pady=10)
        
        color_scroll = ctk.CTkScrollableFrame(color_inner, fg_color=self.panel_bg, width=210, height=300)
        color_scroll.pack(padx=10, pady=10, fill="both")
        
        self.color_circle_data = self.load_color_circle()
        self.color_circle_img = ImageTk.PhotoImage(self.color_circle_data)
        color_circle_label = tk.Label(color_scroll, image=self.color_circle_img)
        color_circle_label.pack(pady=10)
        color_circle_label.bind("<Button-1>", self.select_color_from_circle)
        
        self.hex_input = ctk.CTkEntry(
            color_inner, placeholder_text="Enter hex color (e.g., #FF0000)",
            fg_color=self.panel_bg, text_color=self.text_shade, border_color=self.border_shade,
            width=200, corner_radius=5
        )
        self.hex_input.pack(pady=5)
        
        ctk.CTkButton(
            color_inner, text="Apply Hex", command=self.apply_hex,
            fg_color=self.panel_bg, hover_color=self.hover_shade, text_color=self.text_shade,
            width=200, height=30, corner_radius=5, font=("Arial", 12),
            border_width=1, border_color=self.border_shade
        ).pack(pady=5)
        
        self.color_sample = ctk.CTkLabel(
            color_inner, text="", fg_color=self.active_color,
            width=200, height=30, corner_radius=5
        )
        self.color_sample.pack(pady=5)
        
        self.color_panel.pack_forget()
        
        self.canvas_info_switch = ctk.CTkSwitch(
            self.main_container, text="Show Details", command=self.toggle_canvas_info,
            fg_color=self.panel_bg, progress_color=self.text_shade, text_color=self.text_shade,
            font=("Arial", 14)
        )
        self.canvas_info_switch.place(relx=0.95, rely=0.05, anchor="ne")
        
        self.canvas_info_label = ctk.CTkLabel(
            self.main_container, text=self.get_canvas_info(), font=("Arial", 12),
            text_color=self.text_shade, justify="right"
        )
        self.canvas_info_label.place_forget()
        
        self.drawing_area.bind("<ButtonPress-1>", self.start_drawing)
        self.drawing_area.bind("<B1-Motion>", self.draw_motion)
        self.drawing_area.bind("<ButtonRelease-1>", self.stop_drawing)
        
        self.update_discord_status(f"Drawing on {self.file_title}", f"Using {self.active_tool.capitalize()}", self.active_tool, f"Eclipse - {self.active_tool.capitalize()}")

    def toggle_info(self):
        self.show_info = not self.show_info
        if self.show_info:
            self.info_label.place(relx=0.5, rely=0.85, anchor="center")
        else:
            self.info_label.place_forget()

    def toggle_canvas_info(self):
        self.show_canvas_info = not self.show_canvas_info
        if self.show_canvas_info:
            self.canvas_info_label.configure(text=self.get_canvas_info())
            self.canvas_info_label.place(relx=0.95, rely=0.1, anchor="ne")
        else:
            self.canvas_info_label.place_forget()

    def toggle_color_panel(self):
        self.is_color_panel_open = not self.is_color_panel_open
        if self.is_color_panel_open:
            self.color_panel.pack(side="right", fill="y", padx=15, pady=15)
            self.color_btn.configure(text="🎨\nClose")
            self.update_discord_status(f"Drawing on {self.file_title}", "Choosing Color", "logo", "Eclipse - Color Picker")
        else:
            self.color_panel.pack_forget()
            self.color_btn.configure(text="🎨\nColor")
            self.update_discord_status(f"Drawing on {self.file_title}", f"Using {self.active_tool.capitalize()}", self.active_tool, f"Eclipse - {self.active_tool.capitalize()}")

    def create_new_canvas(self):
        self.home_panel.destroy()
        self.active_file = None
        self.file_title = "Unnamed"
        self.file_location = "N/A"
        self.last_modified = "N/A"
        self.file_size_info = "N/A"
        self.setup_drawing_ui()

    def return_to_home(self):
        if self.main_container:
            self.main_container.destroy()
            self.menu_bar.destroy()
            self.drawing_area = None
            self.draw_history = []
            self.canvas_img = None
            self.image_data = None
            self.active_file = None
            self.file_title = "Unnamed"
            self.file_location = "N/A"
            self.last_modified = "N/A"
            self.file_size_info = "N/A"
            self.show_home_page()

    def choose_tool(self, tool):
        self.active_tool = tool
        self.drawing_area.bind("<Button-1>", self.add_text if tool == "text" else self.start_drawing)
        self.drawing_area.bind("<ButtonPress-1>", self.start_drawing)
        self.drawing_area.bind("<B1-Motion>", self.draw_motion)
        self.drawing_area.bind("<ButtonRelease-1>", self.stop_drawing)
        self.update_discord_status(f"Drawing on {self.file_title}", f"Using {self.active_tool.capitalize()}", self.active_tool, f"Eclipse - {self.active_tool.capitalize()}")

    def add_text(self, event):
        text_input = simpledialog.askstring("Text", "Enter text:", parent=self.window)
        if text_input:
            pos = (event.x, event.y)
            self.drawing_area.create_text(
                pos, text=text_input, fill=self.active_color, font=("Arial", self.brush_thickness * 2)
            )
            self.draw_history.append({
                'type': 'text', 'coords': list(pos), 'text': text_input,
                'fill': self.active_color, 'font': ("Arial", self.brush_thickness * 2)
            })

    def apply_flood_fill(self, img, x, y, new_color, tolerance=10):
        if not (0 <= x < img.width and 0 <= y < img.height):
            return img
        base_color = img.getpixel((x, y))
        if base_color == new_color:
            return img
        w, h = img.size
        pending = deque([(x, y)])
        seen = set()
        while pending:
            cx, cy = pending.popleft()
            if (cx, cy) in seen:
                continue
            seen.add((cx, cy))
            if 0 <= cx < w and 0 <= cy < h:
                current = img.getpixel((cx, cy))
                if all(abs(a - b) <= tolerance for a, b in zip(base_color[:3], current[:3])):
                    img.putpixel((cx, cy), new_color)
                    pending.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])
        return img

    def start_drawing(self, event):
        if self.active_tool in ["pen", "brush", "eraser", "line", "box", "circle"]:
            self.start_x, self.start_y = event.x, event.y
            self.prev_x, self.prev_y = event.x, event.y

    def draw_motion(self, event):
        if self.prev_x is None or self.prev_y is None:
            return
        if self.active_tool == "pen":
            line_coords = (self.prev_x, self.prev_y, event.x, event.y)
            self.drawing_area.create_line(
                line_coords, fill=self.active_color, width=self.brush_thickness, capstyle="round", smooth=True
            )
            self.draw_history.append({
                'type': 'line', 'coords': list(line_coords), 'fill': self.active_color,
                'width': self.brush_thickness, 'capstyle': 'round', 'smooth': True
            })
        elif self.active_tool == "brush":
            line_coords = (self.prev_x, self.prev_y, event.x, event.y)
            self.drawing_area.create_line(
                line_coords, fill=self.active_color, width=self.brush_thickness * 1.5,
                capstyle="round", smooth=True
            )
            self.draw_history.append({
                'type': 'brush', 'coords': list(line_coords), 'fill': self.active_color,
                'width': self.brush_thickness * 1.5, 'capstyle': 'round', 'smooth': True
            })
        elif self.active_tool == "eraser":
            line_coords = (self.prev_x, self.prev_y, event.x, event.y)
            self.drawing_area.create_line(
                line_coords, fill=self.drawing_surface, width=self.brush_thickness, capstyle="round", smooth=True
            )
            self.draw_history.append({
                'type': 'line', 'coords': list(line_coords), 'fill': self.drawing_surface,
                'width': self.brush_thickness, 'capstyle': 'round', 'smooth': True
            })
        self.prev_x, self.prev_y = event.x, event.y

    def stop_drawing(self, event):
        if self.start_x is None or self.start_y is None:
            return
        if self.active_tool == "line":
            line_coords = (self.start_x, self.start_y, event.x, event.y)
            self.drawing_area.create_line(line_coords, fill=self.active_color, width=self.brush_thickness)
            self.draw_history.append({
                'type': 'line', 'coords': list(line_coords), 'fill': self.active_color,
                'width': self.brush_thickness, 'capstyle': 'projecting', 'smooth': False
            })
        elif self.active_tool == "box":
            box_coords = (self.start_x, self.start_y, event.x, event.y)
            self.drawing_area.create_rectangle(box_coords, outline=self.active_color, width=self.brush_thickness)
            self.draw_history.append({
                'type': 'rectangle', 'coords': list(box_coords), 'outline': self.active_color,
                'width': self.brush_thickness
            })
        elif self.active_tool == "circle":
            circle_coords = (self.start_x, self.start_y, event.x, event.y)
            self.drawing_area.create_oval(circle_coords, outline=self.active_color, width=self.brush_thickness)
            self.draw_history.append({
                'type': 'ellipse', 'coords': list(circle_coords), 'outline': self.active_color,
                'width': self.brush_thickness
            })
        elif self.active_tool == "fill":
            composite_img = self.create_composite()
            x, y = event.x, event.y
            fill_rgb = tuple(int(self.active_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            fill_color = fill_rgb + (255,)
            try:
                composite_img = self.apply_flood_fill(composite_img, x, y, fill_color, tolerance=10)
                self.image_data = composite_img
                self.drawing_area.delete("all")
                self.canvas_img = ImageTk.PhotoImage(composite_img.convert("RGB"))
                self.drawing_area.create_image(0, 0, anchor="nw", image=self.canvas_img)
                self.drawing_area.image = self.canvas_img
                self.draw_history = []
                messagebox.showinfo("Success", "Fill applied successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Fill failed: {e}")
        self.prev_x, self.prev_y = None, None
        self.start_x, self.start_y = None, None

    def select_color_from_circle(self, event):
        x, y = event.x, event.y
        try:
            pixel_rgb = self.color_circle_data.getpixel((x, y))
            hex_val = '#{:02x}{:02x}{:02x}'.format(*pixel_rgb)
            if hex_val != "#2a2a2a":
                self.update_color(hex_val)
                self.hex_input.delete(0, tk.END)
                self.hex_input.insert(0, hex_val)
                self.update_discord_status(f"Drawing on {self.file_title}", "Choosing Color", "logo", "Eclipse - Color Picker")
        except Exception:
            pass

    def update_color(self, color):
        self.active_color = color
        self.color_sample.configure(fg_color=self.active_color)
        if not self.is_color_panel_open:
            self.update_discord_status(f"Drawing on {self.file_title}", f"Using {self.active_tool.capitalize()}", self.active_tool, f"Eclipse - {self.active_tool.capitalize()}")

    def apply_hex(self):
        hex_val = self.hex_input.get().strip()
        if len(hex_val) == 7 and hex_val.startswith("#") and all(c in "0123456789ABCDEFabcdef" for c in hex_val[1:]):
            self.update_color(hex_val)

    def set_brush_size(self):
        size = simpledialog.askinteger("Brush Size", "Enter size (1-50):", parent=self.window, minvalue=1, maxvalue=50)
        if size is not None:
            self.brush_thickness = size
            self.brush_adjuster.set(size)
            self.update_discord_status(f"Drawing on {self.file_title}", f"Using {self.active_tool.capitalize()} (Size: {self.brush_thickness})", self.active_tool, f"Eclipse - {self.active_tool.capitalize()}")

    def adjust_brush(self, value):
        self.brush_thickness = int(value)
        self.update_discord_status(f"Drawing on {self.file_title}", f"Using {self.active_tool.capitalize()} (Size: {self.brush_thickness})", self.active_tool, f"Eclipse - {self.active_tool.capitalize()}")

    def get_canvas_info(self):
        return f"Artwork: {self.file_title}\nLocation: {self.file_location}\nLast Modified: {self.last_modified}\nSize: {self.file_size_info}"

    def update_file_info(self, file_path):
        self.active_file = file_path
        self.file_title = os.path.basename(file_path)
        self.file_location = file_path
        try:
            stats = os.stat(file_path)
            self.last_modified = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            size_bytes = stats.st_size
            self.file_size_info = f"{size_bytes / 1024:.2f} KB" if size_bytes < 1024 * 1024 else f"{size_bytes / (1024 * 1024):.2f} MB"
        except Exception:
            self.last_modified = "N/A"
            self.file_size_info = "N/A"
        self.update_discord_status(f"Drawing on {self.file_title}", f"Using {self.active_tool.capitalize()}", self.active_tool, f"Eclipse - {self.active_tool.capitalize()}")

    def new_artwork(self):
        if self.drawing_area:
            self.drawing_area.delete("all")
            self.draw_history = []
            self.canvas_img = None
            self.image_data = None
            self.active_file = None
            self.file_title = "Unnamed"
            self.file_location = "N/A"
            self.last_modified = "N/A"
            self.file_size_info = "N/A"
            self.canvas_info_label.configure(text=self.get_canvas_info())
            self.update_discord_status(f"Drawing on {self.file_title}", f"Using {self.active_tool.capitalize()}", self.active_tool, f"Eclipse - {self.active_tool.capitalize()}")

    def save_artwork(self):
        if not self.drawing_area:
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".skt", filetypes=[("Sketch files", "*.skt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.draw_history, f, indent=2)
                self.update_file_info(file_path)
                self.canvas_info_label.configure(text=self.get_canvas_info())
                messagebox.showinfo("Success", f"Saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Save failed: {e}")

    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Sketch files", "*.skt"), ("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            if not self.drawing_area:
                self.home_panel.destroy()
                self.setup_drawing_ui()
            self.drawing_area.delete("all")
            self.draw_history = []
            self.canvas_img = None
            self.image_data = None
            try:
                if file_path.endswith('.png'):
                    img = Image.open(file_path).resize((800, 600), Image.Resampling.LANCZOS)
                    self.image_data = img
                    self.canvas_img = ImageTk.PhotoImage(img)
                    self.drawing_area.create_image(0, 0, anchor="nw", image=self.canvas_img)
                    self.drawing_area.image = self.canvas_img
                else:
                    with open(file_path, 'r') as f:
                        self.draw_history = json.load(f)
                    self.redraw_canvas()
                self.update_file_info(file_path)
                self.canvas_info_label.configure(text=self.get_canvas_info())
                messagebox.showinfo("Success", f"Opened {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Open failed: {e}")

    def export_png(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            try:
                composite = self.create_composite().convert("RGB")
                composite.save(file_path, "PNG")
                self.update_file_info(file_path)
                messagebox.showinfo("Success", f"Exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")

    def create_composite(self):
        if not self.image_data:
            self.image_data = Image.new("RGBA", (800, 600), (255, 255, 255, 255))
        
        draw = ImageDraw.Draw(self.image_data)
        for action in self.draw_history:
            if action['type'] in ['line', 'brush']:
                x1, y1, x2, y2 = action['coords']
                fill_rgb = tuple(int(action['fill'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                draw.line(
                    [(x1, y1), (x2, y2)], fill=fill_rgb + (255,),
                    width=int(action['width']), joint="curve" if action.get('smooth', False) else None
                )
            elif action['type'] == 'rectangle':
                x1, y1, x2, y2 = action['coords']
                outline_rgb = tuple(int(action['outline'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                draw.rectangle(
                    [(min(x1, x2), min(y1, y2)), (max(x1, x2), max(y1, y2))],
                    outline=outline_rgb + (255,), width=int(action['width'])
                )
            elif action['type'] == 'ellipse':
                x1, y1, x2, y2 = action['coords']
                outline_rgb = tuple(int(action['outline'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                draw.ellipse(
                    [(min(x1, x2), min(y1, y2)), (max(x1, x2), max(y1, y2))],
                    outline=outline_rgb + (255,), width=int(action['width'])
                )
            elif action['type'] == 'text':
                x, y = action['coords']
                fill_rgb = tuple(int(action['fill'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                try:
                    draw.text((x, y), action['text'], fill=fill_rgb + (255,), font_size=action['font'][1])
                except TypeError:
                    draw.text((x, y), action['text'], fill=fill_rgb + (255,))
        return self.image_data

    def redraw_canvas(self):
        try:
            for action in self.draw_history:
                if not isinstance(action, dict) or 'type' not in action or 'coords' not in action:
                    continue
                if action['type'] in ['line', 'brush']:
                    self.drawing_area.create_line(
                        action['coords'], fill=action.get('fill', '#000000'), width=action.get('width', 1),
                        capstyle=action.get('capstyle', 'projecting'), smooth=action.get('smooth', False)
                    )
                elif action['type'] == 'rectangle':
                    self.drawing_area.create_rectangle(
                        action['coords'], outline=action.get('outline', '#000000'), width=action.get('width', 1)
                    )
                elif action['type'] == 'ellipse':
                    self.drawing_area.create_oval(
                        action['coords'], outline=action.get('outline', '#000000'), width=action.get('width', 1)
                    )
                elif action['type'] == 'text':
                    self.drawing_area.create_text(
                        action['coords'], text=action.get('text', ''), fill=action.get('fill', '#000000'),
                        font=action.get('font', ("Arial", 10))
                    )
        except Exception as e:
            messagebox.showerror("Error", f"Redraw failed: {e}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = EclipseApp(root)
    try:
        root.mainloop()
    finally:
        app.shutdown_discord()
