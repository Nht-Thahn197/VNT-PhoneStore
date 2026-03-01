(() => {
    const root = document.querySelector("[data-notify]");
    if (!root) return;

    const button = root.querySelector("[data-notify-button]");
    const panel = root.querySelector("[data-notify-panel]");
    const list = root.querySelector("[data-notify-list]");
    const badge = root.querySelector("[data-notify-badge]");
    const endpoint = "/dashboard/orders/notifications/";

    let unreadCount = 0;
    let isOpen = false;

    const formatVnd = (value) => {
        const rounded = Math.round(value || 0);
        return `${rounded}`.replace(/\B(?=(\d{3})+(?!\d))/g, ".") + "đ";
    };

    const formatRelative = (isoString) => {
        if (!isoString) return "";
        const now = Date.now();
        const time = new Date(isoString).getTime();
        const diff = Math.max(0, now - time);
        const minutes = Math.floor(diff / 60000);
        if (minutes < 1) return "Vừa xong";
        if (minutes < 60) return `${minutes} phút trước`;
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours} giờ trước`;
        const days = Math.floor(hours / 24);
        return `${days} ngày trước`;
    };

    let audioContext = null;

    const ensureAudioContext = () => {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) return null;
        if (!audioContext) {
            audioContext = new AudioCtx();
        }
        if (audioContext.state === "suspended") {
            audioContext.resume();
        }
        return audioContext;
    };

    const playSound = () => {
        try {
            const ctx = ensureAudioContext();
            if (!ctx) return;
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.type = "sine";
            osc.frequency.value = 880;
            gain.gain.setValueAtTime(0.001, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.2, ctx.currentTime + 0.02);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);

            osc.connect(gain).connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.4);
            osc.onended = () => {
                gain.disconnect();
                osc.disconnect();
            };
        } catch (error) {
        }
    };

    const setBadge = (count) => {
        unreadCount = count;
        if (!badge) return;
        badge.textContent = count > 99 ? "99+" : `${count}`;
        badge.classList.toggle("is-visible", count > 0);
        badge.hidden = count <= 0;
    };

    const renderOrders = (orders) => {
        if (!list) return;
        list.innerHTML = "";
        if (!orders || !orders.length) {
            const empty = document.createElement("div");
            empty.className = "empty-state";
            empty.textContent = "Chưa có đơn hàng mới.";
            list.appendChild(empty);
            return;
        }

        orders.forEach((order) => {
            const item = document.createElement("a");
            item.className = "notify-item";
            item.href = `/dashboard/orders/${order.id}/`;
            item.innerHTML = `
                <strong>Đơn #${order.id} · ${order.full_name}</strong>
                <span>${formatVnd(order.total)} · ${formatRelative(order.created_at)}</span>
            `;
            list.appendChild(item);
        });
    };

    const fetchNotifications = async () => {
        try {
            const response = await fetch(endpoint, {
                headers: { "X-Requested-With": "XMLHttpRequest" },
                credentials: "same-origin",
            });
            if (!response.ok) return;
            const data = await response.json();
            renderOrders(data.orders || []);

            if (data.new_count && data.new_count > 0) {
                setBadge(unreadCount + data.new_count);
                playSound();
            }
        } catch (error) {
        }
    };

    const togglePanel = (nextState) => {
        isOpen = typeof nextState === "boolean" ? nextState : !isOpen;
        panel.classList.toggle("is-open", isOpen);
        panel.hidden = !isOpen;
        if (isOpen) {
            setBadge(0);
        }
    };

    button.addEventListener("click", (event) => {
        event.stopPropagation();
        togglePanel();
    });

    document.addEventListener("click", () => {
        ensureAudioContext();
    }, { once: true });

    document.addEventListener("click", (event) => {
        if (!panel.contains(event.target) && !button.contains(event.target)) {
            togglePanel(false);
        }
    });

    fetchNotifications();
    setInterval(fetchNotifications, 5000);
})();
