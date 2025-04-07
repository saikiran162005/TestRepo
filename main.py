import streamlit as st
import os
import subprocess
import datetime
import ctypes

st.set_page_config(page_title="File Recovery & Optimization", layout="centered")
st.title("💾 File System Recovery & Optimization (Streamlit)")

# ---------------------- Admin Check ----------------------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    st.warning("⚠️ This app must be run as Administrator to access system-level features like Recycle Bin or Shadow Copy.")
    st.stop()

# ---------------------- Core Functions ----------------------

def list_files(directory):
    if not os.path.exists(directory):
        st.error(f"❌ Directory not found: {directory}")
        return
    files = os.listdir(directory)
    if files:
        st.success(f"📂 Files in {directory}:")
        for file in files:
            st.write(f"📄 {file}")
    else:
        st.info("The folder is empty.")

def list_deleted_files(drive):
    try:
        cmd = (
            f'powershell -Command "Get-ChildItem -Path \'{drive}:\\$Recycle.Bin\' -Recurse -Force '
            '| Where-Object {{ !$_.PSIsContainer }} '
            '| Select-Object FullName | Format-List"'
        )
        output = os.popen(cmd).read().strip()
        if output:
            st.code(output, language='powershell')
        else:
            st.info("🗑️ No deleted files found.")
    except Exception as e:
        st.error(str(e))

def recover_file(drive, deleted_file_path):
    try:
        cmd = (
            'powershell -Command "(Get-WmiObject -Class Win32_ShadowCopy | '
            'Sort-Object -Property InstallDate -Descending | '
            'Select-Object -First 1).DeviceObject"'
        )
        shadow_copy_path = os.popen(cmd).read().strip().replace("\\??\\", "")
        if not shadow_copy_path:
            st.error("❌ No Shadow Copies found.")
            return

        full_source = f"{shadow_copy_path}{deleted_file_path}"
        recovery_dir = os.path.join(f"{drive}:\\", "Recovered_Files")
        os.makedirs(recovery_dir, exist_ok=True)
        base = os.path.basename(deleted_file_path)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(recovery_dir, f"recovered_{timestamp}_{base}")

        copy_cmd = f'powershell -Command "Copy-Item -Path \'{full_source}\' -Destination \'{dest}\'"'
        result = os.system(copy_cmd)

        if result == 0:
            os.system(f'attrib -h -s "{dest}"')
            st.success(f"✅ Recovered to: {dest}")
        else:
            st.error("❌ Recovery failed. File may not exist in Shadow Copy.")
    except Exception as e:
        st.error(str(e))

def check_disk(drive):
    try:
        process = subprocess.Popen(["chkdsk", f"{drive}:"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate()
        st.code(output if output else error, language='bash')
    except Exception as e:
        st.error(str(e))

def optimize_disk(drive):
    try:
        os.system(f"defrag {drive}: /U /V")
        st.success("🚀 Disk optimized.")
    except Exception as e:
        st.error(str(e))

def delete_file(path):
    try:
        os.remove(path)
        st.success(f"🗑️ Deleted: {path}")
    except Exception as e:
        st.error(str(e))

# ---------------------- Sidebar Menu ----------------------
option = st.sidebar.selectbox("Select Action", [
    "📂 List Files",
    "🗑️ List Deleted Files",
    "🔄 Recover File",
    "🛠️ Check Disk",
    "🚀 Optimize Disk",
    "❌ Delete File"
])

# ---------------------- UI Panels ----------------------
if option == "📂 List Files":
    directory = st.text_input("Enter directory path", "D:\\CODE\\OS_project")
    if st.button("List Files"):
        list_files(directory)

elif option == "🗑️ List Deleted Files":
    drive = st.text_input("Drive letter (e.g., C)")
    if st.button("Show Deleted Files") and drive:
        list_deleted_files(drive)

elif option == "🔄 Recover File":
    drive = st.text_input("Drive letter (e.g., C)")
    file_path = st.text_input("Path to deleted file (e.g., \\Users\\John\\Documents\\file.txt)")
    if st.button("Recover") and drive and file_path:
        recover_file(drive, file_path)

elif option == "🛠️ Check Disk":
    drive = st.text_input("Drive letter (e.g., C)")
    if st.button("Run CHKDSK") and drive:
        check_disk(drive)

elif option == "🚀 Optimize Disk":
    drive = st.text_input("Drive letter (e.g., C)")
    if st.button("Defragment") and drive:
        optimize_disk(drive)

elif option == "❌ Delete File":
    file_path = st.text_input("Full path to file you want to delete")
    if st.button("Delete File") and file_path:
        delete_file(file_path)
