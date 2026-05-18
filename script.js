document.addEventListener('DOMContentLoaded', () => {
    // Combina os produtos originais com os do Bob's Watches
    if (window.bobsWatches) {
        window.watches = [...window.watches, ...window.bobsWatches];
    }

    const productsContainer = document.getElementById('products-container');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const cartCountEl = document.querySelector('.cart-count');
    const modal = document.getElementById('watch-modal');
    const modalBody = document.getElementById('modal-body-content');
    const closeModal = document.querySelector('.close-modal');

    let cart = JSON.parse(localStorage.getItem('primeCart')) || [];
    let cartCount = cart.reduce((acc, item) => acc + item.quantity, 0);
    if(cartCountEl) cartCountEl.textContent = cartCount;
    // Render Products
    function renderProducts(filter = 'all') {
        productsContainer.innerHTML = '';
        
        const filteredWatches = filter === 'all' 
            ? window.watches 
            : window.watches.filter(w => {
                const b = (w.brand || '').toLowerCase();
                const m = (w.model || '').toLowerCase();
                const f = filter.toLowerCase();
                return b === f || m.includes(f);
            });

        filteredWatches.forEach((watch, index) => {
            const card = document.createElement('div');
            card.className = 'product-card';
            card.style.animationDelay = `${index * 0.1}s`;
            
            // Use the first image in the array
            const mainImage = watch.images && watch.images.length > 0 ? watch.images[0] : 'https://via.placeholder.com/400x400?text=Relogio+Premium';
            
            card.innerHTML = `
                <div class="product-image">
                    <img src="${mainImage}" alt="${watch.model}" loading="lazy" onerror="this.src='https://via.placeholder.com/400x400?text=Relogio+Premium'">
                </div>
                <div class="product-info">
                    <span class="product-brand">${watch.brand}</span>
                    <h3 class="product-title" style="text-transform: capitalize;">${(watch.model||'').toLowerCase()}</h3>
                    <div class="product-price">
                        <span>${watch.price}</span>
                    </div>
                    <div class="product-actions">
                        <button class="btn btn-primary buy-btn" data-index="${window.watches.indexOf(watch)}">COMPRAR</button>
                        <button class="btn btn-secondary details-btn" data-index="${window.watches.indexOf(watch)}">DETALLES</button>
                    </div>
                </div>
            `;
            
            productsContainer.appendChild(card);
        });

        // Re-attach event listeners
        attachCardListeners();
    }

    function attachCardListeners() {
        // Buy Button
        document.querySelectorAll('.buy-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = e.target.getAttribute('data-index');
                const watch = window.watches[index];
                addToCart(watch);
                
                btn.textContent = '¡Añadido!';
                btn.style.backgroundColor = '#00A36C';
                setTimeout(() => {
                    btn.textContent = 'COMPRAR';
                    btn.style.backgroundColor = '';
                }, 1000);
            });
        });

        // Details Button
        document.querySelectorAll('.details-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = e.target.getAttribute('data-index');
                const watch = window.watches[index];
                showModal(watch);
            });
        });
    }

    // Modal Functionality with Carousel/Thumbnails
    function showModal(watch) {
        let specsHtml = '';
        for (const [key, value] of Object.entries(watch.specifications)) {
            const kl = key.toLowerCase();
            if (kl.includes('condition') || kl.includes('movement') || kl.includes('gender') || kl.includes('box')) continue;
            
            let translatedKey = key;
            if (kl.includes('dial')) translatedKey = 'Esfera';
            if (kl.includes('case')) translatedKey = 'Caja';
            if (kl.includes('bracelet')) translatedKey = 'Brazalete';
            if (kl.includes('year')) translatedKey = 'Año';
            if (kl.includes('reference')) translatedKey = 'Referencia';
            
            specsHtml += `<li style="padding: 8px 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between;"><strong>${translatedKey}:</strong> <span style="text-align: right; max-width: 60%;">${value}</span></li>`;
        }

        // Generate Thumbnails HTML
        let thumbnailsHtml = '';
        if (watch.images && watch.images.length > 1) {
            thumbnailsHtml = '<div class="modal-thumbnails">';
            watch.images.forEach((img, idx) => {
                thumbnailsHtml += `<img src="${img}" class="thumb-img ${idx === 0 ? 'active' : ''}" data-index="${idx}" onerror="this.src='https://via.placeholder.com/100x100?text=Relogio'">`;
            });
            thumbnailsHtml += '</div>';
        }

        const mainImage = watch.images && watch.images.length > 0 ? watch.images[0] : 'https://via.placeholder.com/400x400?text=Relogio+Premium';

        modalBody.innerHTML = `
            <div class="modal-gallery">
                <div class="modal-main-image">
                    <img id="modal-img-display" src="${mainImage}" alt="${watch.model}" onerror="this.src='https://via.placeholder.com/400x400?text=Relogio+Premium'">
                </div>
                ${thumbnailsHtml}
            </div>
            <div class="modal-info">
                <span class="product-brand" style="color: var(--primary); font-weight: bold; letter-spacing: 2px; text-transform: uppercase;">${watch.brand}</span>
                <h2 style="font-family: var(--font-body); font-weight: 600; font-size: 1.4rem; line-height: 1.4; margin-top: 5px; margin-bottom: 15px; color: var(--black); text-transform: capitalize;">${(watch.model||'').toLowerCase()}</h2>
                <h3 style="color: var(--black); font-weight: bold; font-size: 1.8rem; margin-bottom: 20px;">${watch.price}</h3>
                <h4 style="margin-bottom: 10px; color: var(--black);">Especificaciones:</h4>
                <ul style="list-style: none; margin-bottom: 30px; color: var(--text-muted); font-size: 0.95rem; padding: 0;">
                    <li style="padding: 8px 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between;"><strong>Calidad:</strong> <span>AAA</span></li>
                    <li style="padding: 8px 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between;"><strong>Estado:</strong> <span>Nuevo</span></li>
                    <li style="padding: 8px 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between;"><strong>¿Con caja?:</strong> <span>Sí</span></li>
                    <li style="padding: 8px 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between;"><strong>Movimiento:</strong> <span>Automático</span></li>
                    ${specsHtml}
                </ul>
                <button class="btn btn-primary modal-buy-btn">Añadir al Carrito</button>
            </div>
        `;

        modal.style.display = 'block';

        // Add Thumbnail Click Listeners
        const thumbs = document.querySelectorAll('.thumb-img');
        const mainImgDisplay = document.getElementById('modal-img-display');
        
        thumbs.forEach(thumb => {
            thumb.addEventListener('click', (e) => {
                const idx = e.target.getAttribute('data-index');
                mainImgDisplay.src = watch.images[idx];
                
                // Update active class
                thumbs.forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');
            });
        });

        // Modal Buy Button
        const modalBuyBtn = document.querySelector('.modal-buy-btn');
        // Remove old listeners to prevent multiple additions if modal is opened multiple times
        const newModalBuyBtn = modalBuyBtn.cloneNode(true);
        modalBuyBtn.parentNode.replaceChild(newModalBuyBtn, modalBuyBtn);
        
        newModalBuyBtn.addEventListener('click', () => {
            addToCart(watch);
            modal.style.display = 'none';
        });
    }

    // Close Modals
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Find the closest modal and close it
            const parentModal = e.target.closest('.modal');
            if (parentModal) parentModal.style.display = 'none';
        });
    });

    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });

    // Render Filter Buttons in Modal
    function renderFilters() {
        const popupList = document.getElementById('category-popup-list');
        if (!popupList) return;
        
        // Lista exata de marcas solicitada
        const brands = [
            "Rolex", "OMEGA", "Breitling", "Patek Philippe",
            "Audemars Piguet", "Panerai", "Tissot"
        ];
        
        // Criar os botões
        let buttonsHtml = `<button class="filter-btn active" data-filter="all" style="width:100%; border-radius: 8px;">Todos</button>`;
        brands.forEach(brand => {
            buttonsHtml += `<button class="filter-btn" data-filter="${brand}" style="width:100%; border-radius: 8px;">${brand}</button>`;
        });
        
        popupList.innerHTML = buttonsHtml;
        
        // Atachar eventos aos botões
        const filterButtons = popupList.querySelectorAll('.filter-btn');
        const currentCategoryTitle = document.getElementById('current-category-title');
        const categoryModal = document.getElementById('category-modal');
        
        filterButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                filterButtons.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                
                const filter = e.target.getAttribute('data-filter');
                if(currentCategoryTitle) {
                    currentCategoryTitle.textContent = filter === 'all' ? 'Todos os Relógios' : filter;
                }
                
                renderProducts(filter);
                
                // Fechar modal ao escolher
                categoryModal.style.display = 'none';
            });
        });
    }

    // Modal de Categoria Logic
    const openCategoryBtn = document.getElementById('open-category-modal');
    const categoryModal = document.getElementById('category-modal');
    const closeCategoryBtn = document.querySelector('.close-category-modal');

    if(openCategoryBtn) {
        openCategoryBtn.addEventListener('click', () => {
            categoryModal.style.display = 'block';
        });
    }

    if(closeCategoryBtn) {
        closeCategoryBtn.addEventListener('click', () => {
            categoryModal.style.display = 'none';
        });
    }

    // Close Modals on Outside Click
    window.addEventListener('click', (e) => {
        const watchModal = document.getElementById('watch-modal');
        if (e.target === categoryModal) categoryModal.style.display = 'none';
        if (e.target === watchModal) watchModal.style.display = 'none';
    });

    // Initial Render
    renderFilters();
    renderProducts();
    // --- CART DRAWER LOGIC ---
    const cartDrawer = document.getElementById('cart-drawer');
    const cartOverlay = document.getElementById('cart-overlay');
    const cartBtn = document.getElementById('cart-btn');
    const closeCartBtn = document.getElementById('close-cart-btn');
    const cartItemsContainer = document.getElementById('cart-items-container');
    const cartTotalPrice = document.getElementById('cart-total-price');
    const checkoutBtn = document.getElementById('checkout-btn');

    // Save cart to local storage
    function saveCart() {
        localStorage.setItem('primeCart', JSON.stringify(cart));
    }

    // Make functions globally available if needed
    window.addToCart = function(watch) {
        // Check if watch already exists in cart
        const existingItemIndex = cart.findIndex(item => item.model === watch.model && item.brand === watch.brand);
        
        if (existingItemIndex > -1) {
            cart[existingItemIndex].quantity += 1;
        } else {
            // Store a deep copy so we can modify quantity
            cart.push({ ...watch, quantity: 1 });
        }
        
        cartCount = cart.reduce((acc, item) => acc + item.quantity, 0);
        cartCountEl.textContent = cartCount;
        
        saveCart();
        
        // Pulse animation on the icon
        cartCountEl.style.transform = 'scale(1.3)';
        setTimeout(() => cartCountEl.style.transform = 'scale(1)', 200);
        
        updateCartUI();
        openCart(); // Auto open cart when adding (iFood style)
    };

    window.updateQuantity = function(index, delta) {
        if (!cart[index]) return;
        
        cart[index].quantity += delta;
        if (cart[index].quantity <= 0) {
            cart.splice(index, 1);
        }
        
        cartCount = cart.reduce((acc, item) => acc + item.quantity, 0);
        cartCountEl.textContent = cartCount;
        
        saveCart();
        updateCartUI();
    };

    window.removeFromCart = function(index) {
        cart.splice(index, 1);
        cartCount = cart.reduce((acc, item) => acc + item.quantity, 0);
        cartCountEl.textContent = cartCount;
        
        saveCart();
        updateCartUI();
    };

    function parsePrice(priceStr) {
        if (!priceStr) return 0;
        let clean = priceStr.replace('R$', '').trim();
        clean = clean.replace(/\./g, '');
        clean = clean.replace(',', '.');
        return parseFloat(clean) || 0;
    }

    function formatPrice(num) {
        return 'R$ ' + num.toFixed(2).replace('.', ',').replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    }

    function updateCartUI() {
        if (!cartDrawer) return;
        
        if (cart.length === 0) {
            cartItemsContainer.innerHTML = '<div class="empty-cart-msg">Su carrito está vacío.</div>';
            cartTotalPrice.textContent = 'R$ 0,00';
            checkoutBtn.style.opacity = '0.5';
            checkoutBtn.style.pointerEvents = 'none';
            return;
        }

        let html = '';
        let total = 0;

        cart.forEach((item, index) => {
            const mainImg = item.images && item.images.length > 0 ? item.images[0] : 'https://via.placeholder.com/100x100';
            const price = parsePrice(item.price);
            total += price * item.quantity;

            html += `
                <div class="cart-item">
                    <img src="${mainImg}" class="cart-item-img" alt="${item.model}" loading="lazy">
                    <div class="cart-item-info">
                        <span class="cart-item-brand">${item.brand}</span>
                        <div class="cart-item-title">${(item.model||'').toLowerCase()}</div>
                        <div class="cart-item-price-row">
                            <span class="cart-item-price">${item.price}</span>
                            <div class="cart-item-controls">
                                <button class="cart-qty-btn" onclick="updateQuantity(${index}, -1)">-</button>
                                <span class="cart-qty">${item.quantity}</span>
                                <button class="cart-qty-btn" onclick="updateQuantity(${index}, 1)">+</button>
                            </div>
                        </div>
                    </div>
                    <button class="remove-item-btn" onclick="removeFromCart(${index})" style="position: absolute; top: 10px; right: 10px;">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
        });

        cartItemsContainer.innerHTML = html;
        cartTotalPrice.textContent = formatPrice(total);
        checkoutBtn.style.opacity = '1';
        checkoutBtn.style.pointerEvents = 'auto';
    }

    function openCart() {
        if (cartDrawer) {
            cartDrawer.classList.add('active');
            cartOverlay.classList.add('active');
        }
    }

    function closeCart() {
        if (cartDrawer) {
            cartDrawer.classList.remove('active');
            cartOverlay.classList.remove('active');
        }
    }

    if (cartBtn) cartBtn.addEventListener('click', openCart);
    if (closeCartBtn) closeCartBtn.addEventListener('click', closeCart);
    if (cartOverlay) cartOverlay.addEventListener('click', closeCart);

    // WhatsApp Checkout
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', () => {
            if (cart.length === 0) return;
            
            let message = "*NUEVO PEDIDO - FABRICANTE PRIME RELOJES*\n\n";
            message += "Hola! Me gustaría finalizar la compra de los siguientes relojes:\n\n";
            
            cart.forEach((item, i) => {
                let model = (item.model||'').toLowerCase();
                model = model.replace(/\b\w/g, l => l.toUpperCase());
                
                message += `*ITEM ${i+1}*\n`;
                message += `*Marca:* ${item.brand}\n`;
                message += `*Modelo:* ${model}\n`;
                message += `*Cantidad:* ${item.quantity}x\n`;
                message += `*Precio Unitario:* ${item.price}\n`;
                message += `\n`;
            });
            
            message += `━━━━━━━━━━━━━━━━━━━━━\n`;
            message += `*TOTAL DEL PEDIDO:* ${cartTotalPrice.textContent}\n`;
            message += `━━━━━━━━━━━━━━━━━━━━━\n\n`;
            message += `Aguardando instrucciones para el pago y envío.`;
            
            const phone = window.whatsappPhone || "554791028539"; 
            const encodedMessage = encodeURIComponent(message);
            window.open(`https://wa.me/${phone}?text=${encodedMessage}`, '_blank');
        });
    }

    // Initialize cart UI on load
    updateCartUI();
});
