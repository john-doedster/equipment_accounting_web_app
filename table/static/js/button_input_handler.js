document.addEventListener('DOMContentLoaded', function() {
    console.log('Script loaded'); // Проверка загрузки
    
    const fileInput = document.getElementById('fileInput');
    const fileButton = document.getElementById('fileButton');
    const fileLabel = document.getElementById('fileLabel');
    const fileName = document.getElementById('fileName');
    const submitButton = document.getElementById('submitButton');
    const form = document.getElementById('importForm');

    if (!fileInput || !form) {
        console.error('Элементы не найдены! Проверьте ID в HTML.');
        return;
    }

    fileButton.addEventListener('click', function() {
        console.log('Кнопка "Выбрать файл" нажата');
        fileInput.click();
    });

    fileInput.addEventListener('change', function(e) {
        console.log('Файл выбран', this.files);
        
        if (this.files && this.files[0]) {
            const file = this.files[0];
            fileName.textContent = file.name;
            fileName.style.display = 'block';
            fileLabel.textContent = 'Выбран файл:';
            submitButton.disabled = false;

            if (!file.name.match(/\.(xlsx|xls)$/i)) {
                alert('Пожалуйста, выберите файл Excel (.xlsx или .xls)');
                this.value = '';
                fileName.style.display = 'none';
                fileLabel.textContent = 'Выберите файл Excel';
                submitButton.disabled = true;
            }
        }
    });

    form.addEventListener('submit', function(e) {
        console.log('Форма отправляется...');
        
        if (!fileInput.files.length) {
            e.preventDefault();
            alert('Пожалуйста, выберите файл для загрузки');
            return false;
        }
        
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="bi bi-arrow-repeat spinner"></i> Идет загрузка...';
        console.log('Форма валидна, отправка данных');
    });
});