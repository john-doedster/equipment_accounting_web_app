document.addEventListener('DOMContentLoaded', function() {
    // Получаем элементы DOM
    const form = document.getElementById('importForm');
    const fileInput = document.getElementById('fileInput');
    const submitButton = document.getElementById('submitButton');
    const fileButton = document.getElementById('fileButton');
    const fileName = document.getElementById('fileName');
    const fileLabel = document.getElementById('fileLabel');

    // Проверяем, что все элементы существуют
    if (!form || !fileInput || !submitButton || !fileButton) {
        console.error('Не удалось найти необходимые элементы DOM');
        return;
    }

    // Обработчик для кнопки выбора файла
    fileButton.addEventListener('click', function() {
        fileInput.click();
    });

    // Обработчик изменения файла
    fileInput.addEventListener('change', function() {
        if (this.files && this.files.length > 0) {
            fileName.textContent = this.files[0].name;
            fileName.style.display = 'block';
            fileLabel.textContent = 'Выбран файл:';
            submitButton.disabled = false;
        } else {
            fileName.style.display = 'none';
            fileLabel.textContent = 'Выберите файл Excel';
            submitButton.disabled = true;
        }
    });

    // Обработчик отправки формы
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        console.log('Форма отправляется...');
        
        if (!fileInput.files.length) {
            alert('Пожалуйста, выберите файл для загрузки');
            return false;
        }
        
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="bi bi-arrow-repeat spinner"></i> Идет загрузка...';
        
        // Создаем FormData и добавляем файл
        const formData = new FormData(form);
        
        // Добавляем CSRF токен
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // AJAX-запрос
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = data.redirect_url;
            } else {
                alert(data.message || 'Произошла ошибка при обработке файла');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при загрузке файла');
        })
        .finally(() => {
            submitButton.disabled = false;
            submitButton.innerHTML = '<i class="bi bi-upload"></i> Импортировать';
        });
    });
});