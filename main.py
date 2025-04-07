import os
import tkinter as tk
from tkinter import filedialog,ttk, messagebox, simpledialog
import ctypes
import sys
import subprocess
import threading

# Check if script is running as Admin
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# If not running as admin, restart with admin rights
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()


# Function to list files in a directory
def list_files():
    try:
        directory = "D:\\CODE\\OS_project"  # Consider making this configurable
        if not os.path.exists(directory):
            messagebox.showerror("Error", f"Directory not found: {directory}")
            return
            
        files = "\n".join(os.listdir(directory))
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, f"Files in {directory}:\n{files}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not list files: {str(e)}")

# Function to list deleted files using PowerShell
def list_deleted_files():
    drive = simpledialog.askstring("Input", "Enter Drive Letter (e.g., C):")
    if not drive:
        return

    try:
        # Corrected PowerShell command to list deleted files
        cmd = (
            f'powershell -Command "Get-ChildItem -Path \'{drive}:\\$Recycle.Bin\' -Recurse -Force '
            '| Where-Object { !$_.PSIsContainer } '
            '| Select-Object FullName | Format-List"'
        )

        output = os.popen(cmd).read().strip()

        if not output:
            messagebox.showinfo("Info", "🗑️ No deleted files found.")
            return

        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, output)

    except Exception as e:
        messagebox.showerror("Error", f"⚠️ Error: {str(e)}")


# Function to restore files using Shadow Copies
def recover_files():
    drive = simpledialog.askstring("Input", "Enter Drive Letter (e.g., C):")
    if not drive:
        return

    try:
        file_name = simpledialog.askstring("Input", "Enter the full path of the deleted file (e.g., \\Users\\Name\\file.txt):")
        if not file_name:
            return

        # Get the most recent shadow copy
        cmd = (
            'powershell -Command "(Get-WmiObject -Class Win32_ShadowCopy | '
            'Sort-Object -Property InstallDate -Descending | '
            'Select-Object -First 1).DeviceObject"'
        )
        shadow_copy_path = os.popen(cmd).read().strip()
        
        if not shadow_copy_path:
            messagebox.showerror("Error", "No Shadow Copies found.")
            return

        # Clean up the shadow copy path and prepare paths
        shadow_copy_path = shadow_copy_path.replace("\\??\\", "")
        source_path = f"{shadow_copy_path}{file_name}"
        
        # Create a recovery directory if it doesn't exist
        recovery_dir = os.path.join(f"{drive}:\\", "Recovered_Files")
        os.makedirs(recovery_dir, exist_ok=True)
        
        # Prepare destination path
        base_name = os.path.basename(file_name)
        recovered_path = os.path.join(recovery_dir, base_name)
        
        # Add timestamp to avoid overwrites
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        recovered_path = os.path.join(recovery_dir, f"recovered_{timestamp}_{base_name}")

        # Execute the copy command
        copy_cmd = f'powershell -Command "Copy-Item -Path \'{source_path}\' -Destination \'{recovered_path}\'"'
        result = os.system(copy_cmd)

        if result == 0:
            # Make the file visible (remove hidden/system attributes if any)
            os.system(f'attrib -h -s "{recovered_path}"')
            messagebox.showinfo("Success", f"File recovered to:\n{recovered_path}\n\nPlease check the 'Recovered_Files' folder on {drive}: drive.")
            
            # Open the recovery directory in File Explorer
            os.system(f'explorer "{recovery_dir}"')
        else:
            messagebox.showerror("Error", "File recovery failed. The file might not exist in shadow copies.")

    except Exception as e:
        messagebox.showerror("Error", f"Recovery failed: {str(e)}")

# Function to check disk (Windows equivalent of fsck)
def check_disk():
    drive = simpledialog.askstring("Input", "Enter Drive Letter (e.g., C):")
    if drive:
        def run_chkdsk():
            try:
                process = subprocess.Popen(
                    ["chkdsk", f"{drive}:"],  # Removed /F to prevent blocking
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                output, error = process.communicate()

                output_text.delete("1.0", tk.END)
                output_text.insert(tk.END, output if output else error)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to check disk:\n{e}")

        # Run chkdsk in a separate thread to prevent freezing the GUI
        threading.Thread(target=run_chkdsk, daemon=True).start()

# Function to optimize disk (Windows defrag)
def optimize_disk():
    drive = simpledialog.askstring("Input", "Enter Drive Letter (e.g., C):")
    if drive:
        os.system(f"defrag {drive}: /U /V")
        messagebox.showinfo("Success", "Disk Optimized Successfully!")

# Function to delete a file
def delete_file():
    file_path = filedialog.askopenfilename(title="Select File to Delete")
    if file_path:
        try:
            os.remove(file_path)
            messagebox.showinfo("Success", f"Deleted: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete file:\n{e}")


# GUI Setup
# ---------------- GUI SETUP ----------------

root = tk.Tk()
root.title("🖥️ File System Recovery & Optimization")
root.geometry("750x500")
root.resizable(False, False)
root.configure(bg="#2C2F33")  # Dark Background

# --- Custom Styling ---
style = ttk.Style()
style.configure("TButton", font=("Arial", 11, "bold"), padding=8, background="#7289DA", foreground="white")
style.configure("TLabel", background="#2C2F33", foreground="white", font=("Arial", 14, "bold"))
style.configure("TFrame", background="#2C2F33")
style.configure("TText", font=("Arial", 11), background="#23272A", foreground="white")

# --- Gradient Header ---
header = tk.Canvas(root, width=750, height=80, bg="#7289DA", highlightthickness=0)
header.create_rectangle(0, 0, 750, 80, fill="#7289DA")
header.create_text(375, 40, text="💾 File System Recovery & Optimization", fill="white", font=("Arial", 16, "bold"))
header.pack()

# --- Buttons Frame ---
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

# --- Button Styles ---
def on_enter(e):
    e.widget["background"] = "#99AAB5"

def on_leave(e):
    e.widget["background"] = e.widget.default_color

buttons = [
    ("📂 List Files", list_files, "#3498db"),
    ("🗑️ List Deleted Files", list_deleted_files, "#8e44ad"),
    ("🔄 Recover File", recover_files, "#27ae60"),
    ("🛠️ Check Disk", check_disk, "#f39c12"),
    ("🚀 Optimize Disk", optimize_disk, "#e74c3c"),
    ("❌ Delete File", delete_file, "#c0392b")
]

for i, (text, cmd, color) in enumerate(buttons):
    row, col = divmod(i, 2)
    btn = tk.Button(button_frame, text=text, command=cmd, font=("Arial", 11, "bold"),
                    bg=color, fg="white", width=22, height=2, relief="flat")
    btn.default_color = color
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    btn.grid(row=row, column=col, padx=10, pady=5)

# --- Output Box ---
output_frame = ttk.Frame(root)
output_frame.pack(pady=15, fill="both", expand=True)

output_text = tk.Text(output_frame, height=10, width=80, font=("Arial", 11), bg="#23272A", fg="white", wrap="word")
output_text.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(output_frame, command=output_text.yview)
scrollbar.pack(side="right", fill="y")
output_text.config(yscrollcommand=scrollbar.set)

# --- Run Tkinter Main Loop ---
root.mainloop()
