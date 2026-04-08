from PIL import Image
import configparser
import customtkinter
import tkinter as tk
import pystray
import keyboard
import os
import threading
import subprocess
import webbrowser
import time
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores its path in sys._MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MessageWindow(customtkinter.CTkToplevel):
    def __init__(self, master, title, message, wtype):
        super().__init__(master)
        self.grab_set()
        self.title(title)

        screenwidth = int(self.winfo_screenwidth())
        screenheight = int(self.winfo_screenheight())
        xpos = (screenwidth - 300) // 2
        ypos = (screenheight - 125) // 2
        self.geometry(f"300x125+{xpos}+{ypos}")

        self.message = message
        self.message_label = customtkinter.CTkLabel(master=self, text=message)
        
        self.button_frame = customtkinter.CTkFrame(master=self)
        
        self.type = wtype 
        if wtype == 1:
            self.button_frame.grid_columnconfigure((0), weight=1)
            self.okay_btn = customtkinter.CTkButton(master=self.button_frame, text="Okay", command=self.destroy)
            
            self.button_frame.pack(side="bottom", fill="x", padx=10, pady=10)
            self.okay_btn.grid(sticky="ew", row=0, column=0, padx=5)
            self.message_label.pack(pady=2)

        elif wtype == 2:
            self.button_frame.grid_columnconfigure((0, 1), weight=1)

            self.confirm_btn = customtkinter.CTkButton(master=self.button_frame, text="Confirm", command=self.confirm_removal)
            self.cancel_btn = customtkinter.CTkButton(master=self.button_frame, text="Cancel", command=self.destroy)

            self.button_frame.pack(side="bottom", fill="x", padx=10, pady=10)
            self.confirm_btn.grid(sticky="ew", row=0, column=0, padx=5)
            self.cancel_btn.grid(sticky="ew", row=0, column=1, padx=5)
            self.removal_label.pack(pady=20)


        

class RemoveModalWindow(customtkinter.CTkToplevel):
    def __init__(self, master, hotkey_name):
        super().__init__(master)
        self.grab_set()
        self.hotkey_name = hotkey_name

        self.title("Confirm Removal")
        self.after(200, lambda: self.iconbitmap(resource_path('hkman.ico')))
        
        screenwidth = int(self.winfo_screenwidth())
        screenheight = int(self.winfo_screenheight())
        xpos = (screenwidth - 300) // 2
        ypos = (screenheight - 125) // 2
        self.geometry(f"300x125+{xpos}+{ypos}")
      

        removal_string = f"Are you sure you want to remove\n'{hotkey_name}'?"
        self.removal_label = customtkinter.CTkLabel(master=self, text=removal_string)

        self.button_frame = customtkinter.CTkFrame(master=self)
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        self.confirm_btn = customtkinter.CTkButton(master=self.button_frame, text="Confirm", command=self.confirm_removal)
        self.cancel_btn = customtkinter.CTkButton(master=self.button_frame, text="Cancel", command=self.destroy)

        self.button_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        self.confirm_btn.grid(sticky="ew", row=0, column=0, padx=5)
        self.cancel_btn.grid(sticky="ew", row=0, column=1, padx=5)
        self.removal_label.pack(pady=20)

    def confirm_removal(self):
        self.master.delete_hotkey(self.hotkey_name)
        self.destroy()







class ConfigModalWindow(customtkinter.CTkToplevel):
    def __init__(self, master, name=None, keybind=None, path=None, item_type=None):
        super().__init__(master)
        self.grab_set()
        self.is_recording = False
        self.is_destroyed = False
        
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self.title("Hotkey Editor")
        self.after(200, lambda: self.iconbitmap(resource_path('hkman.ico')))
        


        screenwidth = int(self.winfo_screenwidth())
        screenheight = int(self.winfo_screenheight())
        xpos = (screenwidth - 300) // 2
        ypos = (screenheight - 300) // 2
        self.geometry(f"300x300+{xpos}+{ypos}")
        
        
        self.form_frame = customtkinter.CTkFrame(self)
        self.form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.form_frame.grid_columnconfigure((0), weight=0)
        self.form_frame.grid_columnconfigure((1), weight=1)
        

        self.name_label = customtkinter.CTkLabel(self.form_frame, text="Name:")
        self.keybind_label = customtkinter.CTkLabel(self.form_frame, text="Keybind:")
        self.path_label = customtkinter.CTkLabel(self.form_frame, text="Path:")

       
        self.name_entry = customtkinter.CTkEntry(self.form_frame)
        self.keybind_entry = customtkinter.CTkEntry(self.form_frame)
        self.path_entry = customtkinter.CTkEntry(self.form_frame)
        
        self.name_label.grid(sticky="ew", row=0, column=0, padx=10, pady=10)
        self.keybind_label.grid(sticky="ew", row=1, column=0, padx=10, pady=10)
        self.path_label.grid(sticky="ew", row=2, column=0, padx=10, pady=10)

        self.name_entry.grid(sticky="ew", row=0, column=1, padx=10, pady=10)
        self.keybind_entry.grid(sticky="ew", row=1, column=1, padx=10, pady=10)
        self.path_entry.grid(sticky="ew", row=2, column=1, padx=10, pady=10)
    
        self.keybind_entry.bind("<FocusIn>", self.start_keybind_recording)

        if item_type is not None:
            self.type_label = customtkinter.CTkLabel(self.form_frame, text="Type")
            self.type_label.grid(sticky="ew", row=3, column=0, padx=10, pady=10)

            self.type_entry = customtkinter.CTkEntry(self.form_frame)
            self.type_entry.grid(sticky="ew", row=3, column=1, padx=10, pady=10)

        self.button_frame = customtkinter.CTkFrame(self)
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        self.confirm_btn = customtkinter.CTkButton(master=self.button_frame, text="Confirm", command=self.submit_data)
        self.cancel_btn = customtkinter.CTkButton(master=self.button_frame, text="Cancel", command=self.destroy)

        self.button_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        self.confirm_btn.grid(sticky="ew", row=0, column=0, padx=5)
        self.cancel_btn.grid(sticky="ew", row=0, column=1, padx=5)

        if name is not None:
            self.name_entry.insert(0, name)
            self.name_entry.configure(state="readonly")
        if keybind is not None:
            self.keybind_entry.insert(0, keybind)
        if path is not None:
            self.path_entry.insert(0, path)
        if item_type is not None:
            self.type_entry.insert(0, item_type)
            self.type_entry.configure(state="readonly")

    def start_keybind_recording(self, event):
        if not self.is_recording:
            threading.Thread(target=self.record_keybind, daemon=True).start()

    def record_keybind(self):
        self.after(0, self.focus_set)
        self.is_recording = True
        


        self.after(0, lambda: self.name_entry.configure(state="readonly"))
        self.after(0, lambda: self.path_entry.configure(state="readonly"))
        self.after(0, lambda: self.confirm_btn.configure(state="disabled"))
        self.after(0, lambda: self.cancel_btn.configure(state="disabled"))

        self.after(0, lambda: self.keybind_entry.delete(0, "end"))
        self.after(0, lambda: self.keybind_entry.insert(0, 'Listening...'))
        keyboard._pressed_events.clear()

        time.sleep(0.1)
        recorded_keybind = keyboard.read_hotkey(suppress=True)
        time.sleep(0.5)

        if getattr(self, 'is_destroyed', False):
            print("Thread successfully ended.")
            return 
            
        
        if recorded_keybind == 'esc':
            self.after(0, lambda: self.keybind_entry.delete(0, "end"))
            self.is_recording = False
            print("Thread successfully ended.")
            self.after(0, self.focus_set)
            return

           

        self.after(0, lambda: self.keybind_entry.delete(0, "end"))
        self.after(0, lambda: self.keybind_entry.insert(0, recorded_keybind))

        self.after(0, lambda: self.name_entry.configure(state="normal"))
        self.after(0, lambda: self.path_entry.configure(state="normal"))
        self.after(0, lambda: self.confirm_btn.configure(state="normal"))
        self.after(0, lambda: self.cancel_btn.configure(state="normal"))
        
        self.is_recording = False
        self.after(0, self.focus_set)

        
    def open_blank_field_warning(self):
        msg_window = MessageWindow(self, "Warning: Empty Input", "Error: All fields must be filled out! Please enter a value into each field and try again.", 1)

    def submit_data(self):
           
        self.name = self.name_entry.get().strip()
        self.keybind = self.keybind_entry.get().strip()
        self.path = self.path_entry.get().strip()

        if self.name == "" or self.keybind == "" or self.path == "":
            self.open_blank_field_warning()
            print("Error: All fields must be filled out!")
            return 

        

        
        # Safely check if the type_entry was created during __init__ (Edit Mode)
        if hasattr(self, 'type_entry'):
           self.item_type = self.type_entry.get()
        else:
            path_lower = self.path.lower()
            if path_lower.startswith("http://") or path_lower.startswith("https://"):
                self.item_type = "Website"
            elif path_lower.endswith(".exe"):
                self.item_type = "Application"
            elif path_lower.endswith((".py", ".bat", ".ahk", ".ps1")):
                self.item_type = "Script"
            elif "." in path_lower.replace("\\", "/").split("/")[-1]:
                # If there is a dot in the final part of the path, it's a file
                self.item_type = "File"
            else:
                # If there's no dot, we assume it's a folder/directory
                self.item_type = "Folder"

                if self.path.lower().startswith("http://") or self.path.lower().startswith("https://") == False :
                    if os.path.exists(os.path.expandvars(self.path)) == False:
                        MessageWindow(self, "Warning: Invalid Path", "Error: The entered path does not exist.", 1)
                        return

        self.master.save_hotkey(self.name, self.keybind, self.path, self.item_type)
        self.destroy()

    def on_window_close(self):
        self.is_destroyed = True
        if getattr(self, 'is_recording', False):
            keyboard.send('esc')
            print("Thread successfully ended.")
        
        self.destroy()
        



class ConfigWindow(customtkinter.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self.grab_set()
        self.selected_item = customtkinter.StringVar(value="")
        self.radio_buttons = {}
        self.hotkey_data = {}

        self.title("Keyboard Configuration")
        self.after(200, lambda: self.iconbitmap(resource_path('hkman.ico')))
        
        screenwidth = int(self.winfo_screenwidth())
        screenheight = int(self.winfo_screenheight())
        xpos = (screenwidth - 1200) // 2
        ypos = (screenheight - 400) // 2
        self.geometry(f"1200x400+{xpos}+{ypos}")

        self.scrollable_list = customtkinter.CTkScrollableFrame(master=self)

        self.button_frame = customtkinter.CTkFrame(master=self)
        self.button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.create_btn = customtkinter.CTkButton(master=self.button_frame, text="Create", command=self.open_config_modal)
        self.remove_btn = customtkinter.CTkButton(master=self.button_frame, text="Remove", state="disabled", command=self.open_remove_modal)
        self.edit_btn = customtkinter.CTkButton(master=self.button_frame, text="Edit", state="disabled", command=self.open_edit_modal)

        self.button_frame.pack(side="bottom", fill="x", padx=10, pady=10)
       
        self.create_btn.grid(sticky="ew", row=0, column=0, padx=5)
        self.remove_btn.grid(sticky="ew", row=0, column=1, padx=5)
        self.edit_btn.grid(sticky="ew", row=0, column=2, padx=5)

        self.scrollable_list = customtkinter.CTkScrollableFrame(master=self)
        self.scrollable_list.pack(fill="both", expand=True, padx=10, pady=10)

        self.header_frame = customtkinter.CTkFrame(master=self.scrollable_list, fg_color="transparent")
        self.header_frame.grid_columnconfigure(0, weight=0, minsize=40) 
        self.header_frame.grid_columnconfigure((1, 2, 4), weight=1, uniform="col")
        self.header_frame.grid_columnconfigure(3, weight=2, uniform="col")
        
        self.header_frame.pack(fill="x", pady=(0, 5))

        customtkinter.CTkLabel(master=self.header_frame, text="Name", anchor="center", font=("Arial", 14, "bold")).grid(row=0, column=1, sticky="ew", padx=5)
        customtkinter.CTkLabel(master=self.header_frame, text="Keybind", anchor="center", font=("Arial", 14, "bold")).grid(row=0, column=2, sticky="ew", padx=5)
        customtkinter.CTkLabel(master=self.header_frame, text="Path", anchor="center", font=("Arial", 14, "bold")).grid(row=0, column=3, sticky="ew", padx=5)
        customtkinter.CTkLabel(master=self.header_frame, text="Type", anchor="center", font=("Arial", 14, "bold")).grid(row=0, column=4, sticky="ew", padx=5)

        self.scrollable_list.pack(fill="both", expand=True)

        self.load_saved_hotkeys()

    def on_window_close(self):
        self.master.state_btn.configure(state="normal")
        self.destroy()

    def load_saved_hotkeys(self):
        for section_name in self.master.config.sections():  # Loops through every section header (like [MyFolder]) found in the config file
            section_data = self.master.config[section_name]  # Grabs the dictionary of settings under that specific section
            
            skeybind = section_data.get('keybind')
            spath = section_data.get('path')
            stype = section_data.get('type')

            print(f"{section_name}\n{skeybind}\n{spath}\n{stype}\n")
            self.add_list_item(section_name, skeybind, spath, stype)
            


    def open_config_modal(self):
        self.config_modal_window = ConfigModalWindow(self)
        

    def add_list_item(self, name, keybind, path, item_type):
        row_frame = customtkinter.CTkFrame(master=self.scrollable_list, fg_color="transparent")
        row_frame.grid_columnconfigure(0, weight=0, minsize=40)
        row_frame.grid_columnconfigure((1, 2, 4), weight=1, uniform="col")
        row_frame.grid_columnconfigure(3, weight=2, uniform="col")
        row_frame.pack(fill="x", pady=2)

        name_label = customtkinter.CTkLabel(master=row_frame, text=name, anchor="center")
        name_label.grid(row=0, column=1, sticky="ew", padx=5)
        
        keybind_label = customtkinter.CTkLabel(master=row_frame, text=keybind, anchor="center")
        keybind_label.grid(row=0, column=2, sticky="ew", padx=5)

        path_label = customtkinter.CTkLabel(
            master=row_frame, 
            text=path, 
            anchor="center", 
            justify="center", 
            wraplength=400
        )
        path_label.grid(row=0, column=3, sticky="ew", padx=5)

        type_label = customtkinter.CTkLabel(master=row_frame, text=item_type, anchor="center")
        type_label.grid(row=0, column=4, sticky="ew", padx=5)
       
        radio_btn = customtkinter.CTkRadioButton(master=row_frame, text="", width=30, variable=self.selected_item, value=name, command=self.enable_btn)
        radio_btn.grid(row=0, column=0, sticky="w")
        
        divider = tk.Frame(master=row_frame, height=1, bg="#333333")
        divider.grid(row=1, column=0, columnspan=5, sticky="ew", pady=(5, 0))

        self.radio_buttons[name] = row_frame
        self.hotkey_data[name] = (keybind, path, item_type)



    def save_hotkey(self, name, keybind, path, item_type):
        if name == "":
            print("Error, a valid name but be entered to save a hotkey!")
            return

        if name in self.radio_buttons:
            self.delete_hotkey(name)

        self.master.config[name] = {
        'keybind': keybind,       
        'path': path,      
        'type': item_type         
        }

        self.master.save_config()
        self.add_list_item(name, keybind, path, item_type)

        if self.master.is_enabled:
            keyboard.unhook_all()
            self.master.register_keybinds()

    def delete_hotkey(self, name):
        self.radio_buttons[name].destroy()
        del self.radio_buttons[name]
        del self.hotkey_data[name]
        self.selected_item.set("")
        self.remove_btn.configure(state="disabled")
        self.edit_btn.configure(state="disabled")

        self.master.config.remove_section(name)
        self.master.save_config()

        if self.master.is_enabled:
            keyboard.unhook_all()
            self.master.register_keybinds()

    def enable_btn(self):
        self.remove_btn.configure(state="normal")
        self.edit_btn.configure(state="normal")

    def open_remove_modal(self):
        selected_item =  self.selected_item.get()
        self.remove_modal_window = RemoveModalWindow(self, selected_item)



    def open_edit_modal(self):
        name = self.selected_item.get()
        keybind, path, item_type = self.hotkey_data[name]
        self.edit_modal_window = ConfigModalWindow(self, name, keybind, path, item_type)

        

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.create_config()
        self.config = self.get_editable_config()
        self.is_enabled = False

        self.title("Keyboard Manager")
        self.geometry("285x50+0+0")
        self.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.iconbitmap(resource_path('hkman.ico'))

        self.button_frame = customtkinter.CTkFrame(master=self)
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        self.state_btn = customtkinter.CTkButton(master=self.button_frame, text="Click to Enable", command=self.toggle_state)
        self.config_btn = customtkinter.CTkButton(master=self.button_frame, text="Configure Hotkeys", command=self.open_config_window)
        
        self.button_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        self.state_btn.grid(sticky="ew", row=0, column=0, padx=5)
        self.config_btn.grid(sticky="ew", row=0, column=1, padx=5)

        self.tray_img = Image.open(resource_path("hkman.ico"))

        self.tray_menu = pystray.Menu(
            pystray.MenuItem('Show', self.show_window, default = True),
            pystray.MenuItem('Exit', self.quit_app)
        )

        self.tray_icon = pystray.Icon("Icon", self.tray_img, "Keyboard Manager", self.tray_menu)
        self.tray_icon.run_detached()

    

    def quit_app(self, icon, item):
        icon.stop() # Safely stop the system tray icon
        keyboard.unhook_all() # Safely release the keyboard
        self.after(0, self.destroy) # Safely tell Tkinter to close

    def hide_window(self):
        self.withdraw()
    
    def show_window(self, icon, item):
        self.after(0, self.deiconify)

    def toggle_state(self):
        if self.is_enabled == True:
            keyboard.unhook_all()
            self.state_btn.configure(text="Click to Enable")
            print("Keybinds Disabled")
            self.is_enabled = False
        elif self.is_enabled == False:
            self.register_keybinds()
            self.state_btn.configure(text="Click to Disable")
            print("Keybinds Enabled")
            self.is_enabled = True

    def open_config_window(self):
        if not hasattr(self, 'config_window') or not self.config_window.winfo_exists():
            self.config_window = ConfigWindow(self)
        else:
            self.config_window.focus() 

    def register_keybinds(self):
        for section_name in self.config.sections():
            section_data = self.config[section_name]

            skeybind = section_data.get('keybind')
            spath = section_data.get('path')

            if skeybind != "" and spath != "":
                keyboard.add_hotkey(skeybind, lambda target_path=spath: self.open_path(target_path))


    def format_config(self, config):
        for entry in config:
            config[entry] = os.path.expandvars(config[entry])
        return config  


    def save_config(self):
        """
        Persists modified ConfigParser object back to config.ini.
        Overwrites entire file.
        """
        with open('./config.ini', 'w') as configfile:
            self.config.write(configfile) 
        print(f"Updated keybinds successfully!")  

    def get_editable_config(self):
        """
        Loads config.ini without interpolation for direct editing.
        Disables default ${var} expansion to avoid conflicts.
        """

        config = configparser.ConfigParser(interpolation=None)
        config.read('./config.ini')  
        return config  

    def create_config(self):
        config_path = './config.ini'
        if not os.path.exists(config_path):
            config = configparser.ConfigParser(interpolation=None)
            with open(config_path, 'w') as configfile:
                config.write(configfile)  
            print("Created a new config.ini file.")

def open_path(self, path):
        # On Linux/Mac, expandvars uses $VAR instead of %VAR%
        full_path = os.path.expandvars(path)
        
        if full_path.startswith("https://") or full_path.startswith("http://"):
            webbrowser.open(full_path)
            return
        else:
            if not os.path.exists(full_path):
                print(f"Error: Path does not exist: {full_path}")
                return
            
       
        if sys.platform == "win32":
            # --- WINDOWS LOGIC ---
            if os.path.isdir(full_path):
                # 0x00000008 is the Windows flag for DETACHED_PROCESS
                subprocess.Popen(['explorer', full_path], creationflags=0x00000008)
            else:
                os.startfile(full_path) 
                
        elif sys.platform == "darwin":
            # --- MACOS LOGIC ---
            # start_new_session=True safely detaches the child process on Apple
            subprocess.Popen(['open', full_path], start_new_session=True)
            
        else:
            # --- LINUX LOGIC ---
            # start_new_session=True safely detaches the child process on Linux
            subprocess.Popen(['xdg-open', full_path], start_new_session=True)
     







def main():
  app = App()
  app.mainloop()


if __name__ == "__main__":
    main()
