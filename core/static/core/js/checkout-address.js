(() => {
    const citySelect = document.getElementById("city");
    const wardSelect = document.getElementById("ward");

    if (!citySelect || !wardSelect) {
        return;
    }

    const API_V2 = "https://provinces.open-api.vn/api/v2/";
    const API_V1 = "https://provinces.open-api.vn/api/?depth=3";

    const normalizeName = (value) => (value || "").toString().trim();
    const getCode = (item) => {
        if (!item) return "";
        return (item.code ?? item.id ?? item.code_name ?? item.codename ?? item.code_id ?? "").toString();
    };
    const getName = (item) => {
        if (!item) return "";
        return normalizeName(item.name ?? item.full_name ?? item.name_with_type ?? item.title ?? item.label ?? "");
    };

    const setOptions = (select, options, placeholder, disabled = false) => {
        select.innerHTML = "";
        const placeholderOption = document.createElement("option");
        placeholderOption.value = "";
        placeholderOption.textContent = placeholder;
        placeholderOption.disabled = true;
        placeholderOption.selected = true;
        select.appendChild(placeholderOption);

        options.forEach((option) => {
            const opt = document.createElement("option");
            opt.value = option.code;
            opt.textContent = option.name;
            select.appendChild(opt);
        });

        select.disabled = disabled;
        if (window.CustomSelect?.refresh) {
            window.CustomSelect.refresh(select);
        }
    };

    const extractWards = (province) => {
        if (!province || typeof province !== "object") {
            return [];
        }
        const directKeys = ["wards", "ward", "phuong_xa", "xa_phuong", "communes", "commune"];
        for (const key of directKeys) {
            if (Array.isArray(province[key])) {
                return province[key];
            }
        }
        if (Array.isArray(province.districts)) {
            const wards = [];
            province.districts.forEach((district) => {
                for (const key of directKeys) {
                    if (Array.isArray(district[key])) {
                        wards.push(...district[key]);
                        return;
                    }
                }
                if (Array.isArray(district.wards)) {
                    wards.push(...district.wards);
                }
            });
            return wards;
        }
        return [];
    };

    const parseProvinceData = (data) => {
        if (!Array.isArray(data)) {
            return { provinces: [], wardMap: new Map() };
        }
        const provinces = [];
        const wardMap = new Map();

        data.forEach((province) => {
            const code = getCode(province);
            const name = getName(province);
            if (!code || !name) {
                return;
            }
            provinces.push({ code, name });
            const wardsRaw = extractWards(province);
            const wards = wardsRaw
                .map((ward) => ({ code: getCode(ward), name: getName(ward) }))
                .filter((ward) => ward.code && ward.name)
                .sort((a, b) => a.name.localeCompare(b.name, "vi"));
            wardMap.set(code, wards);
        });

        provinces.sort((a, b) => a.name.localeCompare(b.name, "vi"));
        return { provinces, wardMap };
    };

    const loadFromApi = async (url) => {
        const response = await fetch(url, { mode: "cors" });
        if (!response.ok) {
            throw new Error("Failed to fetch location data.");
        }
        return response.json();
    };

    const hydrate = ({ provinces, wardMap }) => {
        setOptions(citySelect, provinces, "Chọn Tỉnh / Thành phố", false);
        setOptions(wardSelect, [], "Chọn Phường / Xã", true);

        citySelect.addEventListener("change", () => {
            const wards = wardMap.get(citySelect.value) || [];
            setOptions(wardSelect, wards, "Chọn Phường / Xã", wards.length === 0);
        });
    };

    const init = async () => {
        setOptions(citySelect, [], "Đang tải danh sách...", true);
        setOptions(wardSelect, [], "Chọn Tỉnh/Thành trước", true);

        try {
            const data = await loadFromApi(`${API_V2}?depth=2`);
            hydrate(parseProvinceData(data));
        } catch (error) {
            try {
                const data = await loadFromApi(API_V1);
                hydrate(parseProvinceData(data));
            } catch (fallbackError) {
                setOptions(citySelect, [], "Không tải được danh sách", true);
                setOptions(wardSelect, [], "Không tải được danh sách", true);
            }
        }
    };

    init();
})();
