document.addEventListener('DOMContentLoaded', function() {
    const profileToggle = document.getElementById('profileToggle');
    const dropdownMenu = document.getElementById('dropdownMenu');

    // Показать/скрыть выпадающее меню
    profileToggle.addEventListener('click', function(e) {
        e.stopPropagation();
        dropdownMenu.classList.toggle('show');
    });

    // Закрыть меню при клике вне его
    document.addEventListener('click', function() {
        dropdownMenu.classList.remove('show');
    });

    // Предотвратить закрытие при клике внутри меню
    dropdownMenu.addEventListener('click', function(e) {
        e.stopPropagation();
    });
});