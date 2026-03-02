import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mss
import cv2
import numpy as np
import threading
import time
from PIL import Image, ImageTk
import os
import sys
import wave
import sounddevice as sd
from moviepy.editor import VideoFileClip, AudioFileClip
import ctypes
from ctypes import wintypes


APP_NAME = "XVCapture v1.0"
PROGRAMMER_NAME = "Rodolfo Hernández Baz - Pr@fEsOr X"


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

IMAGE_FILE = resource_path("1f2833.png")


class AreaSelector:
    def __init__(self, parent, monitor_geometry):
        self.parent = parent
        self.coords = None
        self.window = tk.Toplevel(parent)
        self.window.attributes('-fullscreen', True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.3)
        self.window.configure(bg="black")
        
        if monitor_geometry:
             self.window.geometry(f"{monitor_geometry['width']}x{monitor_geometry['height']}+{monitor_geometry['left']}+{monitor_geometry['top']}")

        self.canvas = tk.Canvas(self.window, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.start_x = 0
        self.start_y = 0
        self.rect = None
        
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.window.bind("<Escape>", lambda e: self.cancel())
        self.window.wait_window()

    def on_click(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline='red', width=3)

    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        end_x, end_y = event.x, event.y
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        
        width = x2 - x1
        height = y2 - y1
        
        if width > 5 and height > 5:
            self.coords = (x1, y1, width, height)
        
        self.window.destroy()

    def cancel(self):
        self.coords = None
        self.window.destroy()


class WindowSelector:
    def __init__(self, parent):
        self.parent = parent
        self.selected_rect = None
        

        self.window = tk.Toplevel(parent)
        self.window.attributes('-fullscreen', True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.1) # Muy tenue
        self.window.configure(bg="black", cursor="crosshair")
        
        self.window.bind("<Button-1>", self.on_click)
        self.window.bind("<Escape>", lambda e: self.cancel())
        
        self.window.wait_window()

    def on_click(self, event):

        self.window.withdraw()
        self.parent.update()
        

        x, y = self.parent.winfo_pointerxy()
        

        user32 = ctypes.windll.user32
        point = wintypes.POINT(x, y)
        hwnd = user32.WindowFromPoint(point)
        

        root_hwnd = user32.GetAncestor(hwnd, 2)
        
      
        user32.SetForegroundWindow(root_hwnd)
        
       
        time.sleep(0.2) 
        
    
        rect = wintypes.RECT()
        user32.GetWindowRect(root_hwnd, ctypes.byref(rect))
        
        self.selected_rect = (rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top)
        self.window.destroy()

    def cancel(self):
        self.window.destroy()

class SplashScreen:
    def __init__(self, parent, image_path):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.overrideredirect(True)
        self.window.attributes('-alpha', 0.0)
        bg_splash = "#1f2833"
        
        try:
            self.img = Image.open(image_path)
            base_width = 400
            w_percent = (base_width / float(self.img.size[0]))
            h_size = int((float(self.img.size[1]) * float(w_percent)))
            self.img = self.img.resize((base_width, h_size), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(self.img)
            
            label = tk.Label(self.window, image=self.logo, bg=bg_splash)
            label.pack()
            
            self.window.update_idletasks()
            width = self.window.winfo_width()
            height = self.window.winfo_height()
            x = (self.window.winfo_screenwidth() // 2) - (width // 2)
            y = (self.window.winfo_screenheight() // 2) - (height // 2)
            self.window.geometry(f'{width}x{height}+{x}+{y}')
        except Exception as e:
            print(f"Error cargando splash: {e}")
            self.window.destroy()
            return

        self.fade_in()

    def fade_in(self):
        alpha = self.window.attributes('-alpha')
        if alpha < 1.0:
            alpha += 0.05
            self.window.attributes('-alpha', alpha)
            self.window.after(20, self.fade_in)
        else:
            self.window.after(2000, self.fade_out)

    def fade_out(self):
        alpha = self.window.attributes('-alpha')
        if alpha > 0:
            alpha -= 0.05
            self.window.attributes('-alpha', alpha)
            self.window.after(20, self.fade_out)
        else:
            self.window.destroy()
            self.parent.deiconify()

class ScreenCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("580x680") 
        self.root.resizable(False, False)
        self.root.withdraw()

        # Variables de estado
        self.is_recording = False
        self.video_writer = None
        self.recording_thread = None
        self.audio_thread = None
        self.record_audio = False
        
    
        self.recording_start_time = 0
        self.timer_id = None
        self.frames_recorded = 0
        self.actual_fps = 0
        
        self.setup_style()
        self.create_widgets()
        SplashScreen(self.root, IMAGE_FILE)

    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        
   
        base_dark = "#1f2833"
        accent_cyan = "#66FCF1"
        accent_teal = "#45A29E"
        text_light = "#C5C6C7"
        text_white = "#FFFFFF"
        
        self.root.configure(background=base_dark)

   
        style.configure("TFrame", background=base_dark)
        style.configure("TLabel", background=base_dark, foreground=text_light, font=('Segoe UI', 10))
        style.configure("Header.TLabel", font=('Segoe UI', 16, 'bold'), foreground=accent_cyan)
        
        style.configure("TButton", background=accent_teal, foreground=text_white, font=('Segoe UI', 10, 'bold'), padding=10, borderwidth=0, focuscolor='none')
        style.map("TButton", background=[('active', accent_cyan)], foreground=[('active', base_dark)])

        style.configure("TCheckbutton", background=base_dark, foreground=text_light)
        style.map("TCheckbutton", background=[('active', base_dark)])

        style.configure("TCombobox", fieldbackground="#2d3a4a", background=accent_teal, foreground=text_white, arrowcolor=text_white)
        style.map("TCombobox", fieldbackground=[('readonly', "#2d3a4a")])

        style.configure("TLabelframe", background=base_dark)
        style.configure("TLabelframe.Label", background=base_dark, foreground=accent_cyan, font=('Segoe UI', 11, 'bold'))
        

        style.configure("Status.TLabel", background=base_dark, foreground=accent_cyan, font=('Segoe UI', 9, 'italic'))
        style.configure("Recording.TLabel", background=base_dark, foreground="red", font=('Segoe UI', 16, 'bold'))

    
        style.configure("TNotebook", background=base_dark, borderwidth=0)
        style.configure("TNotebook.Tab", background=base_dark, foreground=text_light, padding=[10, 5], font=('Segoe UI', 10, 'bold'))
        style.map("TNotebook.Tab", background=[("selected", accent_teal)], foreground=[("selected", text_white)])

    def create_widgets(self):
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

       
        tab_capture = ttk.Frame(self.notebook)
        self.notebook.add(tab_capture, text=" CAPTURA ")

        main_frame = ttk.Frame(tab_capture, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

       
        ttk.Label(main_frame, text=APP_NAME, style="Header.TLabel").pack(pady=(0, 10))

        
        mon_frame = ttk.LabelFrame(main_frame, text=" ORIGEN DE CAPTURA (VIDEO) ", padding="10")
        mon_frame.pack(fill=tk.X, pady=5)

        ttk.Label(mon_frame, text="Seleccionar Monitor:").pack(anchor=tk.W)
        self.monitors_dict = {}
        monitors_list = []
        with mss.mss() as sct:
            for i, mon in enumerate(sct.monitors[1:], start=1):
                name = f"Monitor {i} ({mon['width']}x{mon['height']})"
                self.monitors_dict[name] = i
                monitors_list.append(name)
        
        self.selected_monitor = ttk.Combobox(mon_frame, values=monitors_list, state="readonly")
        if monitors_list:
            self.selected_monitor.current(0)
        self.selected_monitor.pack(fill=tk.X, pady=5)

       
        img_frame = ttk.LabelFrame(main_frame, text=" CAPTURA DE IMAGEN ", padding="10")
        img_frame.pack(fill=tk.X, pady=5)

        
        opts_row = ttk.Frame(img_frame)
        opts_row.pack(fill=tk.X, pady=5)

        
        left_col = ttk.Frame(opts_row)
        left_col.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(left_col, text="Modo de Captura:").pack(anchor=tk.W)
        
        mode_frame = ttk.Frame(left_col)
        mode_frame.pack(fill=tk.X)
        
        self.var_fullscreen = tk.IntVar(value=1) # Nueva variable, activada por defecto
        self.var_area = tk.IntVar()
        self.var_window = tk.IntVar()
        
       
        chk_full = ttk.Checkbutton(mode_frame, text="Pantalla Completa", variable=self.var_fullscreen)
        chk_full.pack(side=tk.LEFT, padx=(0, 5))
        
        chk_area = ttk.Checkbutton(mode_frame, text="Seleccionar Área", variable=self.var_area)
        chk_area.pack(side=tk.LEFT, padx=(0, 5))
        
        chk_window = ttk.Checkbutton(mode_frame, text="Ventana Específica", variable=self.var_window)
        chk_window.pack(side=tk.LEFT)
        
       
        right_col = ttk.Frame(opts_row)
        right_col.pack(side=tk.LEFT, padx=(20, 0))
        
        ttk.Label(right_col, text="Retardo:").pack(anchor=tk.W)
        
        delay_frame = ttk.Frame(right_col)
        delay_frame.pack(fill=tk.X)
        
        self.var_d3 = tk.IntVar()
        self.var_d4 = tk.IntVar()
        self.var_d5 = tk.IntVar()
        
        ttk.Checkbutton(delay_frame, text="3 seg", variable=self.var_d3).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Checkbutton(delay_frame, text="4 seg", variable=self.var_d4).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Checkbutton(delay_frame, text="5 seg", variable=self.var_d5).pack(side=tk.LEFT)

        
        ttk.Label(img_frame, text="Calidad:").pack(anchor=tk.W, pady=(10, 0))
        self.img_quality = ttk.Combobox(img_frame, values=["Alta (Original)", "Media (80%)", "Baja (50%)"], state="readonly")
        self.img_quality.current(0)
        self.img_quality.pack(fill=tk.X, pady=5)

        btn_img = ttk.Button(img_frame, text="Capturar Imagen", command=self.initiate_image_capture)
        btn_img.pack(fill=tk.X, pady=5)

     
        vid_frame = ttk.LabelFrame(main_frame, text=" CAPTURA DE VIDEO ", padding="10")
        vid_frame.pack(fill=tk.X, pady=5)

        ttk.Label(vid_frame, text="Calidad:").pack(anchor=tk.W)
        self.vid_quality = ttk.Combobox(vid_frame, values=["Alta (30 FPS)", "Media (20 FPS)", "Baja (10 FPS)"], state="readonly")
        self.vid_quality.current(0)
        self.vid_quality.pack(fill=tk.X, pady=5)

        self.audio_var = tk.IntVar()
        chk_audio = ttk.Checkbutton(vid_frame, text="Grabar Audio del Micrófono", variable=self.audio_var)
        chk_audio.pack(anchor=tk.W, pady=5)

        btns_vid_frame = ttk.Frame(vid_frame)
        btns_vid_frame.pack(fill=tk.X, pady=5)

        self.btn_start = ttk.Button(btns_vid_frame, text="Iniciar Grabación", command=self.start_recording)
        self.btn_start.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,5))

        self.btn_stop = ttk.Button(btns_vid_frame, text="Detener", command=self.stop_recording, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5,0))

       
        self.status_label = ttk.Label(main_frame, text="Estado: Listo", style="Status.TLabel")
        self.status_label.pack(side=tk.BOTTOM, pady=(10, 0))

        
        tab_about = ttk.Frame(self.notebook)
        self.notebook.add(tab_about, text=" Acerca de ")

        about_container = ttk.Frame(tab_about, padding="20")
        about_container.pack(fill=tk.BOTH, expand=True)

        
        try:
            img = Image.open(IMAGE_FILE)
            img = img.resize((120, 120), Image.Resampling.LANCZOS)
            self.logo_about = ImageTk.PhotoImage(img)
            lbl_logo = tk.Label(about_container, image=self.logo_about, bg="#1f2833")
            lbl_logo.pack(pady=15)
        except: pass

        ttk.Label(about_container, text=APP_NAME, font=('Segoe UI', 18, 'bold')).pack()
        ttk.Label(about_container, text=f"Desarrollado por: {PROGRAMMER_NAME}", font=('Segoe UI', 10, 'italic')).pack(pady=(0, 15))
        
        features_text = """
        INFORMACIÓN TÉCNICA
        
        Motor de Captura: MSS (High Performance)
        Motor de Audio: SoundDevice
        Interfaz: Tkinter (Dark Theme)
        
        CARACTERÍSTICAS PRINCIPALES
        
        • Multi-Monitor: Selección de pantalla.
        • Audio: Grabación de micrófono.
        • Optimización: Hilos separados.
        • Formato Salida: MP4 (H.264) + AAC.
        
        CAPTURA DE IMAGEN
        
        • Modos: Pantalla completa, selección de
          área manual y ventana específica.
        • Retardo: Temporizador de 3, 4 y 5
          segundos para captura retardada.
        
        VIDEO
        
        • Contador de tiempo en tiempo real.
        • Sincronización automática de Audio/Video.
        * 2026
        """
        
        txt = tk.Text(about_container, height=20, width=50, bg="#2d3a4a", fg="#C5C6C7", font=('Consolas', 9), relief=tk.FLAT, padx=10, pady=10, insertbackground="white")
        txt.insert(tk.END, features_text)
        txt.config(state=tk.DISABLED)
        txt.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

   
    def get_monitor_index(self):
        selection = self.selected_monitor.get()
        idx = self.monitors_dict.get(selection, 1)
        return idx

    def initiate_image_capture(self):
        seconds = 0
        if self.var_d5.get() == 1: seconds = 5
        elif self.var_d4.get() == 1: seconds = 4
        elif self.var_d3.get() == 1: seconds = 3
        
        if seconds > 0:
            self._run_countdown(seconds)
        else:
            self.capture_image()

    def _run_countdown(self, seconds):
        if seconds > 0:
            self.status_label.config(text=f"Capturando en {seconds}...", style="Status.TLabel")
            self.root.update()
            time.sleep(1)
            self._run_countdown(seconds - 1)
        else:
            self.status_label.config(text="¡Capturando!", style="Status.TLabel")
            self.root.update()
            self.capture_image()

    def capture_image(self):
        try:
            monitor_idx = self.get_monitor_index()
            quality_sel = self.img_quality.get()
            
            
            is_window_mode = self.var_window.get() == 1
            is_area_mode = self.var_area.get() == 1
            
            if "Alta" in quality_sel: scale, quality_val = 1.0, 95
            elif "Media" in quality_sel: scale, quality_val = 0.8, 85
            else: scale, quality_val = 0.5, 60

            with mss.mss() as sct:
                base_monitor = sct.monitors[monitor_idx]
                
                if is_window_mode:
                   
                    self.status_label.config(text="Haz clic en la ventana a capturar...", style="Status.TLabel")
                    self.root.update()
                    
                    selector = WindowSelector(self.root)
                    
                    if selector.selected_rect:
                        x, y, w, h = selector.selected_rect
                        monitor = {
                            "left": x, "top": y,
                            "width": w, "height": h,
                        }
                        screenshot = sct.grab(monitor)
                    else:
                        self.status_label.config(text="Estado: Cancelado", style="Status.TLabel")
                        return

                elif is_area_mode:
                    selector = AreaSelector(self.root, base_monitor)
                    if selector.coords:
                        x, y, w, h = selector.coords
                        monitor = {
                            "left": base_monitor["left"] + x, "top": base_monitor["top"] + y,
                            "width": w, "height": h,
                        }
                        screenshot = sct.grab(monitor)
                    else:
                        self.status_label.config(text="Estado: Listo", style="Status.TLabel")
                        return 
                else:
                    
                    screenshot = sct.grab(base_monitor)
            
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
            if scale < 1.0:
                img = img.resize((int(screenshot.width * scale), int(screenshot.height * scale)), Image.Resampling.LANCZOS)

            filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if filename:
                img.save(filename, quality=quality_val, optimize=True)
                self.status_label.config(text=f"Imagen guardada.", style="Status.TLabel")
                messagebox.showinfo("Éxito", "Captura realizada.")
            else:
                self.status_label.config(text="Estado: Listo", style="Status.TLabel")

        except Exception as e:
            messagebox.showerror("Error", f"Error al capturar: {e}")
            self.status_label.config(text="Estado: Error", style="Status.TLabel")

    def start_recording(self):
        self.is_recording = True
        self.record_audio = self.audio_var.get() == 1
        
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        
        q_sel = self.vid_quality.get()
        if "Alta" in q_sel: self.fps, self.scale_factor = 30, 1.0
        elif "Media" in q_sel: self.fps, self.scale_factor = 20, 0.75
        else: self.fps, self.scale_factor = 10, 0.5
        
        self.current_monitor_idx = self.get_monitor_index()

        base_filename = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
        if not base_filename:
            self.stop_recording() 
            return
        
        self.recording_start_time = time.time()
        self.frames_recorded = 0 
        self.update_timer()

        self.final_filename = base_filename
        self.temp_video_filename = base_filename.replace(".mp4", "_temp_video.mp4")
        self.temp_audio_filename = base_filename.replace(".mp4", "_temp_audio.wav")

        self.video_thread = threading.Thread(target=self.record_video_loop)
        self.video_thread.start()
        
        if self.record_audio:
            self.audio_thread = threading.Thread(target=self.record_audio_loop)
            self.audio_thread.start()

    def update_timer(self):
        if self.is_recording:
            elapsed = int(time.time() - self.recording_start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            time_str = f"Grabando: {minutes:02d}:{seconds:02d}"
            self.status_label.config(text=time_str, style="Recording.TLabel")
            self.timer_id = self.root.after(1000, self.update_timer)

    def record_video_loop(self):
        start_time = time.time()
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[self.current_monitor_idx]
                width, height = monitor['width'], monitor['height']
                out_width = int(width * self.scale_factor)
                out_height = int(height * self.scale_factor)

                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                self.video_writer = cv2.VideoWriter(self.temp_video_filename, fourcc, self.fps, (out_width, out_height))

                next_frame_time = time.time()

                while self.is_recording:
                    img = np.array(sct.grab(monitor))
                    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    
                    if self.scale_factor < 1.0:
                        frame = cv2.resize(frame, (out_width, out_height), interpolation=cv2.INTER_AREA)
                    
                    self.video_writer.write(frame)
                    self.frames_recorded += 1

                    next_frame_time += 1.0 / self.fps
                    current_time = time.time()
                    
                    if next_frame_time > current_time:
                        time.sleep(next_frame_time - current_time)
        
        except Exception as e:
            print(f"Error video thread: {e}")
        finally:
            if self.video_writer:
                self.video_writer.release()
            
            end_time = time.time()
            duration = end_time - start_time
            if duration > 0 and self.frames_recorded > 0:
                self.actual_fps = self.frames_recorded / duration
            else:
                self.actual_fps = self.fps 

    def record_audio_loop(self):
        fs = 44100
        channels = 1
        try:
            with sd.InputStream(samplerate=fs, channels=channels, dtype='int16') as stream:
                frames = []
                while self.is_recording:
                    data, overflowed = stream.read(1024)
                    if overflowed: print("Advertencia: Audio buffer overflow")
                    frames.append(data)
                
                wf = wave.open(self.temp_audio_filename, 'wb')
                wf.setnchannels(channels)
                wf.setsampwidth(2)
                wf.setframerate(fs)
                audio_data = b''.join([t.tobytes() for t in frames])
                wf.writeframes(audio_data)
                wf.close()
        except Exception as e:
            print(f"Error audio thread: {e}")

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None

            if self.video_thread: self.video_thread.join()
            if self.audio_thread: self.audio_thread.join()
            
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
            
            self.status_label.config(text="Estado: Procesando...", style="Status.TLabel")
            
            if self.record_audio and os.path.exists(self.temp_audio_filename):
                self.merge_audio_video()
            else:
                if os.path.exists(self.temp_video_filename):
                    os.rename(self.temp_video_filename, self.final_filename)
                self.status_label.config(text="Estado: Grabación finalizada")
                messagebox.showinfo("Info", f"Video guardado en:\n{self.final_filename}")

    def merge_audio_video(self):
        try:
            videoclip = VideoFileClip(self.temp_video_filename)
            audioclip = AudioFileClip(self.temp_audio_filename)
            
            # Corrección de sincronización
            print(f"FPS Objetivo: {self.fps} | FPS Reales: {self.actual_fps:.2f}")
            videoclip = videoclip.set_fps(self.actual_fps)
            
            final_clip = videoclip.set_audio(audioclip)
            
            final_clip.write_videofile(
                self.final_filename,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                threads=4,
                preset='ultrafast'
            )
            
            videoclip.close()
            audioclip.close()
            final_clip.close()
            
            if os.path.exists(self.temp_video_filename): os.remove(self.temp_video_filename)
            if os.path.exists(self.temp_audio_filename): os.remove(self.temp_audio_filename)
            
            self.status_label.config(text="Estado: Video con audio guardado")
            messagebox.showinfo("Éxito", f"Video guardado en:\n{self.final_filename}")
            
        except Exception as e:
            messagebox.showerror("Error de Fusión", f"No se pudo unir audio y video: {e}")
            if os.path.exists(self.temp_video_filename):
                os.rename(self.temp_video_filename, self.final_filename.replace(".mp4", "_NO_AUDIO.mp4"))

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenCaptureApp(root)
    root.mainloop()