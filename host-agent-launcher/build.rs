fn main() {
    if std::env::var("CARGO_CFG_TARGET_OS").unwrap() == "windows" {
        let mut res = winres::WindowsResource::new();
        res.set_icon_with_id("favicon.ico", "app_icon"); // Đặt tên ID tài nguyên là app_icon
        res.compile().unwrap();
    }
}
