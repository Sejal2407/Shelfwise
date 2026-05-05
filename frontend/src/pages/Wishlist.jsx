import React, { useState, useEffect } from 'react';
import axios from 'axios';
import BookCard from '../components/bookCard';
import "../css/book.css";

function Wishlist() {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const user = JSON.parse(localStorage.getItem('user'));

  const fetchWishlist = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/wishlist', {
        params: { userId: user.email }
      });
      setBooks(response.data);
    } catch (error) {
      console.error("Error fetching wishlist:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWishlist();
  }, []);

  return (
    <div className='books-section'>
      <div className='book-header'>
        <div>
          <h2>My Wishlist</h2>
          <p>Total: {books.length} books</p>
        </div>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : books.length === 0 ? (
        <p style={{ color: "#aaa", marginTop: "2rem" }}>
          No books in your wishlist yet.
        </p>
      ) : (
        <div className="books-grid">
          {books.map((book) => (
            <BookCard
              key={book._id}
              book={book}
              refreshBooks={fetchWishlist}
              onWishlistChange={fetchWishlist}  
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default Wishlist;