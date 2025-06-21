document.addEventListener('DOMContentLoaded', () => {
    const searchInput    = document.getElementById('search-input');
    const categorySelect = document.getElementById('category-select');
    const cards          = Array.from(document.querySelectorAll('#events-container .card'));
  
    function filterCards() {
      const term = searchInput.value.trim().toLowerCase();
      const cat  = categorySelect.value;
  
      cards.forEach(card => {
        const title    = card.dataset.title.toLowerCase();
        const category = card.dataset.category;
        const matchText= title.includes(term);
        const matchCat = !cat || cat === category;
        card.style.display = (matchText && matchCat) ? 'flex' : 'none';
      });
    }
  
    searchInput.addEventListener('input', filterCards);
    categorySelect.addEventListener('change', filterCards);
  });

document.addEventListener('DOMContentLoaded', () => {
  const eventsContainer = document.getElementById('events-container');
  const searchInput = document.getElementById('search-input');
  const categorySelect = document.getElementById('category-select');

  let allEvents = [];  // сюда загрузим данные с API


  async function loadEvents() {
    try {
      const response = await fetch(`/admin/events/json?user_id=${userId}`);
      const data = await response.json();
      allEvents = data.events || [];
      renderEvents();
    } catch (err) {
      console.error("Ошибка загрузки событий:", err);
      eventsContainer.innerHTML = '<p class="col-span-full text-center text-red-500">Ошибка загрузки.</p>';
    }
  }

  function renderEvents() {
    const term = searchInput.value.trim().toLowerCase();
    const cat = categorySelect.value;

    const filtered = allEvents.filter(ev =>
      ev.title.toLowerCase().includes(term) &&
      (cat === '' || ev.category === cat)
    );

    eventsContainer.innerHTML = '';
    if (!filtered.length) {
      eventsContainer.innerHTML = '<p class="col-span-full text-center text-gray-500">Событий не найдено.</p>';
      return;
    }

    filtered.forEach(ev => {
      const div = document.createElement('div');
      div.className = 'bg-white rounded-2xl shadow-lg overflow-hidden flex flex-col';
      div.innerHTML = `
        <div class="relative">
          <img src="${ev.img || '/static/default-event.jpg'}" alt="${ev.title}" class="w-full h-48 object-cover"/>
          <span class="absolute top-3 left-3 bg-indigo-600 text-white text-xs font-bold uppercase py-1 px-3 rounded-full">
            ${ev.category}
          </span>
        </div>
        <div class="p-5 flex-1 flex flex-col justify-between">
          <h3 class="text-lg font-semibold mb-2">${ev.title}</h3>
          <div class="flex items-center text-sm text-gray-500 space-x-4 mb-4">
            <div class="flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
              <span class="ml-1">${ev.date}</span>
            </div>
            <div class="flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87M16 7a4 4 0 11-8 0 4 4 0 018 0z"/>
              </svg>
              <span class="ml-1">${ev.participants}</span>
            </div>
          </div>
          <button class="mt-auto py-2 rounded-lg ${
            ev.joined ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 text-white'
          }" ${ev.joined ? 'disabled' : ''}>
            ${ev.joined ? 'Уже участвуете' : 'Присоединиться'}
          </button>
        </div>
      `;
      eventsContainer.appendChild(div);
    });
  }

  searchInput.addEventListener('input', renderEvents);
  categorySelect.addEventListener('change', renderEvents);

  loadEvents();  // начальная загрузка
});


  document.addEventListener('DOMContentLoaded', () => {
    const nav = document.querySelector('nav');
    const footer = document.querySelector('footer');
    new IntersectionObserver(entries => {
      entries.forEach(entry => {
        nav.classList.toggle('-translate-y-2', entry.isIntersecting);
      });
    }, { threshold: 0 }).observe(footer);
  });