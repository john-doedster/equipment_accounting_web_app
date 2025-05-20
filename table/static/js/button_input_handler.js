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
    
    // AJAX-запрос
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.href = data.redirect_url;
        } else {
            alert(data.message);
            submitButton.disabled = false;
            submitButton.innerHTML = '<i class="bi bi-upload"></i> Импортировать';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка при загрузке файла');
        submitButton.disabled = false;
        submitButton.innerHTML = '<i class="bi bi-upload"></i> Импортировать';
    });
});