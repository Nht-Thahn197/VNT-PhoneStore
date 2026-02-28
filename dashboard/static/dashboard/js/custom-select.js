(() => {
    const SELECTOR = ".js-custom-select";

    const closeAll = (except = null) => {
        document.querySelectorAll(".custom-select.is-open").forEach((node) => {
            if (node !== except) {
                node.classList.remove("is-open");
                const trigger = node.querySelector(".custom-select__trigger");
                if (trigger) {
                    trigger.setAttribute("aria-expanded", "false");
                }
            }
        });
    };

    const buildCustomSelect = (select) => {
        if (select.dataset.customized === "true") {
            return;
        }
        select.dataset.customized = "true";

        const wrapper = document.createElement("div");
        wrapper.className = "custom-select";

        const trigger = document.createElement("button");
        trigger.type = "button";
        trigger.className = "custom-select__trigger";
        trigger.setAttribute("aria-haspopup", "listbox");
        trigger.setAttribute("aria-expanded", "false");

        const valueSpan = document.createElement("span");
        valueSpan.className = "custom-select__value";

        const iconSpan = document.createElement("span");
        iconSpan.className = "custom-select__icon";
        iconSpan.setAttribute("aria-hidden", "true");

        trigger.appendChild(valueSpan);
        trigger.appendChild(iconSpan);

        const menu = document.createElement("div");
        menu.className = "custom-select__menu";
        menu.setAttribute("role", "listbox");
        menu.tabIndex = -1;

        const options = Array.from(select.options);
        const optionButtons = [];

        options.forEach((option) => {
            if (option.hidden) {
                return;
            }
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "custom-select__option";
            btn.textContent = option.textContent;
            btn.dataset.value = option.value;
            btn.setAttribute("role", "option");
            if (option.disabled) {
                btn.classList.add("is-disabled");
                btn.disabled = true;
            }
            if (option.selected) {
                btn.classList.add("is-selected");
                btn.setAttribute("aria-selected", "true");
            } else {
                btn.setAttribute("aria-selected", "false");
            }
            menu.appendChild(btn);
            optionButtons.push(btn);
        });

        const syncFromSelect = () => {
            const selectedOption = select.options[select.selectedIndex];
            valueSpan.textContent = selectedOption ? selectedOption.textContent : "";
            optionButtons.forEach((btn) => {
                const isSelected = btn.dataset.value === select.value;
                btn.classList.toggle("is-selected", isSelected);
                btn.setAttribute("aria-selected", isSelected ? "true" : "false");
            });
            wrapper.classList.toggle("is-placeholder", !select.value);
        };

        const openMenu = () => {
            closeAll(wrapper);
            wrapper.classList.add("is-open");
            trigger.setAttribute("aria-expanded", "true");
            const selectedButton = menu.querySelector(".custom-select__option.is-selected")
                || menu.querySelector(".custom-select__option:not(.is-disabled)");
            if (selectedButton) {
                selectedButton.focus();
            }
        };

        const closeMenu = () => {
            wrapper.classList.remove("is-open");
            trigger.setAttribute("aria-expanded", "false");
        };

        trigger.addEventListener("click", () => {
            if (wrapper.classList.contains("is-open")) {
                closeMenu();
            } else {
                openMenu();
            }
        });

        trigger.addEventListener("keydown", (event) => {
            if (event.key === "ArrowDown" || event.key === "ArrowUp" || event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                openMenu();
            }
        });

        menu.addEventListener("click", (event) => {
            const target = event.target.closest(".custom-select__option");
            if (!target || target.classList.contains("is-disabled")) {
                return;
            }
            select.value = target.dataset.value;
            select.dispatchEvent(new Event("change", { bubbles: true }));
            syncFromSelect();
            closeMenu();
            trigger.focus();
        });

        menu.addEventListener("keydown", (event) => {
            const enabledOptions = optionButtons.filter((btn) => !btn.disabled);
            if (!enabledOptions.length) {
                return;
            }
            const currentIndex = enabledOptions.indexOf(document.activeElement);

            if (event.key === "ArrowDown") {
                event.preventDefault();
                const nextIndex = currentIndex < enabledOptions.length - 1 ? currentIndex + 1 : 0;
                enabledOptions[nextIndex].focus();
            } else if (event.key === "ArrowUp") {
                event.preventDefault();
                const prevIndex = currentIndex > 0 ? currentIndex - 1 : enabledOptions.length - 1;
                enabledOptions[prevIndex].focus();
            } else if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                document.activeElement.click();
            } else if (event.key === "Escape") {
                event.preventDefault();
                closeMenu();
                trigger.focus();
            }
        });

        document.addEventListener("click", (event) => {
            if (!wrapper.contains(event.target)) {
                closeMenu();
            }
        });

        select.addEventListener("change", syncFromSelect);

        select.classList.add("custom-select__native");
        select.parentNode.insertBefore(wrapper, select);
        wrapper.appendChild(select);
        wrapper.appendChild(trigger);
        wrapper.appendChild(menu);

        syncFromSelect();
    };

    const bindFileInput = (input) => {
        if (input.dataset.fileBound === "true") {
            return;
        }
        input.dataset.fileBound = "true";

        const wrapper = input.closest(".file-field");
        const nameLabel = wrapper ? wrapper.querySelector("[data-file-name]") : null;
        const updateName = () => {
            const fileName = input.files && input.files.length ? input.files[0].name : "Chưa có tệp nào được chọn";
            if (nameLabel) {
                nameLabel.textContent = fileName;
            }
        };
        input.addEventListener("change", updateName);
        updateName();
    };

    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll(SELECTOR).forEach(buildCustomSelect);
        document.querySelectorAll(".js-file-input").forEach(bindFileInput);
    });
})();
