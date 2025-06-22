document.addEventListener('DOMContentLoaded', () => {
  const eventsContainer = document.getElementById('events-container');
  const searchInput     = document.getElementById('search-input');
  const categorySelect  = document.getElementById('category-select');
  let allEvents = [];

  // Загрузить события с сервера
  async function loadEvents() {
    try {
      const res = await fetch(`/admin/events/json?user_id=${userId}`);
      const json = await res.json();
      allEvents = json.events || [];
      renderEvents();
    } catch (err) {
      console.error("Ошибка загрузки событий:", err);
      eventsContainer.innerHTML = '<p class="col-span-full text-center text-red-500">Ошибка загрузки.</p>';
    }
  }

  // Создать и вставить карточку
  function renderEvents() {
    const term = searchInput.value.trim().toLowerCase();
    const cat  = categorySelect.value;
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
      // Корневой контейнер карточки — делает всю карточку кликабельной
      console.log(ev);
      const card = document.createElement('div');
      card.className = 'bg-white/70 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 overflow-hidden hover:shadow-xl transition-all duration-300 group cursor-pointer flex flex-col';
      card.onclick = () => window.location.href = `/user/event/${ev.id}`;

      card.innerHTML = `
        <div class="relative">
        <img src="${ev.img}"
               alt="${ev.title}"
               class="w-full h-48 object-cover"/>
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
                      d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
              <span class="ml-1">${ev.participants}</span>
            </div>
          </div>
          <button
            class="mt-auto py-2 rounded-lg ${ev.joined ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 text-white'}"
            ${ev.joined ? 'disabled' : ''}
            onclick="joinEvent(${ev.id}, this)">
            ${ev.joined ? 'Уже участвуете' : 'Присоединиться'}
          </button>
        </div>
      `;

      eventsContainer.appendChild(card);
    });
  }

  // Фильтрация в реальном времени
  searchInput.addEventListener('input', renderEvents);
  categorySelect.addEventListener('change', renderEvents);

  // Стартуем
  loadEvents();
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