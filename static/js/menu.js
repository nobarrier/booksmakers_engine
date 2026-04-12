document.addEventListener("DOMContentLoaded", function () {

    const topbar = document.querySelector(".category-bar");
    const sidebar = document.querySelector(".sidebar-menu");

    /* 전체 open 제거 (Topbar용) */
    function closeAll() {
        document.querySelectorAll("li.open")
            .forEach(item => item.classList.remove("open"));
    }

    /* 같은 레벨만 닫기 (Sidebar용) */
    function closeSiblings(li) {
        const parent = li.parentElement;
        if (!parent) return;
        Array.from(parent.children).forEach(sib => {
            if (sib !== li) sib.classList.remove("open");
        });
    }

    /* =========================
       TOPBAR CONTROL
    ========================== */
    if (topbar) {

        topbar.addEventListener("mouseover", function (e) {

            const li = e.target.closest("li");
            if (!li || !topbar.contains(li)) return;

            closeAll();  // Sidebar 포함 전체 닫기

            if (li.querySelector(":scope > ul, :scope > .top-dropdown")) {
                li.classList.add("open");
            }
        });

        topbar.addEventListener("mouseleave", function () {
            closeAll();
        });
    }

    /* =========================
       SIDEBAR CONTROL
    ========================== */
    if (sidebar) {

        sidebar.querySelectorAll("li").forEach(li => {

            li.addEventListener("mouseenter", function () {

                closeSiblings(li);  // 같은 레벨만 닫기

                if (li.querySelector(":scope > ul")) {
                    li.classList.add("open");
                }
            });

        });

        sidebar.addEventListener("mouseleave", function () {
            closeAll();
        });
    }

    /* =========================
       빈 하위 UL 제거
    ========================== */
    document.querySelectorAll(".sidebar-menu li > ul").forEach(ul => {
        const hasItem = Array.from(ul.children)
            .some(li => li.tagName === "LI");

        if (!hasItem) {
            ul.remove();
        }
    });

});
