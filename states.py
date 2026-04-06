from aiogram.fsm.state import State, StatesGroup


class FeedbackSG(StatesGroup):
    """
    Контейнер станів машини кінцевих автоматів (FSM) для процесу збору відгуків.

    Цей клас наслідує `StatesGroup` і визначає кроки, які проходить користувач
    під час залишення відгуку про ресторан. Кожен атрибут є екземпляром `State`,
    що представляє окремий етап очікування вводу даних від користувача.

    Attributes:
        waiting_rating (State): Стан очікування числової оцінки візиту (від 1 до 5).
        waiting_comment (State): Стан очікування розгорнутого текстового коментаря.
    """

    waiting_rating = State()
    waiting_comment = State()


class BookingSG(StatesGroup):
    """
    Контейнер станів машини кінцевих автоматів (FSM) для процесу бронювання.

    Цей клас наслідує `StatesGroup` з фреймворку aiogram і визначає лінійний
    маршрут збору інформації від клієнта ресторану. Кожен атрибут класу є
    екземпляром `State` і представляє окремий ізольований крок у діалозі.

    Attributes:
        waiting_date (State): Стан очікування дати бронювання у форматі ДД-ММ-РРРР.
        waiting_time (State): Стан очікування часу візиту у форматі ГГ:ХХ.
        waiting_guests (State): Стан очікування введення кількості гостей (ціле число).
        waiting_wishes (State): Стан для збору додаткових побажань користувача.
        waiting_phone (State): Фінальний стан очікування валідного номеру телефону.
    """

    waiting_date = State()
    waiting_time = State()
    waiting_guests = State()
    waiting_wishes = State()
    waiting_phone = State()
