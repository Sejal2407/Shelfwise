import React, { useState, useEffect } from 'react';
import axios from 'axios';
import BookCard from '../components/bookCard';
import AddBook from '../components/AddBook';
import "../css/book.css";

function Books() {
  const [books, setBooks] = useState([]);
  const [search, setSearch] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('All');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedBook, setSelectedBook] = useState(null);
  const user = JSON.parse(localStorage.getItem('user'));
  const isLibrarian = user?.role === 'librarian';

  const handleEdit = (book) => { setSelectedBook(book); setIsModalOpen(true); };
  const handleAddNew = () => { setSelectedBook(null); setIsModalOpen(true); };

  const fetchBooks = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/books');
      setBooks(response.data);
    } catch (error) {
      console.error("Error fetching books:", error);
    }
  };

  useEffect(() => { fetchBooks(); }, []);

  // Get unique genres from books
  const genres = ['All', ...new Set(books.map(b => b.genre).filter(Boolean))];

  // Filter by search and genre
  const filteredBooks = books.filter(book => {
    const matchesSearch =
      book.title?.toLowerCase().includes(search.toLowerCase()) ||
      book.author?.toLowerCase().includes(search.toLowerCase()) ||
      book.isbn?.toLowerCase().includes(search.toLowerCase());
    const matchesGenre = selectedGenre === 'All' || book.genre === selectedGenre;
    return matchesSearch && matchesGenre;
  });

  return (
    <div className='books-section'>
      <div className='book-header'>
        <div>
          <h2>Books</h2>
          <p>Total Books: {books.length}</p>
        </div>
        {isLibrarian && (
          <button className='add-btn' onClick={handleAddNew}>+ Add new Book</button>
        )}
      </div>

      {/* Search and Filter */}
      <div className='book-controls'>
        <input
          type='text'
          className='search-input'
          placeholder='Search by title, author or ISBN...'
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className='genre-filters'>
          {genres.map(genre => (
            <button
              key={genre}
              className={`genre-btn ${selectedGenre === genre ? 'active' : ''}`}
              onClick={() => setSelectedGenre(genre)}
            >
              {genre}
            </button>
          ))}
        </div>
      </div>

      {filteredBooks.length === 0 ? (
        <p style={{ color: '#aaa', marginTop: '2rem' }}>No books found.</p>
      ) : (
        <div className="books-grid">
          {filteredBooks.map((book) => (
            <BookCard
              key={book._id}
              book={book}
              refreshBooks={fetchBooks}
              onEdit={() => handleEdit(book)}
            />
          ))}
        </div>
      )}

      <AddBook
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        refreshBooks={fetchBooks}
        initialData={selectedBook}
      />
    </div>
  );
}

export default Books;