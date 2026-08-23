document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('offers-container');
    const paginationContainer = document.getElementById('pagination-container');
    let offers = [];
    let currentPage = 1;
    const itemsPerPage = 24;
    let filteredOffers = [];

    try {
        const response = await fetch('offerte.json');
        if (response.ok) {
            offers = await response.json();
        }
    } catch (e) {
        console.error("Errore caricamento offerte:", e);
    }

    if (offers.length === 0) {
        container.innerHTML = '<p style="text-align:center; width:100%; color:var(--text-muted);">Nessuna offerta caricata al momento. Torna tra poco!</p>';
        return;
    }

    let originalOffers = offers.slice();

    const renderOffers = (offersToRender) => {
        container.innerHTML = '';
        if (offersToRender.length === 0) {
            const searchInput = document.getElementById('search-input');
            const searchTerm = searchInput ? searchInput.value.trim() : '';
            if (searchTerm) {
                container.innerHTML = `<p style="text-align:center; width:100%; color:var(--text-muted);">Cerco "<b>${searchTerm}</b>" online in tempo reale, attendi...</p>`;
                
                fetch(`/api/search?q=${encodeURIComponent(searchTerm)}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.trovate > 0) {
                            fetch('offerte.json')
                                .then(res => res.json())
                                .then(newOffers => {
                                    originalOffers = newOffers;
                                    applyFilters();
                                });
                        } else {
                            container.innerHTML = '<p style="text-align:center; width:100%; color:var(--text-muted);">Nessuna offerta locale o online corrisponde ai criteri di ricerca.</p>';
                        }
                    })
                    .catch(e => {
                        container.innerHTML = '<p style="text-align:center; width:100%; color:var(--text-muted);">Errore durante la ricerca online.</p>';
                    });
            } else {
                container.innerHTML = '<p style="text-align:center; width:100%; color:var(--text-muted);">Nessuna offerta corrisponde ai criteri di ricerca.</p>';
            }
            return;
        }
        offersToRender.forEach((offer, index) => {
            const card = document.createElement('div');
            card.className = 'offer-card';
            
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.animation = `fadeUp 0.6s ease forwards ${index * 0.1}s`;

            const imgUrl = offer.image || "https://images.unsplash.com/photo-1542838132-92c53300491e?w=600&q=80";

            let formattedPrice = offer.newPrice;
            try {
                let numericPrice = parseFloat(offer.newPrice.toString().replace(',', '.'));
                if (!isNaN(numericPrice)) {
                    formattedPrice = numericPrice.toFixed(2).replace('.', ',');
                }
            } catch(e) {}

            let expirationStyle = "display: none;";
            let expirationText = `Scade: ${offer.expiration}`;
            
            if (offer.expiration && offer.expiration !== "N/D") {
                const expDate = new Date(offer.expiration);
                const today = new Date();
                today.setHours(0,0,0,0);
                
                if (!isNaN(expDate.getTime())) {
                    const diffTime = expDate - today;
                    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                    
                    if (diffDays <= 1 && diffDays >= 0) {
                        expirationStyle = "color: #ef4444; font-weight: bold; font-size: 1rem; animation: pulse 1.5s infinite; text-decoration: none; margin-bottom: 1.5rem; display: block;";
                        const endOfDay = new Date(expDate);
                        endOfDay.setHours(23, 59, 59, 999);
                        expirationText = `<span class="live-countdown" data-expires="${endOfDay.getTime()}">Calcolo...</span>`;
                    } else if (diffDays <= 3 && diffDays > 1) {
                        expirationStyle = "color: #f59e0b; font-weight: bold; font-size: 0.95rem; text-decoration: none; margin-bottom: 1.5rem; display: block;";
                        expirationText = `Scade: ${offer.expiration}`;
                    } else if (diffDays > 3) {
                        expirationStyle = "color: #10b981; font-weight: bold; font-size: 0.95rem; text-decoration: none; margin-bottom: 1.5rem; display: block;";
                        expirationText = `Scade: ${offer.expiration}`;
                    } else {
                        expirationStyle = "color: #6b7280; text-decoration: line-through; font-size: 0.9rem; margin-bottom: 1.5rem; display: block;";
                        expirationText = "Offerta Scaduta";
                    }
                }
            }

            card.innerHTML = `
                <div class="offer-img-wrapper">
                    <img src="${imgUrl}" alt="${offer.title}" class="offer-img">
                </div>
                <div class="offer-content">
                    <div class="store-name">${offer.store}</div>
                    <h3 class="product-title">${offer.title}</h3>
                    <div class="price-container" style="margin-bottom: 0.5rem;">
                        <span class="price-new">${formattedPrice} €</span>
                    </div>
                    <div class="expiration-info" style="${expirationStyle}">${expirationText}</div>
                    <button class="offer-btn donate-trigger" data-link="${offer.link || 'https://t.me/+0mC7roUUmYswZjA0'}">Vedi nel Canale</button>
                </div>
            `;
            
            container.appendChild(card);
        });
    };

    const applyFilters = () => {
        let result = originalOffers.slice();
        
        // 1. Ricerca testo (titolo o negozio)
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            const searchTerm = searchInput.value.toLowerCase();
            if (searchTerm) {
                result = result.filter(o => 
                    (o.title && o.title.toLowerCase().includes(searchTerm)) || 
                    (o.store && o.store.toLowerCase().includes(searchTerm))
                );
            }
        }

        // Helper functions
        const getDays = (dateStr) => {
            if (!dateStr || dateStr === "N/D") return Infinity;
            const expDate = new Date(dateStr);
            if (isNaN(expDate.getTime())) return Infinity;
            const today = new Date();
            today.setHours(0,0,0,0);
            return Math.ceil((expDate - today) / (1000 * 60 * 60 * 24));
        };
        const getPrice = (priceStr) => {
            if (!priceStr) return 99999;
            const p = parseFloat(priceStr.toString().replace(',', '.'));
            return isNaN(p) ? 99999 : p;
        };

        const sortPriceEl = document.getElementById('sort-price');
        const sortDateEl = document.getElementById('sort-date');
        const sortPrice = sortPriceEl ? sortPriceEl.value : '';
        const sortDate = sortDateEl ? sortDateEl.value : '';

        // 2. Ordinamento
        result.sort((a, b) => {
            if (sortPrice === 'asc') {
                return getPrice(a.newPrice) - getPrice(b.newPrice);
            } else if (sortPrice === 'desc') {
                return getPrice(b.newPrice) - getPrice(a.newPrice);
            } else if (sortDate === 'late') {
                const wA = getDays(a.expiration) < 0 ? -Infinity : getDays(a.expiration);
                const wB = getDays(b.expiration) < 0 ? -Infinity : getDays(b.expiration);
                return wB - wA; // decrescente (più tardi prima)
            } else {
                // Default o "soon": scadenza più vicina
                const daysA = getDays(a.expiration);
                const daysB = getDays(b.expiration);
                const wA = daysA < 0 ? Infinity : daysA;
                const wB = daysB < 0 ? Infinity : daysB;
                return wA - wB;
            }
        });

        filteredOffers = result;
        currentPage = 1;
        updateView();
    };

    const updateView = () => {
        const start = (currentPage - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const sliced = filteredOffers.slice(start, end);
        renderOffers(sliced);
        renderPagination();
    };

    const renderPagination = () => {
        if (!paginationContainer) return;
        paginationContainer.innerHTML = '';
        const totalPages = Math.ceil(filteredOffers.length / itemsPerPage);
        
        if (totalPages <= 1) return;

        const scrollUp = () => document.getElementById('offerte').scrollIntoView({ behavior: 'smooth' });

        const prevBtn = document.createElement('button');
        prevBtn.className = 'page-btn';
        prevBtn.innerHTML = '<i class="fa-solid fa-chevron-left"></i> Prec';
        prevBtn.disabled = currentPage === 1;
        prevBtn.onclick = () => {
            if (currentPage > 1) {
                currentPage--;
                updateView();
                scrollUp();
            }
        };
        paginationContainer.appendChild(prevBtn);

        let startPage = Math.max(1, currentPage - 2);
        let endPage = Math.min(totalPages, currentPage + 2);
        
        if (startPage > 1) {
            const btn = document.createElement('button');
            btn.className = 'page-btn';
            btn.innerText = '1';
            btn.onclick = () => { currentPage = 1; updateView(); scrollUp(); };
            paginationContainer.appendChild(btn);
            if (startPage > 2) {
                const dots = document.createElement('span');
                dots.style.color = "var(--text-muted)";
                dots.style.alignSelf = "center";
                dots.innerText = '...';
                paginationContainer.appendChild(dots);
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            const btn = document.createElement('button');
            btn.className = 'page-btn' + (i === currentPage ? ' active' : '');
            btn.innerText = i;
            btn.onclick = () => {
                currentPage = i;
                updateView();
                scrollUp();
            }
            paginationContainer.appendChild(btn);
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                const dots = document.createElement('span');
                dots.style.color = "var(--text-muted)";
                dots.style.alignSelf = "center";
                dots.innerText = '...';
                paginationContainer.appendChild(dots);
            }
            const btn = document.createElement('button');
            btn.className = 'page-btn';
            btn.innerText = totalPages;
            btn.onclick = () => { currentPage = totalPages; updateView(); scrollUp(); };
            paginationContainer.appendChild(btn);
        }

        const nextBtn = document.createElement('button');
        nextBtn.className = 'page-btn';
        nextBtn.innerHTML = 'Succ <i class="fa-solid fa-chevron-right"></i>';
        nextBtn.disabled = currentPage === totalPages;
        nextBtn.onclick = () => {
            if (currentPage < totalPages) {
                currentPage++;
                updateView();
                scrollUp();
            }
        };
        paginationContainer.appendChild(nextBtn);
    };

    const styleSheet = document.createElement("style");
    styleSheet.innerText = `
        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    `;
    document.head.appendChild(styleSheet);

    // Event listeners
    const searchInput = document.getElementById('search-input');
    const sortPrice = document.getElementById('sort-price');
    const sortDate = document.getElementById('sort-date');

    if (searchInput) searchInput.addEventListener('input', applyFilters);
    if (sortPrice) {
        sortPrice.addEventListener('change', () => {
            if (sortDate) sortDate.value = ''; // resetta data
            applyFilters();
        });
    }
    if (sortDate) {
        sortDate.addEventListener('change', () => {
            if (sortPrice) sortPrice.value = ''; // resetta prezzo
            applyFilters();
        });
    }

    applyFilters();

    // Setup live countdown timer
    setInterval(() => {
        document.querySelectorAll('.live-countdown').forEach(el => {
            const expires = parseInt(el.getAttribute('data-expires'), 10);
            const now = new Date().getTime();
            const distance = expires - now;
            
            if (distance < 0) {
                el.innerHTML = "Scaduta";
                el.style.textDecoration = "line-through";
                el.style.color = "#6b7280";
                el.parentElement.style.animation = "none";
                el.parentElement.style.color = "#6b7280";
            } else {
                const hours = Math.floor(distance / (1000 * 60 * 60));
                const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((distance % (1000 * 60)) / 1000);
                
                // Formatta con zero iniziale se < 10
                const h = hours.toString().padStart(2, '0');
                const m = minutes.toString().padStart(2, '0');
                const s = seconds.toString().padStart(2, '0');
                
                el.innerHTML = `🔥 Scade in ${h}h ${m}m ${s}s`;
            }
        });
    }, 1000);

    // Modal Logic
    const modal = document.getElementById('donate-modal');
    const closeModal = document.getElementById('close-modal');
    const continueLink = document.getElementById('continue-link');
    const donateYes = document.getElementById('donate-yes');

    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('donate-trigger')) {
            e.preventDefault();
            const link = e.target.getAttribute('data-link');
            continueLink.href = link;
            modal.classList.add('active');
        }
    });

    const hideModal = () => {
        modal.classList.remove('active');
    };

    if (closeModal) closeModal.addEventListener('click', hideModal);
    if (continueLink) continueLink.addEventListener('click', hideModal);
    
    // Close modal when any donate option is clicked
    document.querySelectorAll('.donate-option').forEach(btn => {
        btn.addEventListener('click', hideModal);
    });
    
    // Dropdown Logic for Mobile/Click
    const dropdownLink = document.querySelector('.dropdown > a');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    if (dropdownLink && dropdownMenu) {
        dropdownLink.addEventListener('click', (e) => {
            e.preventDefault();
            dropdownMenu.classList.toggle('show');
        });
    }

    // Hide when clicking outside
    window.addEventListener('click', (e) => {
        if (!e.target.closest('.dropdown')) {
            if (dropdownMenu) dropdownMenu.classList.remove('show');
        }
        if (e.target === modal) {
            hideModal();
        }
    });

    // Gestione Form Contatti
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = document.getElementById('contact-submit');
            const statusDiv = document.getElementById('contact-status');
            const name = document.getElementById('contact-name').value.trim();
            const message = document.getElementById('contact-message').value.trim();

            if (!message) return;

            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Invio in corso...';
            statusDiv.style.display = 'none';

            try {
                const res = await fetch('/api/contact', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, message })
                });
                
                if (res.ok) {
                    statusDiv.innerHTML = '✅ Messaggio inviato con successo! Grazie per il tuo feedback.';
                    statusDiv.style.color = '#10b981';
                    contactForm.reset();
                } else {
                    statusDiv.innerHTML = '❌ Errore durante l\'invio. Riprova più tardi.';
                    statusDiv.style.color = '#ef4444';
                }
            } catch (err) {
                statusDiv.innerHTML = '❌ Errore di connessione.';
                statusDiv.style.color = '#ef4444';
            }

            statusDiv.style.display = 'block';
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Invia Messaggio <i class="fa-solid fa-paper-plane"></i>';
        });
    }
});

// --- E-COMMERCE LOGIC ---
const shopProducts = [
    { id: 101, name: "Disponibile a Breve", price: 0.00, image: "https://images.unsplash.com/photo-1614332287897-cdc485fa562d?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=60", desc: "Questo spazio è pronto per un tuo nuovo prodotto!" },
    { id: 102, name: "Disponibile a Breve", price: 0.00, image: "https://images.unsplash.com/photo-1614332287897-cdc485fa562d?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=60", desc: "Questo spazio è pronto per un tuo nuovo prodotto!" },
    { id: 103, name: "Disponibile a Breve", price: 0.00, image: "https://images.unsplash.com/photo-1614332287897-cdc485fa562d?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=60", desc: "Questo spazio è pronto per un tuo nuovo prodotto!" }
];

let cart = [];

function renderShop() {
    const container = document.getElementById('products-container');
    if(!container) return;
    
    container.innerHTML = shopProducts.map(p => `
        <div class="offer-card glass-card" style="min-width: 280px; flex: 0 0 auto; cursor: pointer; transition: transform 0.3s;" onclick="openProduct(${p.id})" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            <div class="offer-image" style="background-image: url('${p.image}')"></div>
            <div class="offer-details">
                <h3 class="offer-title">${p.name}</h3>
                <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem;">${p.desc}</p>
                <div class="offer-meta" style="justify-content: flex-end;">
                    <span class="offer-price" style="font-size: 1.3rem;">€${p.price.toFixed(2)}</span>
                </div>
            </div>
        </div>
    `).join('');
}

function updateCartUI() {
    const badge = document.getElementById('cart-badge');
    const itemsContainer = document.getElementById('cart-items');
    const totalEl = document.getElementById('cart-total');
    const btn = document.getElementById('btn-checkout');
    const emptyMsg = document.getElementById('empty-cart-msg');
    const paymentMethods = document.getElementById('payment-methods');
    
    const count = cart.reduce((sum, item) => sum + item.qty, 0);
    const total = cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
    
    if(count > 0) {
        badge.style.display = 'block';
        badge.textContent = count;
        btn.style.display = 'block';
        emptyMsg.style.display = 'none';
        
        itemsContainer.innerHTML = cart.map((item, idx) => `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <div>
                    <div style="font-weight: 600;">${item.name}</div>
                    <div style="font-size: 0.8rem; color: var(--text-muted);">€${item.price.toFixed(2)} x ${item.qty}</div>
                </div>
                <div>
                    <span style="font-weight: 800; margin-right: 1rem;">€${(item.price * item.qty).toFixed(2)}</span>
                    <button onclick="removeFromCart(${idx})" style="background: none; border: none; color: #ef4444; cursor: pointer;"><i class="fa-solid fa-trash"></i></button>
                </div>
            </div>
        `).join('');
    } else {
        badge.style.display = 'none';
        btn.style.display = 'none';
        emptyMsg.style.display = 'block';
        if(paymentMethods) paymentMethods.style.display = 'none';
        itemsContainer.innerHTML = '';
    }
    
    totalEl.textContent = '€' + total.toFixed(2);
}

window.addToCart = function(id, fromModal = false) {
    const product = shopProducts.find(p => p.id === id);
    const existing = cart.find(i => i.id === id);
    
    let qtyToAdd = 1;
    if (fromModal) {
        const qtyInput = document.getElementById('product-modal-qty');
        qtyToAdd = qtyInput ? parseInt(qtyInput.value) : 1;
    } else {
        const qtyInput = document.getElementById('qty-' + id);
        if (qtyInput) qtyToAdd = parseInt(qtyInput.value);
    }
    
    if(existing) {
        existing.qty += qtyToAdd;
    } else {
        cart.push({...product, qty: qtyToAdd});
    }
    updateCartUI();
    
    if (fromModal) {
        document.getElementById('product-modal').classList.remove('active');
        document.getElementById('cart-modal').classList.add('active');
    }
}

window.openProduct = function(id) {
    const product = shopProducts.find(p => p.id === id);
    if(!product) return;
    
    document.getElementById('product-modal-img').style.backgroundImage = `url('${product.image}')`;
    document.getElementById('product-modal-title').textContent = product.name;
    document.getElementById('product-modal-desc').textContent = product.desc;
    document.getElementById('product-modal-price').textContent = `€${product.price.toFixed(2)}`;
    
    // Acquisti bloccati
    // document.getElementById('product-modal-qty').value = 1;
    // const addBtn = document.getElementById('product-modal-add');
    // addBtn.onclick = () => addToCart(product.id, true);
    
    document.getElementById('product-modal').classList.add('active');
}

window.removeFromCart = function(idx) {
    cart.splice(idx, 1);
    updateCartUI();
}

document.addEventListener('DOMContentLoaded', () => {
    renderShop();
    
    // --- CAROUSEL LOGIC ---
    const container = document.getElementById('products-container');
    const btnPrev = document.getElementById('carousel-prev');
    const btnNext = document.getElementById('carousel-next');
    
    if(container && btnPrev && btnNext) {
        const scrollAmount = 300;
        let autoScrollTimer = setInterval(() => scrollNext(), 2000);
        
        function scrollNext() {
            if(container.scrollLeft + container.clientWidth >= container.scrollWidth - 10) {
                container.scrollTo({left: 0, behavior: 'smooth'}); // loop back to start
            } else {
                container.scrollBy({left: scrollAmount, behavior: 'smooth'});
            }
        }
        
        function scrollPrev() {
            if(container.scrollLeft <= 0) {
                container.scrollTo({left: container.scrollWidth, behavior: 'smooth'});
            } else {
                container.scrollBy({left: -scrollAmount, behavior: 'smooth'});
            }
        }

        btnNext.addEventListener('click', () => {
            clearInterval(autoScrollTimer);
            scrollNext();
            autoScrollTimer = setInterval(() => scrollNext(), 2000);
        });
        
        btnPrev.addEventListener('click', () => {
            clearInterval(autoScrollTimer);
            scrollPrev();
            autoScrollTimer = setInterval(() => scrollNext(), 2000);
        });
        
        // Pause on hover
        container.addEventListener('mouseenter', () => clearInterval(autoScrollTimer));
        container.addEventListener('mouseleave', () => {
            autoScrollTimer = setInterval(() => scrollNext(), 2000);
        });
    }
    
    const productModal = document.getElementById('product-modal');
    const closeProduct = document.getElementById('close-product');
    if(closeProduct) {
        closeProduct.addEventListener('click', () => {
            productModal.classList.remove('active');
        });
    }
    
    const cartIcon = document.getElementById('cart-icon');
    const cartModal = document.getElementById('cart-modal');
    const closeCart = document.getElementById('close-cart');
    const btnCheckout = document.getElementById('btn-checkout');
    
    if(cartIcon) {
        cartIcon.addEventListener('click', (e) => {
            e.preventDefault();
            cartModal.classList.add('active');
        });
    }
    
    if(closeCart) {
        closeCart.addEventListener('click', () => {
            cartModal.classList.remove('active');
        });
    }
    
    if(btnCheckout) {
        btnCheckout.addEventListener('click', (e) => {
            e.preventDefault();
            const paymentMethods = document.getElementById('payment-methods');
            if(paymentMethods) {
                paymentMethods.style.display = 'block';
                btnCheckout.style.display = 'none';
            }
        });
    }


});

// --- Caricamento Live Coupons Indipendente ---
document.addEventListener('DOMContentLoaded', () => {
    const couponContainer = document.getElementById('coupons-container');
    if(!couponContainer) return;

    fetch('coupon_live.json')
        .then(response => response.json())
        .then(data => {
            if(!data || data.length === 0) {
                couponContainer.innerHTML = '<p style="color:var(--text-muted); width:100%; text-align:center;">Nessun coupon trovato al momento.</p>';
                return;
            }
            couponContainer.innerHTML = '';
            
            function getLogoHtml(channelName) {
                const ch = channelName.toLowerCase();
                let domain = 'google.com';
                if (ch.includes('esselunga')) domain = 'esselunga.it';
                else if (ch.includes('carrefour')) domain = 'carrefour.it';
                else if (ch.includes('glovo')) domain = 'glovoapp.com';
                else if (ch.includes('conad')) domain = 'conad.it';
                else if (ch.includes('satispay')) domain = 'satispay.com';
                else if (ch.includes('amazon')) domain = 'amazon.it';
                else if (ch.includes('ebay')) domain = 'ebay.it';
                else if (ch.includes('shein')) domain = 'shein.com';
                else if (ch.includes('discoup')) domain = 'discoup.com';
                
                return `<img src="https://logo.clearbit.com/${domain}" style="width:50px; height:50px; object-fit:contain; border-radius:50%; border: 1px solid #d3d3d3; padding:2px; background:white;">`;
            }

            data.forEach(coupon => {
                const card = document.createElement('div');
                card.style.minWidth = '260px';
                card.style.maxWidth = '260px';
                card.style.backgroundColor = '#ffffff';
                card.style.borderRadius = '12px';
                card.style.padding = '1.5rem';
                card.style.boxShadow = '0 4px 15px rgba(0,0,0,0.1)';
                card.style.position = 'relative';
                card.style.display = 'flex';
                card.style.flexDirection = 'column';
                card.style.justifyContent = 'space-between';
                card.style.border = '1px solid #eaeaea';
                
                if (coupon.badge && coupon.badge.includes('SPONSORIZZATO')) {
                    card.style.border = '2px solid #f59e0b';
                    card.style.boxShadow = '0 4px 20px rgba(245, 158, 11, 0.2)';
                }
                
                const badgeColor = coupon.badge && coupon.badge.includes('SPONSORIZZATO') ? '#f59e0b' : '#ec891f';
                const badgeHtml = coupon.badge ? `<div style="display: inline-block; background: ${badgeColor}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; margin-bottom: 5px; text-transform: uppercase;">${coupon.badge}</div>` : '';
                
                // Pulsante stile TopNegozi: "Preleva codice"
                const actionBtn = `<div style="position: relative; width: 100%; border-radius: 8px; overflow: hidden; border: 1px solid #ec891f; cursor: pointer;" onclick="navigator.clipboard.writeText('${coupon.codice}'); ${coupon.link ? `window.open('${coupon.link}', '_blank');` : ''} alert('✅ Codice copiato! ${coupon.link ? "Ti sto reindirizzando al sito dell'offerta..." : ""}');">
                    <button style="width: 70%; background: #ec891f; border: none; color: white; padding: 12px; font-weight: bold; font-size: 1rem; text-transform: uppercase; float: left; pointer-events: none;">Preleva codice</button>
                    <div style="width: 30%; float: left; background: #fff; color: #ec891f; font-weight: bold; text-align: center; padding: 12px 0; font-size: 1rem; border-left: 1px dashed #ec891f;">${coupon.codice.substring(0,3)}***</div>
                    <div style="clear: both;"></div>
                </div>`;

                card.innerHTML = `
                    <div style="display: flex; align-items: flex-start; margin-bottom: 15px;">
                        <div style="flex-shrink: 0; margin-right: 15px;">
                            ${getLogoHtml(coupon.canale)}
                        </div>
                        <div style="flex-grow: 1;">
                            ${badgeHtml}
                            <div style="font-size: 1.1rem; font-weight: 800; color: #0f172a; line-height: 1.3;">
                                ${coupon.canale} - <span style="color: ${badgeColor};">${coupon.codice}</span>
                            </div>
                        </div>
                    </div>
                    
                    <p style="font-size: 0.9rem; color: #475569; line-height: 1.5; margin-bottom: 15px; flex-grow: 1;">${coupon.testo_originale}</p>
                    
                    <div style="margin-top: auto;">
                        ${actionBtn}
                    </div>
                `;
                couponContainer.appendChild(card);
            });
        })
        .catch(err => {
            console.error('Errore caricamento coupon:', err);
            couponContainer.innerHTML = '<p style="color:var(--text-muted); width:100%; text-align:center;">Nessun coupon attivo. Attendi la prossima scansione del bot!</p>';
        });
});
