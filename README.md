# foodgram-project-react

### Описание проекта
Cайт Foodgram или «Продуктовый помощник» - онлайн-сервис, на котором пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Используемый стек технологий
* Python/Django
* JavaScript/React
* HTML & CSS
* Docker
* PostgreSQL

### Локальное развертывание проекта
- Собрать необходимые docker-контейнеры и запустить их:
```
docker-compose up -d --build
``` 
- Выполнить миграции:
```
docker-compose exec web python manage.py migrate --noinput
```
- Создать супер-пользователя:
```
docker-compose exec web python manage.py createsuperuser
```
- Собрать статические файлы:
```
docker-compose exec web python manage.py collectstatic --no-input
```

### Об авторе
Корнилов Денис
студент Яндекс.Практикума 
курса Python разработчик
12 когорты
