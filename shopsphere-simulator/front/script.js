const API_URL = "http://127.0.0.1:8001";

const products = [
    {
        name: "Everyday Headphones",
        category: "Electronics",
        price: 1499,
        emoji: "🎧",
        background: "#e7eaf5"
    },
    {
        name: "Classic Sneakers",
        category: "Fashion",
        price: 2199,
        emoji: "👟",
        background: "#f4e9df"
    },
    {
        name: "Minimal Wristwatch",
        category: "Accessories",
        price: 1799,
        emoji: "⌚",
        background: "#e8efe4"
    },
    {
        name: "Travel Backpack",
        category: "Lifestyle",
        price: 1299,
        emoji: "🎒",
        background: "#f3e9d7"
    },
    {
        name: "Smart Speaker",
        category: "Electronics",
        price: 2499,
        emoji: "🔊",
        background: "#eee6f5"
    },
    {
        name: "Coffee Essentials",
        category: "Home & Living",
        price: 899,
        emoji: "☕",
        background: "#f4e7df"
    }
];

let cartCount = 0;

const productGrid = document.getElementById("productGrid");
const outageScreen = document.getElementById("outageScreen");
const storefront = document.getElementById("storefront");
const serviceStatus = document.getElementById("serviceStatus");

function renderProducts(items) {
    productGrid.replaceChildren();

    document.getElementById("productCount").textContent =
        `${items.length} products`;

    document.getElementById("noResults")
        .classList.toggle("hidden", items.length !== 0);

    for (const product of items) {
        const card = document.createElement("article");
        card.className = "product-card";

        const art = document.createElement("div");
        art.className = "product-art";
        art.style.backgroundColor = product.background;
        art.textContent = product.emoji;

        const info = document.createElement("div");
        info.className = "product-info";

        const category = document.createElement("div");
        category.className = "product-category";
        category.textContent = product.category;

        const name = document.createElement("h3");
        name.textContent = product.name;

        const bottom = document.createElement("div");
        bottom.className = "product-bottom";

        const price = document.createElement("span");
        price.className = "product-price";
        price.textContent =
            `₹${product.price.toLocaleString("en-IN")}`;

        const addButton = document.createElement("button");
        addButton.className = "add-button";
        addButton.textContent = "Add to Cart";

        addButton.addEventListener("click", () => {
            cartCount++;
            document.getElementById("cartCount").textContent = cartCount;

            addButton.textContent = "Added ✓";

            setTimeout(() => {
                addButton.textContent = "Add to Cart";
            }, 1000);
        });

        bottom.append(price, addButton);
        info.append(category, name, bottom);
        card.append(art, info);

        productGrid.append(card);
    }
}

function searchProducts() {
    const query = document.getElementById("searchInput")
        .value.trim().toLowerCase();

    const filtered = products.filter(product =>
        `${product.name} ${product.category}`
            .toLowerCase()
            .includes(query)
    );

    renderProducts(filtered);
}

function showHealthyState() {
    outageScreen.classList.add("hidden");
    storefront.classList.remove("hidden");

    serviceStatus.textContent = "● ShopSphere operational";
    serviceStatus.style.color = "#315d3b";
}

function showUnhealthyState(message) {
    outageScreen.classList.remove("hidden");
    storefront.classList.add("hidden");

    document.getElementById("outageMessage").textContent = message;

    serviceStatus.textContent = "● ShopSphere unavailable";
    serviceStatus.style.color = "#b53d2c";
}

async function checkHealth() {
    try {
        const controller = new AbortController();

        const timeout = setTimeout(() => {
            controller.abort();
        }, 2500);

        let response;

        try {
            response = await fetch(`${API_URL}/health`, {
                method: "GET",
                cache: "no-store",
                signal: controller.signal
            });
        } finally {
            clearTimeout(timeout);
        }

        if (!response.ok) {
            throw new Error(`Health check returned HTTP ${response.status}`);
        }

        const data = await response.json();

        if (data.status !== "healthy") {
            throw new Error("ShopSphere reports an unhealthy state");
        }

        showHealthyState();

    } catch (error) {
        showUnhealthyState(
            error.name === "AbortError"
                ? "Health check timed out"
                : "Service unavailable"
        );
    }
}

document.getElementById("searchButton")
    .addEventListener("click", searchProducts);

document.getElementById("searchInput")
    .addEventListener("input", searchProducts);

document.getElementById("retryButton")
    .addEventListener("click", checkHealth);

renderProducts(products);
checkHealth();

// Check the actual backend every three seconds.
setInterval(checkHealth, 3000);