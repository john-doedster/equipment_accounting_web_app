document.getElementById('importForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const submitButton = document.getElementById('submitButton');
    
    // Показываем индикатор загрузки
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="bi bi-arrow-repeat spinner"></i> Идет загрузка...';
    
    // Отправка AJAX-запроса
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
        alert('Произошла ошибка при отправке файла');
        submitButton.disabled = false;
        submitButton.innerHTML = '<i class="bi bi-upload"></i> Импортировать';
    });
});