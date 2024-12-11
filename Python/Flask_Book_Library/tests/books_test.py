import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from project import app, db
from project.books.models import Book


class BookModelTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()

        # Push an application context
        self.app_context = app.app_context()
        self.app_context.push()

        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # test poprawnie zdefiniowanej książki
    def test_create_book(self):
        response = self.app.post('/books/create', json={
            'name': 'Test Book',
            'author': 'Test Author',
            'year_published': 2021,
            'book_type': '5days'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to list_books

    # test brakujących danych
    def test_create_book_invalid_data(self):
        response = self.app.post('/books/create', json={
            'name': '',
            'author': 'Test Author',
            'year_published': 2021,
            'book_type': '5days'
        })
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Error creating book', response.data)

    # Validation Rules Testing: Test creating a book with invalid year_published
    def test_create_book_invalid_year(self):
        response = self.app.post('/books/create', json={
            'name': 'Test Book',
            'author': 'Test Author',
            'year_published': 'invalid_year',
            'book_type': '5days'
        })
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Error creating book', response.data)

    # Security Testing: Test creating a book with potential XSS attack
    def test_create_book_xss(self):
        response = self.app.post('/books/create', json={
            'name': '<script>alert(1)</script>',
            'author': 'Test Author',
            'year_published': 2021,
            'book_type': '5days'
        })
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Error creating book', response.data)

    # Security Testing: Test creating a book with potential SQL Injection
    def test_create_book_sql_injection(self):
        response = self.app.post('/books/create', json={
            'name': "Test'; DROP TABLE books; --",
            'author': 'Test Author',
            'year_published': 2021,
            'book_type': '5days'
        })
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Error creating book', response.data)

    # Exception Handling Testing: Test editing a book with invalid data (book not found)
    def test_edit_book_invalid_data(self):
        response = self.app.post('/books/999/edit', json={
            'name': 'Updated Book',
            'author': 'Updated Author',
            'year_published': 2022,
            'book_type': '10days'
        })
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Book not found', response.data)

    # Positive Testing: Test listing books
    def test_list_books(self):
        response = self.app.get('/books/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Books page accessed', response.data)

    # Positive Testing: Test listing books in JSON format
    def test_list_books_json(self):
        response = self.app.get('/books/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'books', response.data)

    # Positive Testing: Test fetching book data for editing
    def test_get_book_for_edit(self):
        book = Book(name='Test Book', author='Test Author', year_published=2021, book_type='5days')
        db.session.add(book)
        db.session.commit()

        response = self.app.get(f'/books/{book.id}/edit-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Book', response.data)

    # Exception Handling Testing: Test fetching book data for editing (book not found)
    def test_get_book_for_edit_not_found(self):
        response = self.app.get('/books/999/edit-data')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Book not found', response.data)

    # Positive Testing: Test deleting a book
    def test_delete_book(self):
        book = Book(name='Test Book', author='Test Author', year_published=2021, book_type='5days')
        db.session.add(book)
        db.session.commit()

        response = self.app.post(f'/books/{book.id}/delete')
        self.assertEqual(response.status_code, 302)  # Redirect to list_books

    # Exception Handling Testing: Test deleting a book (book not found)
    def test_delete_book_not_found(self):
        response = self.app.post('/books/999/delete')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Book not found', response.data)

    # Positive Testing: Test getting book details by name
    def test_get_book_details(self):
        book = Book(name='Test Book', author='Test Author', year_published=2021, book_type='5days')
        db.session.add(book)
        db.session.commit()

        response = self.app.get('/books/details/Test%20Book')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Book', response.data)

    # Exception Handling Testing: Test getting book details by name (book not found)
    def test_get_book_details_not_found(self):
        response = self.app.get('/books/details/Nonexistent%20Book')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Book not found', response.data)

if __name__ == '__main__':b
    unittest.main()
