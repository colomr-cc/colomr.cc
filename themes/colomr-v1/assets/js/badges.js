document.addEventListener('DOMContentLoaded', function() {
    const PAGE_SIZE = 20;
    const filterBtns = document.querySelectorAll('.filter-btn');
    const allCards = Array.from(document.querySelectorAll('.badge-card-full'));
    const prevBtn = document.querySelector('.page-prev');
    const nextBtn = document.querySelector('.page-next');
    const pageNumbers = document.querySelector('.page-numbers');
    const pageInfo = document.querySelector('.badges-page-info');

    let currentFilter = 'all';
    let currentPage = 1;

    function getVisibleCards() {
        return allCards.filter(card =>
            currentFilter === 'all' || card.getAttribute('data-category') === currentFilter
        );
    }

    function renderPage() {
        const visible = getVisibleCards();
        const totalPages = Math.ceil(visible.length / PAGE_SIZE);
        const start = (currentPage - 1) * PAGE_SIZE;
        const end = start + PAGE_SIZE;

        allCards.forEach(card => card.style.display = 'none');
        visible.slice(start, end).forEach(card => {
            card.style.display = 'block';
            card.style.animation = 'fadeIn 0.3s ease';
        });

        prevBtn.disabled = currentPage === 1;
        nextBtn.disabled = currentPage === totalPages || totalPages === 0;

        // Números de página
        pageNumbers.innerHTML = '';
        const maxButtons = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxButtons / 2));
        let endPage = Math.min(totalPages, startPage + maxButtons - 1);
        if (endPage - startPage < maxButtons - 1) {
            startPage = Math.max(1, endPage - maxButtons + 1);
        }

        for (let i = startPage; i <= endPage; i++) {
            const btn = document.createElement('button');
            btn.className = 'page-btn page-number' + (i === currentPage ? ' active' : '');
            btn.textContent = i;
            btn.addEventListener('click', () => { currentPage = i; renderPage(); scrollToGrid(); });
            pageNumbers.appendChild(btn);
        }

        // Info de resultados
        const from = visible.length ? start + 1 : 0;
        const to = Math.min(end, visible.length);
        pageInfo.textContent = `Mostrando ${from}\u2013${to} de ${visible.length} badges`;

        // Ocultar paginación si cabe en una página
        const paginationEl = document.querySelector('.badges-pagination');
        paginationEl.style.display = totalPages <= 1 ? 'none' : 'flex';
        pageInfo.style.display = totalPages <= 1 ? 'none' : 'block';
    }

    function scrollToGrid() {
        document.querySelector('.badges-grid').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            currentFilter = this.getAttribute('data-filter');
            currentPage = 1;
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            renderPage();
        });
    });

    prevBtn.addEventListener('click', () => { currentPage--; renderPage(); scrollToGrid(); });
    nextBtn.addEventListener('click', () => { currentPage++; renderPage(); scrollToGrid(); });

    renderPage();

    // Scroll to top button
    const scrollBtn = document.querySelector('.scroll-top-btn');
    window.addEventListener('scroll', function() {
        scrollBtn.classList.toggle('visible', window.scrollY > 600);
    });
    scrollBtn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});
