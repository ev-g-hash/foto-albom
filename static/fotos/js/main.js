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

  // Создаём модальное окно для подтверждения удаления
  createDeleteModal();
});

// Функции для удаления фотографий (глобальные)
function deletePhoto(photoId, photoTitle) {
  showDeleteModal(photoId, photoTitle);
}

// Красивое модальное окно для подтверждения удаления
function createDeleteModal() {
  // Создаём модальное окно если его ещё нет
  if (document.getElementById('deleteModal')) return;

  const modal = document.createElement('div');
  modal.id = 'deleteModal';
  modal.className = 'delete-modal';
  modal.innerHTML = `
    <div class="delete-modal-overlay" onclick="closeDeleteModal()"></div>
    <div class="delete-modal-content">
      <div class="delete-modal-header">
        <h3>🗑️ Подтверждение удаления</h3>
      </div>
      <div class="delete-modal-body">
        <p>Вы уверены, что хотите удалить это фото?</p>
        <p class="photo-title" id="modalPhotoTitle"></p>
      </div>
      <div class="delete-modal-footer">
        <button type="button" class="btn secondary" onclick="closeDeleteModal()">
          ❌ Отмена
        </button>
        <button type="button" class="btn delete-confirm-btn" id="confirmDeleteBtn">
          🗑️ Удалить
        </button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
}

function showDeleteModal(photoId, photoTitle) {
  const modal = document.getElementById('deleteModal');
  const titleEl = document.getElementById('modalPhotoTitle');
  const confirmBtn = document.getElementById('confirmDeleteBtn');
  
  if (modal && titleEl && confirmBtn) {
    titleEl.textContent = `"${photoTitle}"`;
    titleEl.className = 'photo-title';
    
    // Удаляем предыдущие обработчики
    const newConfirmBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
    
    // Добавляем новый обработчик
    newConfirmBtn.addEventListener('click', () => {
      confirmDeletePhoto(photoId);
    });
    
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
  }
}

function closeDeleteModal() {
  const modal = document.getElementById('deleteModal');
  if (modal) {
    modal.style.display = 'none';
    document.body.style.overflow = '';
  }
}

function confirmDeletePhoto(photoId) {
  const csrftoken = getCookie('csrftoken');
  
  fetch(`/fotos/delete/${photoId}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken,
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(response => {
    console.log('Response status:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('Response data:', data);
    
    if (data.success) {
      closeDeleteModal();
      showMessage(data.message || 'Фотография успешно удалена', 'success');
      
      // Обновляем страницу через 1 секунду для проверки результата
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    } else {
      closeDeleteModal();
      showMessage(data.error || 'Ошибка при удалении фотографии', 'error');
    }
  })
  .catch(error => {
    console.error('Fetch error:', error);
    closeDeleteModal();
    showMessage('Ошибка при удалении фотографии', 'error');
  });
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