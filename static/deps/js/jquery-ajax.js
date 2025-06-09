// Когда html документ готов (прорисован)
$(document).ready(function () {
    // берем в переменную элемент разметки с id jq-notification для оповещений от ajax
    var successMessage = $("#jq-notification");

    // Ловим собыитие клика по кнопке добавить в корзину
    $(document).on("click", ".add-to-cart", function (e) {
        // Блокируем его базовое действие
        e.preventDefault();

        // Берем элемент счетчика в значке корзины и берем оттуда значение
        var goodsInCartCount = $("#goods-in-cart-count");
        var cartCount = parseInt(goodsInCartCount.text() || 0);

        // Получаем id товара из атрибута data-product-id
        var product_id = $(this).data("product-id");

        // Из атрибута href берем ссылку на контроллер django
        var add_to_cart_url = $(this).attr("href");

        // делаем post запрос через ajax не перезагружая страницу
        $.ajax({
            type: "POST",
            url: add_to_cart_url,
            data: {
                product_id: product_id,
                csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
            },
            success: function (data) {
                // Сообщение
                successMessage.html(data.message);
                successMessage.fadeIn(400);
                // Через 7сек убираем сообщение
                setTimeout(function () {
                    successMessage.fadeOut(400);
                }, 7000);

                // Увеличиваем количество товаров в корзине (отрисовка в шаблоне)
                cartCount++;
                goodsInCartCount.text(cartCount);

                // Меняем содержимое корзины на ответ от django (новый отрисованный фрагмент разметки корзины)
                var cartItemsContainer = $("#cart-items-container");
                cartItemsContainer.html(data.cart_items_html);

            },

            error: function (data) {
                console.log("Ошибка при добавлении оборудования в список");
            },
        });
    });



    // Ловим событие клика по кнопке удалить товар из корзины
// Модифицируем обработчик удаления товара
$(document).on("click", ".remove-from-cart", function (e) {
    e.preventDefault();
    saveFormData();
    
    var $button = $(this);
    var cart_id = $button.data("cart-id");
    var csrf_token = $button.find("[name=csrfmiddlewaretoken]").val();
    var remove_from_cart_url = $button.attr("href");
    var is_modal = remove_from_cart_url.includes('modal=true');

    $.ajax({
        type: "POST",
        url: remove_from_cart_url,
        data: {
            cart_id: cart_id,
            csrfmiddlewaretoken: csrf_token
        },
        success: function (data) {
            // Обновляем счетчик товаров в корзине
            $("#goods-in-cart-count").text(data.cart_total_quantity);
            
            // Если это модальное окно, обновляем его содержимое
            if (is_modal) {
                $(".modal-body").html(data.modal_html);
            } else {
                // Иначе обновляем обычную корзину
                $("#cart-items-list").html($(data.cart_items_html).find("#cart-items-list").html());
            }
            
            // Восстанавливаем данные формы
            restoreFormData();
            
            // Показываем уведомление
            if (data.message) {
                var successMessage = $("#jq-notification");
                successMessage.html(data.message).fadeIn(400);
                setTimeout(function() {
                    successMessage.fadeOut(400);
                }, 7000);
            }
        },
        error: function (xhr) {
            console.error("Error:", xhr.responseText);
            var successMessage = $("#jq-notification");
            successMessage.html("Ошибка при удалении товара").addClass("alert-danger").fadeIn(400);
            setTimeout(function() {
                successMessage.fadeOut(400).removeClass("alert-danger");
            }, 7000);
        }
    });
});

// Добавляем восстановление данных при загрузке страницы
$(document).ready(function() {
    restoreFormData();
});


    // Теперь + - количества товара 
    // Обработчик события для уменьшения значения
    $(document).on("click", ".decrement", function () {
        // Берем ссылку на контроллер django из атрибута data-cart-change-url
        var url = $(this).data("cart-change-url");
        // Берем id корзины из атрибута data-cart-id
        var cartID = $(this).data("cart-id");
        // Ищем ближайшеий input с количеством 
        var $input = $(this).closest('.input-group').find('.number');
        // Берем значение количества товара
        var currentValue = parseInt($input.val());
        // Если количества больше одного, то только тогда делаем -1
        if (currentValue > 1) {
            $input.val(currentValue - 1);
            // Запускаем функцию определенную ниже
            // с аргументами (id карты, новое количество, количество уменьшилось или прибавилось, url)
            updateCart(cartID, currentValue - 1, -1, url);
        }
    });

    // Обработчик события для увеличения значения
    $(document).on("click", ".increment", function () {
        // Берем ссылку на контроллер django из атрибута data-cart-change-url
        var url = $(this).data("cart-change-url");
        // Берем id корзины из атрибута data-cart-id
        var cartID = $(this).data("cart-id");
        // Ищем ближайшеий input с количеством 
        var $input = $(this).closest('.input-group').find('.number');
        // Берем значение количества товара
        var currentValue = parseInt($input.val());

        $input.val(currentValue + 1);

        // Запускаем функцию определенную ниже
        // с аргументами (id карты, новое количество, количество уменьшилось или прибавилось, url)
        updateCart(cartID, currentValue + 1, 1, url);
    });


// Функция для сохранения данных формы перед обновлением корзины
function saveFormData() {
    const formData = {
        fullName: $('#userFullName').val(),
        position: $('#userPosition').val(),
        conditions: []
    };
    
    $('.condition-select').each(function() {
        formData.conditions.push($(this).val());
    });
    
    sessionStorage.setItem('cartFormData', JSON.stringify(formData));
}

// Функция для восстановления данных формы после обновления корзины
function restoreFormData() {
    const savedData = sessionStorage.getItem('cartFormData');
    if (savedData) {
        const formData = JSON.parse(savedData);
        
        $('#userFullName').val(formData.fullName);
        $('#userPosition').val(formData.position);
        
        $('.condition-select').each(function(index) {
            if (index < formData.conditions.length) {
                $(this).val(formData.conditions[index]);
            }
        });
    }
}


function updateCart(cartID, quantity, change, url) {
    saveFormData();
    var is_modal = url.includes('modal=true');
    
    $.ajax({
        type: "POST",
        url: url,
        data: {
            cart_id: cartID,
            quantity: quantity,
            csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
        },
        success: function (data) {
            // Сообщение
            successMessage.html(data.message);
            successMessage.fadeIn(400);
            // Через 7сек убираем сообщение
            setTimeout(function () {
                successMessage.fadeOut(400);
            }, 7000);

            // Изменяем количество товаров в корзине
            var goodsInCartCount = $("#goods-in-cart-count");
            var cartCount = parseInt(goodsInCartCount.text() || 0);
            cartCount += change;
            goodsInCartCount.text(cartCount);

            // Обновляем содержимое в зависимости от контекста
            if (is_modal) {
                $(".modal-body").html(data.cart_items_html);
            } else {
                $("#cart-items-list").html($(data.cart_items_html).find("#cart-items-list").html());
            }
            
            // Восстанавливаем данные формы
            restoreFormData();
        },
        error: function (data) {
            console.log("Ошибка при изменении количества оборудования");
        },
    });
}

    // Берем из разметки элемент по id - оповещения от django
    var notification = $('#notification');
    // И через 7 сек. убираем
    if (notification.length > 0) {
        setTimeout(function () {
            notification.alert('close');
        }, 7000);
    }

// При клике по значку корзины открываем всплывающее(модальное) окно
$(document).on('click', '#modalButton', function() {
    // Переносим модальное окно в body (решает проблемы с z-index)
    $('#exampleModal').appendTo('body');
    
    // Показываем модальное окно сразу
    $('#exampleModal').modal('show');
    
    // Дополнительно загружаем свежие данные (опционально)
    $.ajax({
        url: "{% url 'cart:cart_modal_content' %}",
        success: function(data) {
            $(".modal-body").html(data);
        },
        error: function() {
            console.log("Ошибка при загрузке корзины");
        }
    });
});

    // Собыите клик по кнопке закрыть окна корзины
    $('#exampleModal .btn-close').click(function () {
        $('#exampleModal').modal('hide');
    });

    // Обработчик события радиокнопки выбора способа доставки
    $("input[name='requires_delivery']").change(function () {
        var selectedValue = $(this).val();
        // Скрываем или отображаем input ввода адреса доставки
        if (selectedValue === "1") {
            $("#deliveryAddressField").show();
        } else {
            $("#deliveryAddressField").hide();
        }
    });

    // Форматирования ввода номера телефона в форме (xxx) xxx-хххx
    document.getElementById('id_phone_number').addEventListener('input', function (e) {
        var x = e.target.value.replace(/\D/g, '').match(/(\d{0,3})(\d{0,3})(\d{0,4})/);
        e.target.value = !x[2] ? x[1] : '(' + x[1] + ') ' + x[2] + (x[3] ? '-' + x[3] : '');
    });

    // Проверяем на стороне клинта коррекность номера телефона в форме xxx-xxx-хх-хx
    $('#create_order_form').on('submit', function (event) {
        var phoneNumber = $('#id_phone_number').val();
        var regex = /^\(\d{3}\) \d{3}-\d{4}$/;

        if (!regex.test(phoneNumber)) {
            $('#phone_number_error').show();
            event.preventDefault();
        } else {
            $('#phone_number_error').hide();

            // Очистка номера телефона от скобок и тире перед отправкой формы
            var cleanedPhoneNumber = phoneNumber.replace(/[()\-\s]/g, '');
            $('#id_phone_number').val(cleanedPhoneNumber);
        }
    });
});