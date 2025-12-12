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

// =============================================================================
// НОВЫЕ ФУНКЦИИ ДЛЯ РЕДАКТИРОВАНИЯ ФОТО (ТОЛЬКО ДЛЯ АВТОРИЗОВАННЫХ)
// =============================================================================

// Показываем модальное окно с действиями для фото (ТОЛЬКО ДЛЯ АВТОРИЗОВАННЫХ)
function showPhotoModal(photoId, photoTitle, photoDescription) {
  // Проверяем, авторизован ли пользователь
  const isAuthenticated = document.querySelector('.auth-btn') || 
                         window.location.pathname.includes('/fotos/') ||
                         document.querySelector('.admin-controls');
  
  if (!isAuthenticated) {
    // Если не авторизован, просто переходим к фото
    window.location.href = `/fotos/${photoId}/`;
    return;
  }
  
  const modal = createPhotoModal();
  const titleEl = modal.querySelector('.photo-title-display');
  const galleryBtn = modal.querySelector('.go-to-gallery');
  const stayBtn = modal.querySelector('.stay-here');
  const editTitleBtn = modal.querySelector('.edit-title');
  const editDescBtn = modal.querySelector('.edit-description');
  const deleteBtn = modal.querySelector('.delete-photo');
  
  // Устанавливаем название фото
  if (titleEl) {
    titleEl.textContent = photoTitle;
  }
  
  // Все кнопки редактирования показываем только для авторизованных
  if (editTitleBtn) {
    editTitleBtn.style.display = 'inline-flex';
  }
  if (editDescBtn) {
    editDescBtn.style.display = 'inline-flex';
  }
  if (deleteBtn) {
    deleteBtn.style.display = 'inline-flex';
  }
  
  // Обработчики событий
  if (galleryBtn) {
    galleryBtn.addEventListener('click', () => {
      closePhotoModal();
      window.location.href = '/fotos/';
    });
  }
  
  if (stayBtn) {
    stayBtn.addEventListener('click', () => {
      closePhotoModal();
    });
  }
  
  if (editTitleBtn) {
    editTitleBtn.addEventListener('click', () => {
      showEditTitleForm(photoId, photoTitle);
    });
  }
  
  if (editDescBtn) {
    editDescBtn.addEventListener('click', () => {
      showEditDescriptionForm(photoId, photoDescription);
    });
  }
  
  if (deleteBtn) {
    deleteBtn.addEventListener('click', () => {
      closePhotoModal();
      deletePhoto(photoId, photoTitle);
    });
  }
  
  modal.style.display = 'flex';
  document.body.style.overflow = 'hidden';
}

// Создаём модальное окно для действий с фото
function createPhotoModal() {
  let modal = document.getElementById('photoModal');
  
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'photoModal';
    modal.className = 'photo-modal';
    modal.innerHTML = `
      <div class="photo-modal-overlay" onclick="closePhotoModal()"></div>
      <div class="photo-modal-content">
        <div class="photo-modal-header">
          <h3>Действия с фото</h3>
          <div class="photo-title-display"></div>
        </div>
        <div class="photo-modal-body">
          <div class="modal-actions">
            <button type="button" class="modal-btn green go-to-gallery">
              🖼️ Перейти в галерею
            </button>
            <button type="button" class="modal-btn secondary stay-here">
              📋 Остаться в содержании
            </button>
            <button type="button" class="modal-btn edit edit-title" style="display: none;">
              ✏️ Редактировать название
            </button>
            <button type="button" class="modal-btn edit edit-description" style="display: none;">
              📝 Редактировать описание
            </button>
            <button type="button" class="modal-btn delete delete-photo" style="display: none;">
              🗑️ Удалить фото
            </button>
          </div>
          
          <!-- Форма редактирования названия -->
          <div class="edit-form" id="editTitleForm">
            <div class="form-group">
              <label for="newTitle">Новое название:</label>
              <input type="text" id="newTitle" class="form-input" placeholder="Введите новое название">
            </div>
            <div class="form-actions">
              <button type="button" class="btn" id="saveTitleBtn">💾 Сохранить</button>
              <button type="button" class="btn secondary" onclick="hideEditForms()">❌ Отмена</button>
            </div>
          </div>
          
          <!-- Форма редактирования описания -->
          <div class="edit-form" id="editDescForm">
            <div class="form-group">
              <label for="newDescription">Новое описание:</label>
              <textarea id="newDescription" class="form-textarea" placeholder="Введите новое описание"></textarea>
            </div>
            <div class="form-actions">
              <button type="button" class="btn" id="saveDescBtn">💾 Сохранить</button>
              <button type="button" class="btn secondary" onclick="hideEditForms()">❌ Отмена</button>
            </div>
          </div>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
  }
  
  return modal;
}

// Закрываем модальное окно
function closePhotoModal() {
  const modal = document.getElementById('photoModal');
  if (modal) {
    modal.style.display = 'none';
    document.body.style.overflow = '';
    hideEditForms();
  }
}

// Показываем форму редактирования названия
function showEditTitleForm(photoId, currentTitle) {
  hideEditForms();
  
  const form = document.getElementById('editTitleForm');
  const input = document.getElementById('newTitle');
  const saveBtn = document.getElementById('saveTitleBtn');
  
  if (form && input && saveBtn) {
    input.value = currentTitle || '';
    form.classList.add('active');
    
    // Удаляем предыдущие обработчики
    const newSaveBtn = saveBtn.cloneNode(true);
    saveBtn.parentNode.replaceChild(newSaveBtn, saveBtn);
    
    // Добавляем новый обработчик
    newSaveBtn.addEventListener('click', () => {
      const newTitle = input.value.trim();
      if (newTitle) {
        updatePhotoTitle(photoId, newTitle);
      }
    });
  }
}

// Показываем форму редактирования описания
function showEditDescriptionForm(photoId, currentDescription) {
  hideEditForms();
  
  const form = document.getElementById('editDescForm');
  const textarea = document.getElementById('newDescription');
  const saveBtn = document.getElementById('saveDescBtn');
  
  if (form && textarea && saveBtn) {
    textarea.value = currentDescription || '';
    form.classList.add('active');
    
    // Удаляем предыдущие обработчики
    const newSaveBtn = saveBtn.cloneNode(true);
    saveBtn.parentNode.replaceChild(newSaveBtn, saveBtn);
    
    // Добавляем новый обработчик
    newSaveBtn.addEventListener('click', () => {
      const newDescription = textarea.value.trim();
      updatePhotoDescription(photoId, newDescription);
    });
  }
}

// Скрываем все формы редактирования
function hideEditForms() {
  const forms = document.querySelectorAll('.edit-form');
  forms.forEach(form => {
    form.classList.remove('active');
  });
}

// Обновляем название фото
function updatePhotoTitle(photoId, newTitle) {
  const csrftoken = getCookie('csrftoken');
  
  fetch(`/fotos/edit/${photoId}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken,
      'X-Requested-With': 'XMLHttpRequest'
    },
    body: JSON.stringify({
      field: 'title',
      value: newTitle
    })
  })
  .then(response => {
    console.log('Response status:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('Response data:', data);
    
    if (data.success) {
      hideEditForms();
      showMessage(data.message || 'Название успешно обновлено', 'success');
      
      // Обновляем название в модальном окне
      const titleEl = document.querySelector('.photo-title-display');
      if (titleEl) {
        titleEl.textContent = newTitle;
      }
      
      // Обновляем название в списке
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    } else {
      showMessage(data.error || 'Ошибка при обновлении названия', 'error');
    }
  })
  .catch(error => {
    console.error('Fetch error:', error);
    showMessage('Ошибка при обновлении названия', 'error');
  });
}

// Обновляем описание фото
function updatePhotoDescription(photoId, newDescription) {
  const csrftoken = getCookie('csrftoken');
  
  fetch(`/fotos/edit/${photoId}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken,
      'X-Requested-With': 'XMLHttpRequest'
    },
    body: JSON.stringify({
      field: 'description',
      value: newDescription
    })
  })
  .then(response => {
    console.log('Response status:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('Response data:', data);
    
    if (data.success) {
      hideEditForms();
      showMessage(data.message || 'Описание успешно обновлено', 'success');
      
      // Обновляем описание в модальном окне
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    } else {
      showMessage(data.error || 'Ошибка при обновлении описания', 'error');
    }
  })
  .catch(error => {
    console.error('Fetch error:', error);
    showMessage('Ошибка при обновлении описания', 'error');
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