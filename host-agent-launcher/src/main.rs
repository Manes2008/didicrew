#![windows_subsystem = "windows"]

use std::process::Command;
use std::sync::{Arc, Mutex};
use tray_item::{IconSource, TrayItem};

#[cfg(target_os = "windows")]
use std::os::windows::process::CommandExt;

#[cfg(target_os = "windows")]
fn create_desktop_shortcut() {
    if let Ok(current_exe) = std::env::current_exe() {
        let exe_path = current_exe.to_string_lossy().replace('\\', "/");
        let work_dir = current_exe.parent().unwrap().to_string_lossy().replace('\\', "/");
        
        let script = format!(
            r#"$WshShell = New-Object -ComObject WScript.Shell; $Desktop = [System.Environment]::GetFolderPath('Desktop'); $Shortcut = $WshShell.CreateShortcut("$Desktop/VideoCrew Agent.lnk"); $Shortcut.TargetPath = "{}"; $Shortcut.WorkingDirectory = "{}"; $Shortcut.IconLocation = "{},0"; $Shortcut.Save()"#,
            exe_path, work_dir, exe_path
        );
        
        // Chạy PowerShell ngầm để tạo shortcut
        let _ = Command::new("powershell")
            .args(["-NoProfile", "-NonInteractive", "-Command", &script])
            .creation_flags(0x08000000) // CREATE_NO_WINDOW
            .status();
    }
}

fn main() {
    // Tự động tạo hoặc cập nhật shortcut ngoài Desktop khi bật launcher
    #[cfg(target_os = "windows")]
    create_desktop_shortcut();

    // 1. Tìm đường dẫn file python.exe phù hợp (môi trường ảo venv hoặc python hệ thống)
    let python_exe = if std::path::Path::new("../venv/Scripts/python.exe").exists() {
        "../venv/Scripts/python.exe"
    } else if std::path::Path::new("venv/Scripts/python.exe").exists() {
        "venv/Scripts/python.exe"
    } else {
        "python"
    };

    // 2. Định vị file host_agent.py phù hợp
    let script_path = if std::path::Path::new("host_agent.py").exists() {
        "host_agent.py"
    } else {
        "../host_agent.py"
    };

    // 3. Khởi chạy host_agent.py ngầm dưới dạng Child Process
    let child = Command::new(python_exe)
        .arg(script_path)
        .spawn();

    let child_arc = Arc::new(Mutex::new(child));

    // 4. Khởi tạo biểu tượng khay hệ thống (System Tray Icon)
    // Xử lý lỗi mềm dẻo nếu không tạo được (ví dụ do chạy dưới quyền Administrator - UIPI hoặc không có taskbar)
    let tray = TrayItem::new("VideoCrew Host Agent", IconSource::Resource("app_icon"));
    match tray {
        Ok(mut t) => {
            let _ = t.add_label("Host Agent is running...");
            let child_clone = Arc::clone(&child_arc);
            let _ = t.add_menu_item("Exit", move || {
                let mut child_guard = child_clone.lock().unwrap();
                if let Ok(ref mut child_process) = *child_guard {
                    let _ = child_process.kill(); // Kill tiến trình python ngầm
                }
                std::process::exit(0);
            });

            // Vòng lặp duy trì hoạt động và tự động thoát khi đóng cửa sổ Dashboard Python
            loop {
                std::thread::sleep(std::time::Duration::from_secs(2));
                let mut child_guard = child_clone.lock().unwrap();
                if let Ok(ref mut child_process) = *child_guard {
                    match child_process.try_wait() {
                        Ok(Some(_status)) => {
                            // Tiến trình con đã kết thúc, thoát launcher luôn
                            std::process::exit(0);
                        }
                        _ => {}
                    }
                }
            }
        }
        Err(e) => {
            println!("[WARN] Khong the tao System Tray Icon: {:?}", e);
            // Vẫn tiếp tục chạy ngầm để quản lý tiến trình Python
            loop {
                std::thread::sleep(std::time::Duration::from_secs(2));
                let mut child_guard = child_arc.lock().unwrap();
                if let Ok(ref mut child_process) = *child_guard {
                    match child_process.try_wait() {
                        Ok(Some(_status)) => {
                            // Tiến trình con đã kết thúc, thoát launcher luôn
                            std::process::exit(0);
                        }
                        _ => {}
                    }
                }
            }
        }
    }
}
