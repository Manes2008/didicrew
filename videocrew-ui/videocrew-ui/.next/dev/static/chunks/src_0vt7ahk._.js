(globalThis["TURBOPACK"] || (globalThis["TURBOPACK"] = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/src/components/AppInitializer.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "AppInitializer",
    ()=>AppInitializer
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$stores$2f$useChannelStore$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/stores/useChannelStore.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$stores$2f$useConfigStore$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/stores/useConfigStore.ts [app-client] (ecmascript)");
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
function AppInitializer() {
    _s();
    const fetchChannels = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$stores$2f$useChannelStore$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useChannelStore"])({
        "AppInitializer.useChannelStore[fetchChannels]": (state)=>state.fetchChannels
    }["AppInitializer.useChannelStore[fetchChannels]"]);
    const fetchConfig = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$stores$2f$useConfigStore$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useConfigStore"])({
        "AppInitializer.useConfigStore[fetchConfig]": (state)=>state.fetchConfig
    }["AppInitializer.useConfigStore[fetchConfig]"]);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "AppInitializer.useEffect": ()=>{
            // Pre-fetch global data in background when app mounts
            fetchChannels().catch(console.error);
            fetchConfig().catch(console.error);
        }
    }["AppInitializer.useEffect"], [
        fetchChannels,
        fetchConfig
    ]);
    return null;
}
_s(AppInitializer, "X3gUywIWkwXzQUwVFqHre/B2BOo=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$stores$2f$useChannelStore$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useChannelStore"],
        __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$stores$2f$useConfigStore$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useConfigStore"]
    ];
});
_c = AppInitializer;
var _c;
__turbopack_context__.k.register(_c, "AppInitializer");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/src/components/AuthGuard.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "AuthGuard",
    ()=>AuthGuard
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/navigation.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$Sidebar$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/Sidebar.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
function AuthGuard({ children }) {
    _s();
    const pathname = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["usePathname"])();
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"])();
    const [isAuthenticated, setIsAuthenticated] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const isLoginPage = pathname ? pathname === "/login" || pathname === "/login/" || pathname.startsWith("/login") : false;
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "AuthGuard.useEffect": ()=>{
            try {
                const user = localStorage.getItem("user");
                if (!user) {
                    setIsAuthenticated(false);
                    if (!isLoginPage) {
                        router.replace("/login");
                    }
                } else {
                    setIsAuthenticated(true);
                    if (isLoginPage) {
                        router.replace("/");
                    }
                }
            } catch (e) {
                setIsAuthenticated(false);
            }
        }
    }["AuthGuard.useEffect"], [
        pathname,
        isLoginPage,
        router
    ]);
    // Loading check session
    if (isAuthenticated === null) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "min-h-screen w-full flex items-center justify-center bg-[#0f1117] text-zinc-400 font-medium text-sm",
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex items-center gap-2",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "w-4 h-4 border-2 border-[#C2542D] border-t-transparent rounded-full animate-spin"
                    }, void 0, false, {
                        fileName: "[project]/src/components/AuthGuard.tsx",
                        lineNumber: 38,
                        columnNumber: 11
                    }, this),
                    "Đang xác thực bảo mật..."
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/AuthGuard.tsx",
                lineNumber: 37,
                columnNumber: 9
            }, this)
        }, void 0, false, {
            fileName: "[project]/src/components/AuthGuard.tsx",
            lineNumber: 36,
            columnNumber: 7
        }, this);
    }
    // Nếu đang ở trang login, luôn render form login
    if (isLoginPage) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
            className: "flex-1 w-full min-h-screen flex items-center justify-center",
            children: children
        }, void 0, false, {
            fileName: "[project]/src/components/AuthGuard.tsx",
            lineNumber: 47,
            columnNumber: 12
        }, this);
    }
    // Nếu chưa đăng nhập và không phải trang login
    if (!isAuthenticated) {
        return null;
    }
    // Đã đăng nhập -> Render đầy đủ Sidebar và nội dung
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Fragment"], {
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$Sidebar$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Sidebar"], {}, void 0, false, {
                fileName: "[project]/src/components/AuthGuard.tsx",
                lineNumber: 58,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
                className: "flex-1 p-8 overflow-y-auto max-w-7xl mx-auto w-full",
                children: children
            }, void 0, false, {
                fileName: "[project]/src/components/AuthGuard.tsx",
                lineNumber: 59,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/src/components/AuthGuard.tsx",
        lineNumber: 57,
        columnNumber: 5
    }, this);
}
_s(AuthGuard, "hSNf6vkbdUP3jmNvHgKdAMYe9D0=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["usePathname"],
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"]
    ];
});
_c = AuthGuard;
var _c;
__turbopack_context__.k.register(_c, "AuthGuard");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/src/components/Sidebar.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "Sidebar",
    ()=>Sidebar
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/client/app-dir/link.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/navigation.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$film$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Film$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/film.mjs [app-client] (ecmascript) <export default as Film>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$layers$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Layers$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/layers.mjs [app-client] (ecmascript) <export default as Layers>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$settings$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Settings$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/settings.mjs [app-client] (ecmascript) <export default as Settings>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chart$2d$column$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__BarChart3$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chart-column.mjs [app-client] (ecmascript) <export default as BarChart3>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$shield$2d$check$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ShieldCheck$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/shield-check.mjs [app-client] (ecmascript) <export default as ShieldCheck>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$monitor$2d$play$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__MonitorPlay$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/monitor-play.mjs [app-client] (ecmascript) <export default as MonitorPlay>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$radio$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Radio$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/radio.mjs [app-client] (ecmascript) <export default as Radio>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$monitor$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Monitor$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/monitor.mjs [app-client] (ecmascript) <export default as Monitor>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$log$2d$out$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__LogOut$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/log-out.mjs [app-client] (ecmascript) <export default as LogOut>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$log$2d$in$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__LogIn$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/log-in.mjs [app-client] (ecmascript) <export default as LogIn>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$panel$2d$left$2d$close$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__PanelLeftClose$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/panel-left-close.mjs [app-client] (ecmascript) <export default as PanelLeftClose>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$panel$2d$left$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__PanelLeft$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/panel-left.mjs [app-client] (ecmascript) <export default as PanelLeft>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
;
function Sidebar() {
    _s();
    const pathname = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["usePathname"])();
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"])();
    const [currentUser, setCurrentUser] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [isCollapsed, setIsCollapsed] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "Sidebar.useEffect": ()=>{
            try {
                const stored = localStorage.getItem("user");
                if (stored) setCurrentUser(JSON.parse(stored));
                const storedCollapsed = localStorage.getItem("sidebar_collapsed");
                if (storedCollapsed !== null) {
                    setIsCollapsed(storedCollapsed === "true");
                }
            } catch (e) {}
        }
    }["Sidebar.useEffect"], []);
    const toggleCollapse = ()=>{
        const next = !isCollapsed;
        setIsCollapsed(next);
        try {
            localStorage.setItem("sidebar_collapsed", String(next));
        } catch (e) {}
    };
    const handleLogout = ()=>{
        localStorage.removeItem("user");
        setCurrentUser(null);
        router.push("/login");
    };
    const navItems = [
        {
            href: "/",
            label: "Tổng quan (Dashboard)",
            icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chart$2d$column$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__BarChart3$3e$__["BarChart3"]
        },
        {
            href: "/production",
            label: "Sản xuất Video AI",
            icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$film$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Film$3e$__["Film"],
            badge: "Live"
        },
        {
            href: "/channels",
            label: "Quản lý Kênh",
            icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$layers$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Layers$3e$__["Layers"]
        },
        {
            href: "/config",
            label: "Cấu hình AI & Engine",
            icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$settings$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Settings$3e$__["Settings"]
        },
        {
            href: "/analytics",
            label: "Phân tích Hiệu quả",
            icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chart$2d$column$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__BarChart3$3e$__["BarChart3"]
        },
        {
            href: "/ip-manager",
            label: "Quản lý IP Admin",
            icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$shield$2d$check$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ShieldCheck$3e$__["ShieldCheck"]
        },
        {
            href: "/rustdesk",
            label: "Cấu hình RustDesk",
            icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$monitor$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Monitor$3e$__["Monitor"]
        }
    ];
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("aside", {
        className: `border-r border-[var(--vc-border)] bg-[var(--vc-card-bg)] backdrop-blur-xl flex flex-col justify-between p-3 min-h-screen sticky top-0 transition-all duration-300 ${isCollapsed ? "w-20" : "w-64"}`,
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex items-center justify-between pb-4 mb-4 border-b border-[var(--vc-border)]",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "flex items-center gap-3 overflow-hidden",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        className: "w-10 h-10 min-w-[40px] rounded-xl flex items-center justify-center bg-gradient-to-br from-[#C2542D] to-[#C99A45] shadow-lg shadow-[#C2542D]/20",
                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$monitor$2d$play$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__MonitorPlay$3e$__["MonitorPlay"], {
                                            className: "w-5 h-5 text-white"
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/Sidebar.tsx",
                                            lineNumber: 73,
                                            columnNumber: 15
                                        }, this)
                                    }, void 0, false, {
                                        fileName: "[project]/src/components/Sidebar.tsx",
                                        lineNumber: 72,
                                        columnNumber: 13
                                    }, this),
                                    !isCollapsed && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        className: "truncate",
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                                                className: "font-extrabold text-base leading-tight gradient-text truncate",
                                                children: "VideoCrew"
                                            }, void 0, false, {
                                                fileName: "[project]/src/components/Sidebar.tsx",
                                                lineNumber: 77,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                className: "text-[11px] text-[var(--vc-muted)] font-medium",
                                                children: "Studio v2.0 Next.js"
                                            }, void 0, false, {
                                                fileName: "[project]/src/components/Sidebar.tsx",
                                                lineNumber: 80,
                                                columnNumber: 17
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/src/components/Sidebar.tsx",
                                        lineNumber: 76,
                                        columnNumber: 15
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/components/Sidebar.tsx",
                                lineNumber: 71,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                onClick: toggleCollapse,
                                title: isCollapsed ? "Mở rộng Sidebar" : "Thu gọn Sidebar",
                                className: "p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-white/[0.06] transition",
                                children: isCollapsed ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$panel$2d$left$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__PanelLeft$3e$__["PanelLeft"], {
                                    className: "w-4 h-4 text-amber-400"
                                }, void 0, false, {
                                    fileName: "[project]/src/components/Sidebar.tsx",
                                    lineNumber: 91,
                                    columnNumber: 28
                                }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$panel$2d$left$2d$close$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__PanelLeftClose$3e$__["PanelLeftClose"], {
                                    className: "w-4 h-4 text-zinc-400"
                                }, void 0, false, {
                                    fileName: "[project]/src/components/Sidebar.tsx",
                                    lineNumber: 91,
                                    columnNumber: 79
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/src/components/Sidebar.tsx",
                                lineNumber: 85,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/Sidebar.tsx",
                        lineNumber: 70,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("nav", {
                        className: "space-y-1",
                        children: [
                            !isCollapsed && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "text-[10px] uppercase font-bold tracking-wider text-[var(--vc-muted)] px-3 mb-2",
                                children: "Menu Điều Hướng"
                            }, void 0, false, {
                                fileName: "[project]/src/components/Sidebar.tsx",
                                lineNumber: 98,
                                columnNumber: 13
                            }, this),
                            navItems.map((item)=>{
                                const Icon = item.icon;
                                const isActive = pathname === item.href;
                                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                                    href: item.href,
                                    title: isCollapsed ? item.label : undefined,
                                    className: `flex items-center ${isCollapsed ? "justify-center px-2" : "justify-between px-3"} py-2.5 rounded-xl font-medium text-xs transition-all duration-200 ${isActive ? "bg-[var(--vc-accent-soft)] text-[#C2542D] border border-[var(--vc-accent-soft-strong)] shadow-sm font-bold" : "text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.04]"}`,
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            className: `flex items-center ${isCollapsed ? "justify-center" : "gap-2.5"} truncate`,
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(Icon, {
                                                    className: `w-4 h-4 min-w-[16px] ${isActive ? "text-[#C2542D]" : "text-zinc-400"}`
                                                }, void 0, false, {
                                                    fileName: "[project]/src/components/Sidebar.tsx",
                                                    lineNumber: 119,
                                                    columnNumber: 19
                                                }, this),
                                                !isCollapsed && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                    className: "truncate",
                                                    children: item.label
                                                }, void 0, false, {
                                                    fileName: "[project]/src/components/Sidebar.tsx",
                                                    lineNumber: 120,
                                                    columnNumber: 36
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/src/components/Sidebar.tsx",
                                            lineNumber: 118,
                                            columnNumber: 17
                                        }, this),
                                        !isCollapsed && item.badge && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            className: "text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-[#C2542D] text-white animate-pulse",
                                            children: item.badge
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/Sidebar.tsx",
                                            lineNumber: 123,
                                            columnNumber: 19
                                        }, this)
                                    ]
                                }, item.href, true, {
                                    fileName: "[project]/src/components/Sidebar.tsx",
                                    lineNumber: 106,
                                    columnNumber: 15
                                }, this);
                            })
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/Sidebar.tsx",
                        lineNumber: 96,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/Sidebar.tsx",
                lineNumber: 69,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "space-y-2.5 mt-4",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: `glass-panel ${isCollapsed ? "p-2 text-center" : "p-3"} border-[var(--vc-border)]`,
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: `flex items-center ${isCollapsed ? "justify-center" : "justify-between"} mb-1`,
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                        className: "text-[11px] font-semibold text-zinc-300 flex items-center gap-1.5",
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$radio$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Radio$3e$__["Radio"], {
                                                className: "w-3 h-3 text-emerald-400 animate-ping"
                                            }, void 0, false, {
                                                fileName: "[project]/src/components/Sidebar.tsx",
                                                lineNumber: 138,
                                                columnNumber: 15
                                            }, this),
                                            !isCollapsed && "DidicrewStudio"
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/src/components/Sidebar.tsx",
                                        lineNumber: 137,
                                        columnNumber: 13
                                    }, this),
                                    !isCollapsed && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                        className: "vc-badge text-[9px] py-0 px-1.5",
                                        children: "Online"
                                    }, void 0, false, {
                                        fileName: "[project]/src/components/Sidebar.tsx",
                                        lineNumber: 141,
                                        columnNumber: 30
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/components/Sidebar.tsx",
                                lineNumber: 136,
                                columnNumber: 11
                            }, this),
                            !isCollapsed && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "text-[10px] text-[var(--vc-muted)] space-y-0.5 border-t border-[var(--vc-border)] pt-1.5 mt-1",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        className: "flex justify-between",
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                children: "Người dùng:"
                                            }, void 0, false, {
                                                fileName: "[project]/src/components/Sidebar.tsx",
                                                lineNumber: 146,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                className: "font-semibold text-zinc-200 truncate ml-1",
                                                children: currentUser?.username || "Didicrew07"
                                            }, void 0, false, {
                                                fileName: "[project]/src/components/Sidebar.tsx",
                                                lineNumber: 147,
                                                columnNumber: 17
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/src/components/Sidebar.tsx",
                                        lineNumber: 145,
                                        columnNumber: 15
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        className: "flex justify-between",
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                children: "Client IP:"
                                            }, void 0, false, {
                                                fileName: "[project]/src/components/Sidebar.tsx",
                                                lineNumber: 152,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                className: "font-mono text-zinc-300",
                                                children: "127.0.0.1"
                                            }, void 0, false, {
                                                fileName: "[project]/src/components/Sidebar.tsx",
                                                lineNumber: 153,
                                                columnNumber: 17
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/src/components/Sidebar.tsx",
                                        lineNumber: 151,
                                        columnNumber: 15
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/components/Sidebar.tsx",
                                lineNumber: 144,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/Sidebar.tsx",
                        lineNumber: 135,
                        columnNumber: 9
                    }, this),
                    currentUser ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        onClick: handleLogout,
                        title: isCollapsed ? "Đăng Xuất" : undefined,
                        className: `w-full flex items-center ${isCollapsed ? "justify-center p-2" : "justify-center gap-2 py-2"} rounded-xl text-xs font-semibold text-zinc-400 hover:text-red-400 bg-white/[0.03] hover:bg-red-500/10 border border-white/5 transition`,
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$log$2d$out$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__LogOut$3e$__["LogOut"], {
                                className: "w-3.5 h-3.5"
                            }, void 0, false, {
                                fileName: "[project]/src/components/Sidebar.tsx",
                                lineNumber: 167,
                                columnNumber: 13
                            }, this),
                            !isCollapsed && "Đăng Xuất"
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/Sidebar.tsx",
                        lineNumber: 160,
                        columnNumber: 11
                    }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                        href: "/login",
                        title: isCollapsed ? "Đăng Nhập" : undefined,
                        className: `w-full flex items-center ${isCollapsed ? "justify-center p-2" : "justify-center gap-2 py-2"} rounded-xl text-xs font-semibold text-zinc-300 hover:text-white bg-white/[0.05] hover:bg-white/[0.08] border border-white/10 transition`,
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$log$2d$in$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__LogIn$3e$__["LogIn"], {
                                className: "w-3.5 h-3.5 text-[#C2542D]"
                            }, void 0, false, {
                                fileName: "[project]/src/components/Sidebar.tsx",
                                lineNumber: 178,
                                columnNumber: 13
                            }, this),
                            !isCollapsed && "Đăng Nhập"
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/Sidebar.tsx",
                        lineNumber: 171,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/Sidebar.tsx",
                lineNumber: 134,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/src/components/Sidebar.tsx",
        lineNumber: 65,
        columnNumber: 5
    }, this);
}
_s(Sidebar, "gqn0wawuAYSFuhOI5nWzX9vHQh0=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["usePathname"],
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"]
    ];
});
_c = Sidebar;
var _c;
__turbopack_context__.k.register(_c, "Sidebar");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/src/lib/api-client.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "API_BASE_URL",
    ()=>API_BASE_URL,
    "WS_BASE_URL",
    ()=>WS_BASE_URL,
    "apiClient",
    ()=>apiClient
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = /*#__PURE__*/ __turbopack_context__.i("[project]/node_modules/next/dist/build/polyfills/process.js [app-client] (ecmascript)");
const API_BASE_URL = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"].env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";
const WS_BASE_URL = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"].env.NEXT_PUBLIC_WS_URL || "ws://127.0.0.1:8000/ws";
const apiClient = {
    // Auth
    async login (username, password) {
        const res = await fetch(`${API_BASE_URL}/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username,
                password
            })
        });
        if (!res.ok) {
            const err = await res.json().catch(()=>({}));
            throw new Error(err.detail || "Đăng nhập thất bại");
        }
        return res.json();
    },
    async register (username, password, device_label) {
        const res = await fetch(`${API_BASE_URL}/auth/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username,
                password,
                device_label
            })
        });
        if (!res.ok) {
            const err = await res.json().catch(()=>({}));
            throw new Error(err.detail || "Đăng ký thất bại");
        }
        return res.json();
    },
    // Channels
    async getChannels () {
        const res = await fetch(`${API_BASE_URL}/channels`);
        if (!res.ok) throw new Error("Khong the lay danh sach kenh");
        return res.json();
    },
    async createChannel (data) {
        const res = await fetch(`${API_BASE_URL}/channels`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });
        if (!res.ok) {
            const err = await res.json().catch(()=>({}));
            throw new Error(err.detail || "Loi khi tao kenh moi");
        }
        return res.json();
    },
    async updateChannel (id, data) {
        const res = await fetch(`${API_BASE_URL}/channels/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });
        if (!res.ok) {
            const err = await res.json().catch(()=>({}));
            throw new Error(err.detail || "Loi khi cap nhat kenh");
        }
        return res.json();
    },
    async deleteChannel (id) {
        const res = await fetch(`${API_BASE_URL}/channels/${id}`, {
            method: "DELETE"
        });
        if (!res.ok) throw new Error("Khong the xoa kenh");
    },
    // Production
    async triggerVideoGeneration (payload) {
        const res = await fetch(`${API_BASE_URL}/production/generate`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });
        if (!res.ok) {
            const err = await res.json().catch(()=>({}));
            throw new Error(err.detail || "Loi khi khoi tao san xuat video");
        }
        return res.json();
    },
    async triggerSingleStage (payload) {
        const res = await fetch(`${API_BASE_URL}/production/stage/run`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });
        if (!res.ok) {
            const err = await res.json().catch(()=>({}));
            throw new Error(err.detail || "Loi khi chay stage don le");
        }
        return res.json();
    },
    async getChannelProjects (channelId) {
        const res = await fetch(`${API_BASE_URL}/production/channels/${channelId}/projects`);
        if (!res.ok) throw new Error("Khong the lay danh sach du an cua kenh");
        return res.json();
    },
    async getProjectDetail (projectId) {
        const res = await fetch(`${API_BASE_URL}/production/projects/${projectId}`);
        if (!res.ok) throw new Error("Khong the lay chi tiet du an");
        return res.json();
    },
    // System Config
    async getConfig () {
        const res = await fetch(`${API_BASE_URL}/config`);
        if (!res.ok) throw new Error("Khong the lay cau hinh he thong");
        return res.json();
    },
    async updateConfig (data) {
        const res = await fetch(`${API_BASE_URL}/config`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error("Loi khi cap nhat cau hinh");
        return res.json();
    },
    async testApiKey (provider, apiKey) {
        const res = await fetch(`${API_BASE_URL}/config/test-key`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                provider,
                api_key: apiKey
            })
        });
        if (!res.ok) {
            const err = await res.json().catch(()=>({}));
            throw new Error(err.detail || "Lỗi kiểm tra API Key");
        }
        return res.json();
    },
    // Analytics
    async getAnalytics () {
        const res = await fetch(`${API_BASE_URL}/analytics/summary`);
        if (!res.ok) throw new Error("Khong the lay du lieu analytics");
        return res.json();
    },
    // IP Manager
    async getIPList () {
        const res = await fetch(`${API_BASE_URL}/ip-manager`);
        if (!res.ok) throw new Error("Khong the lay danh sach IP");
        return res.json();
    },
    async updateIP (id, status, is_admin_ip) {
        const res = await fetch(`${API_BASE_URL}/ip-manager/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                status,
                is_admin_ip
            })
        });
        if (!res.ok) throw new Error("Khong the cap nhat trang thai IP");
        return res.json();
    },
    async deleteIP (id) {
        const res = await fetch(`${API_BASE_URL}/ip-manager/${id}`, {
            method: "DELETE"
        });
        if (!res.ok) throw new Error("Khong the xoa IP");
    },
    // RustDesk
    async getRustDeskConfig () {
        const res = await fetch(`${API_BASE_URL}/rustdesk`);
        if (!res.ok) throw new Error("Khong the lay cau hinh RustDesk");
        return res.json();
    },
    async updateRustDeskConfig (data) {
        const res = await fetch(`${API_BASE_URL}/rustdesk`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error("Khong the cap nhat RustDesk");
        return res.json();
    }
};
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/src/stores/useChannelStore.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "useChannelStore",
    ()=>useChannelStore
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/zustand/esm/react.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2d$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/lib/api-client.ts [app-client] (ecmascript)");
;
;
const useChannelStore = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["create"])((set, get)=>({
        channels: [],
        selectedChannelId: null,
        isLoading: false,
        isLoaded: false,
        error: null,
        fetchChannels: async (force = false)=>{
            if (get().isLoaded && !force && get().channels.length > 0) {
                return get().channels;
            }
            set({
                isLoading: true,
                error: null
            });
            try {
                const channels = await __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2d$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].getChannels();
                const currentSelected = get().selectedChannelId;
                const validSelected = channels.some((c)=>c.id === currentSelected) ? currentSelected : channels.length > 0 ? channels[0].id : null;
                set({
                    channels,
                    selectedChannelId: validSelected,
                    isLoading: false,
                    isLoaded: true
                });
                return channels;
            } catch (err) {
                const errorMsg = err.message || "Khong the tai danh sach kenh";
                set({
                    isLoading: false,
                    isLoaded: true,
                    error: errorMsg
                });
                return [];
            }
        },
        setSelectedChannelId: (id)=>set({
                selectedChannelId: id
            }),
        createChannel: async (data)=>{
            set({
                isLoading: true,
                error: null
            });
            try {
                const newChannel = await __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2d$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].createChannel(data);
                const updatedChannels = [
                    ...get().channels,
                    newChannel
                ];
                set({
                    channels: updatedChannels,
                    selectedChannelId: get().selectedChannelId ?? newChannel.id,
                    isLoading: false
                });
                return newChannel;
            } catch (err) {
                set({
                    isLoading: false,
                    error: err.message
                });
                throw err;
            }
        },
        updateChannel: async (id, data)=>{
            set({
                isLoading: true,
                error: null
            });
            try {
                const updated = await __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2d$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].updateChannel(id, data);
                const updatedChannels = get().channels.map((c)=>c.id === id ? updated : c);
                set({
                    channels: updatedChannels,
                    isLoading: false
                });
                return updated;
            } catch (err) {
                set({
                    isLoading: false,
                    error: err.message
                });
                throw err;
            }
        },
        deleteChannel: async (id)=>{
            set({
                isLoading: true,
                error: null
            });
            try {
                await __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2d$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].deleteChannel(id);
                const updatedChannels = get().channels.filter((c)=>c.id !== id);
                const newSelected = get().selectedChannelId === id ? updatedChannels.length > 0 ? updatedChannels[0].id : null : get().selectedChannelId;
                set({
                    channels: updatedChannels,
                    selectedChannelId: newSelected,
                    isLoading: false
                });
            } catch (err) {
                set({
                    isLoading: false,
                    error: err.message
                });
                throw err;
            }
        }
    }));
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/src/stores/useConfigStore.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "useConfigStore",
    ()=>useConfigStore
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/zustand/esm/react.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2d$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/lib/api-client.ts [app-client] (ecmascript)");
;
;
const useConfigStore = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["create"])((set, get)=>({
        config: null,
        isLoading: false,
        isLoaded: false,
        error: null,
        fetchConfig: async (force = false)=>{
            if (get().isLoaded && !force && get().config) {
                return get().config;
            }
            set({
                isLoading: true,
                error: null
            });
            try {
                const config = await __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2d$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].getConfig();
                set({
                    config,
                    isLoading: false,
                    isLoaded: true
                });
                return config;
            } catch (err) {
                const errorMsg = err.message || "Khong the tai cau hinh he thong";
                set({
                    isLoading: false,
                    isLoaded: true,
                    error: errorMsg
                });
                return null;
            }
        },
        updateConfig: async (data)=>{
            set({
                isLoading: true,
                error: null
            });
            try {
                const updated = await __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2d$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].updateConfig(data);
                set({
                    config: updated,
                    isLoading: false,
                    isLoaded: true
                });
                return updated;
            } catch (err) {
                set({
                    isLoading: false,
                    error: err.message
                });
                throw err;
            }
        }
    }));
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=src_0vt7ahk._.js.map