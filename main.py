import os
import streamlit as st
import ctypes
import sys
import subprocess
import datetime

# ---------- Admin Check ----------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    st.warning("⚠️ Please run this app as Administrator for full functionality (e.g., disk check, shadow copy access).")
    st.stop()

# ---------- Functionalities ----------
def list_files():
    directory = "D:\\CODE\\OS_project"
    if not os.path.exists(directory):
        st.error(f"Directory not found: {directory}")
    else:
        files = os.listdir(directory)
        st.success(f"📂 Files in {directory}:")
        for f in files:
            st.write(f"📄 {f}")

def list_deleted_files(drive):
    try:
        cmd = (
            f'powershell -Command "Get-ChildItem -Path \'{drive}:\\$Recycle.Bin\' -Recurse -Force '
            '| Where-Object {{ !$_.PSIsContainer }} '
            '| Select-Object FullName | Format-List"'
        )
        output = os.popen(cmd).read().strip()

        if not output:
            st.info("🗑️ No deleted files found.")
        else:
            st.code(output, language='powershell')
    except Exception as e:
        st.error(f"Error: {str(e)}")

def recover_files(drive, file_name):
    try:
        cmd = (
            'powershell -Command "(Get-WmiObject -Class Win32_ShadowCopy | '
            'Sort-Object -Property InstallDate -Descending | '
            'Select-Object -First 1).DeviceObject"'
        )
        shadow_copy_path = os.popen(cmd).read().strip()
        
        if not shadow_copy_path:
            st.error("❌ No Shadow Copies found.")
            return

        shadow_copy_path = shadow_copy_path.replace("\\??\\", "")
        source_path = f"{shadow_copy_path}{file_name}"

        recovery_dir = os.path.join(f"{drive}:\\", "Recovered_Files")
        os.makedirs(recovery_dir, exist_ok=True)

        base_name = os.path.basename(file_name)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        recovered_path = os.path.join(recovery_dir, f"recovered_{timestamp}_{base_name}")

        copy_cmd = f'powershell -Command "Copy-Item -Path \'{source_path}\' -Destination \'{recovered_path}\'"'
        result = os.system(copy_cmd)

        if result == 0:
            os.system(f'attrib -h -s "{recovered_path}"')
            st.success(f"✅ File recovered to: {recovered_path}")
        else:
            st.error("❌ File recovery failed. It may not exist in shadow copies.")
    except Exception as e:
        st.error(f"Recovery failed: {str(e)}")

def check_disk(drive):
    try:
        process = subprocess.Popen(
            ["chkdsk", f"{drive}:"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output, error = process.communicate()
        st.code(output if output else error, language='bash')
    except Exception as e:
        st.error(f"Error: {e}")

def optimize_disk(drive):
    try:
        os.system(f"defrag {drive}: /U /V")
        st.success("🚀 Disk optimized successfully!")
    except Exception as e:
        st.error(f"Error: {e}")

def delete_file(file_path):
    try:
        os.remove(file_path)
        st.success(f"🗑️ Deleted: {file_path}")
    except Exception as e:
        st.error(f"Could not delete file:\n{e}")

# ---------- UI ----------
st.set_page_config(page_title="File System Recovery & Optimization", layout="centered")
st.title("💾 File System Recovery & Optimization Tool")

option = st.sidebar.selectbox("Select Task", [
    "📂 List Files",
    "🗑️ List Deleted Files",
    "🔄 Recover Deleted File",
    "🛠️ Check Disk",
    "🚀 Optimize Disk",
    "❌ Delete File"
])

if option == "📂 List Files":
    if st.button("List Files"):
        list_files()

elif option == "🗑️ List Deleted Files":
    drive = st.text_input("Enter Drive Letter (e.g., C)")
    if st.button("Show Deleted Files") and drive:
        list_deleted_files(drive)

elif option == "🔄 Recover Deleted File":
    drive = st.text_input("Enter Drive Letter (e.g., C)")
    file_name = st.text_input("Enter Full Deleted File Path (e.g., \\Users\\Name\\file.txt)")
    if st.button("Recover File") and drive and file_name:
        recover_files(drive, file_name)

elif option == "🛠️ Check Disk":
    drive = st.text_input("Enter Drive Letter (e.g., C)")
    if st.button("Check Disk") and drive:
        check_disk(drive)

elif option == "🚀 Optimize Disk":
    drive = st.text_input("Enter Drive Letter (e.g., C)")
    if st.button("Optimize Disk") and drive:
        optimize_disk(drive)

elif option == "❌ Delete File":
    file_path = st.text_input("Enter Full Path of File to Delete")
    if st.button("Delete File") and file_path:
        delete_file(file_path)
