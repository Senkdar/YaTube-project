# Проект Yatube
Yatube - социальная сеть с возможность размещения публикаций, комментариев к ним а также подписки на интересующих авторов.

## Как запустить проект (для Windows):
Клонировать репозиторий и перейти в него в командной строке:

```bash
  git clone https://github.com/crocodile-gandhi/api_yamdb
  
  cd api_yamdb
```
 
Cоздать и активировать виртуальное окружение:

```bash
python -m venv venv

source Venv/Scripts/activate

```
Установить зависимости из файла requirements.txt:
```bash
pip install -r requirements.txt
```
Выполнить миграции:
```bash
python manage.py migrate
```
Запустить проект:
```bash
python manage.py runserver   
```
