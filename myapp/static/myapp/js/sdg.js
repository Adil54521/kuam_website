document.addEventListener("DOMContentLoaded", () => {
    const page = document.body;
    const activeLanguage = page.dataset.activeLanguage || document.documentElement.lang;
    const storedLanguage = localStorage.getItem("lang");
    const hasLanguageCookie = document.cookie
        .split(";")
        .some((item) => item.trim().startsWith("django_language="));
    if (
        ["kk", "ru", "en"].includes(storedLanguage) &&
        storedLanguage !== activeLanguage &&
        !hasLanguageCookie
    ) {
        const migrationUrl = new URL(
            page.dataset.setLanguageUrl,
            window.location.origin,
        );
        migrationUrl.searchParams.set("lang", storedLanguage);
        migrationUrl.searchParams.set(
            "next",
            window.location.pathname + window.location.search,
        );
        if (window.location.hash) {
            migrationUrl.searchParams.set("anchor", window.location.hash.slice(1));
        }
        window.location.replace(migrationUrl.toString());
        return;
    }
    if (["kk", "ru", "en"].includes(activeLanguage)) {
        localStorage.setItem("lang", activeLanguage);
    }

    document.querySelectorAll("[data-language-link]").forEach((link) => {
        link.addEventListener("click", () => {
            if (!window.location.hash) return;
            const target = new URL(link.href, window.location.origin);
            target.searchParams.set("anchor", window.location.hash.slice(1));
            link.href = target.toString();
        });
    });

    const revealItems = document.querySelectorAll(".reveal");

    if (!("IntersectionObserver" in window)) {
        revealItems.forEach((element) => element.classList.add("show"));
        return;
    }

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("show");
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.12 },
    );

    revealItems.forEach((element) => observer.observe(element));
});
