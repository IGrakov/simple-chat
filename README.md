# Simple Chat App

## Local deployment (Ubuntu)

1. Make sure that poetry is installed, otherwise run:\
``pip install poetry``

2. Install necessary dependencies specified in pyproject.toml and poetry.lock (you should be in project folder):\
``poetry install``

3. To activate virtual environment:\
``poetry shell``

4. Run migrations:\
``poetry run python manage.py migrate``

5. Start dev server\
``poetry run python manage.py runserver``

6. To run tests:\
``poetry run python manage.py test``

7. To run a specific test:\
``poetry run python manage.py test <path_to_specific_test>``\
e.g.:
``poetry run python manage.py test book.tests.tests.PrivateBookApiTests.test_list_books_filtered_success``