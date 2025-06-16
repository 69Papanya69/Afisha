document.addEventListener('DOMContentLoaded', function () {
    const theaterSelect = document.querySelector('#id_theater');
    const hallSelect = document.querySelector('#id_hall');

    if (!theaterSelect || !hallSelect) return;

    function updateHalls(theaterId) {
        if (!theaterId) return;

        fetch(`/perfomance/api/halls/?theater_id=${theaterId}`)
            .then(response => response.json())
            .then(data => {
                // Очистка текущих опций
                hallSelect.innerHTML = '<option value="">---------</option>';

                // Добавление новых опций
                data.forEach(hall => {
                    const option = document.createElement('option');
                    option.value = hall.id;
                    option.textContent = hall.number_hall;
                    hallSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Ошибка при получении залов:', error);
            });
    }

    // При загрузке страницы — если театр уже выбран, обновляем залы
    if (theaterSelect.value) {
        updateHalls(theaterSelect.value);
    }

    // Обработчик изменения театра
    theaterSelect.addEventListener('change', function () {
        updateHalls(this.value);
    });
});
