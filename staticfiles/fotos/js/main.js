document.addEventListener('DOMContentLoaded', () => {
  // Лёгкая печать текста на главной
  const typedEl = document.getElementById('typed');
  if (typedEl) {
    const text = 'Цифровой альбом Нурмеева Дениса Рашитовича!';
    let i = 0;
    const timer = setInterval(() => {
      typedEl.textContent += text[i];
      i++;
      if (i >= text.length) clearInterval(timer);
    }, 80); // Немного быстрее для короткого текста
  }

  // УБРАЛИ: Весь блок с конфетти canvas - больше не нужен

  // Адаптивная пагинация
  function initResponsivePagination() {
    const galleryDataEl = document.getElementById('gallery-data');
    if (!galleryDataEl) return;

    const galleryData = JSON.parse(galleryDataEl.textContent);
    const galleryEl = document.getElementById('gallery');
    
    if (!galleryEl) return;

    function updatePagination() {
      const isMobile = window.innerWidth <= 560;
      const photosPerPage = isMobile ? 1 : 3;
      
      // Если количество фото изменилось, перезагружаем страницу с новыми параметрами
      const currentURL = new URL(window.location);
      const currentPerPage = currentURL.searchParams.get('per_page') || '3';
      
      if (currentPerPage != photosPerPage.toString()) {
        currentURL.searchParams.set('per_page', photosPerPage.toString());
        // Перезагружаем только если мы на странице галереи
        if (window.location.pathname.includes('/fotos/')) {
          window.location.href = currentURL.toString();
        }
      }
    }

    // Проверяем при загрузке и изменении размера окна
    updatePagination();
    window.addEventListener('resize', () => {
      // Делаем задержку чтобы избежать слишком частых перезагрузок
      clearTimeout(window.resizeTimeout);
      window.resizeTimeout = setTimeout(updatePagination, 300);
    });
  }

  // Инициализируем адаптивную пагинацию только на странице галереи
  if (window.location.pathname.includes('/fotos/')) {
    initResponsivePagination();
  }

  // Лайтбокс для галереи
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = document.getElementById('lightbox-img');
  if (lightbox && lightboxImg) {
    document.addEventListener('click', (e) => {
      const target = e.target;
      if (target && target.matches('.gallery img')) {
        const full = target.getAttribute('data-full') || target.src;
        const title = target.getAttribute('data-title') || '';
        const desc = target.getAttribute('data-desc') || '';
        lightboxImg.src = full;
        lightboxImg.alt = title || desc || 'Увеличенное фото';
        lightbox.classList.add('open');
      }
    });

    lightbox.addEventListener('click', () => {
      lightbox.classList.remove('open');
      lightboxImg.src = '';
    });
  }
});

// Функции для удаления фотографий (глобальные)
function deletePhoto(photoId, photoTitle) {
  if (confirm(`Вы уверены, что хотите удалить "${photoTitle}"?`)) {
    fetch(`/fotos/delete/${photoId}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Удаляем элемент из списка
        const listItem = document.querySelector(`button[onclick="deletePhoto(${photoId}`).closest('li');
        if (listItem) {
          listItem.remove();
        }
        showMessage(data.message, 'success');
      } else {
        showMessage(data.error, 'error');
      }
    })
    .catch(error => {
      showMessage('Ошибка при удалении фотографии', 'error');
    });
  }
}

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

function showMessage(text, type) {
  // Создаём контейнер сообщений если его нет
  let messagesContainer = document.querySelector('.messages');
  if (!messagesContainer) {
    messagesContainer = document.createElement('div');
    messagesContainer.className = 'messages';
    const card = document.querySelector('.card');
    if (card) {
      card.insertBefore(messagesContainer, card.firstChild.nextSibling);
    }
  }
  
  const message = document.createElement('div');
  message.className = `message ${type}`;
  message.textContent = text;
  messagesContainer.appendChild(message);
  
  // Удаляем сообщение через 5 секунд
  setTimeout(() => {
    if (message.parentNode) {
      message.remove();
    }
  }, 5000);
}