document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const fileButton = document.getElementById('fileButton');
    const fileLabel = document.getElementById('fileLabel');
    const fileName = document.getElementById('fileName');
    const submitButton = document.getElementById('submitButton');
    
    fileButton.addEventListener('click', function() {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', function(e) {
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
    
    document.getElementById('importForm').addEventListener('submit', function(e) {
        if (!fileInput.files.length) {
            e.preventDefault();
            alert('Пожалуйста, выберите файл для загрузки');
            return false;
        }
        
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="bi bi-arrow-repeat spinner"></i> Идет загрузка...';
    });
});