import React, { useState, useEffect } from "react";
import { BookMarked, Edit, Trash } from "lucide-react";
import "../css/bookCard.css";
import axios from "axios";
import { toast } from "react-toastify";
import Swal from "sweetalert2";


function BookCard({ book, refreshBooks, onEdit, onWishlistChange }) {
  const [isBorrowed, setIsBorrowed] = useState(false);
  const [isWishlisted, setIsWishlisted] = useState(false);
  const user = JSON.parse(localStorage.getItem('user'));
  const isLibrarian = user?.role === 'librarian';

  useEffect(() => {
    if (isLibrarian) return;

    const checkStatuses = async () => {
      try {
        const [borrowRes, wishRes] = await Promise.all([
          axios.get('http://127.0.0.1:5000/api/books/borrow-status', {
            params: { userId: user.email, bookId: book._id }
          }),
          axios.get('http://127.0.0.1:5000/api/wishlist/status', {
            params: { userId: user.email, bookId: book._id }
          })
        ]);
        setIsBorrowed(borrowRes.data.isBorrowed);
        setIsWishlisted(wishRes.data.isWishlisted);
      } catch (error) {
        console.error("Error checking statuses", error);
      }
    };

    checkStatuses();
  }, [book._id]);

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    const day = date.getDate();
    const month = date.toLocaleString('default', { month: 'long' });
    const suffix =
      day % 10 === 1 && day !== 11 ? 'st' :
      day % 10 === 2 && day !== 12 ? 'nd' :
      day % 10 === 3 && day !== 13 ? 'rd' : 'th';
    return `${day}${suffix} ${month}`;
  };

  const handleDelete = async (bookId) => {
    const result = await Swal.fire({
    title: 'Delete Book?',
    text: 'This action cannot be undone.',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#e74c3c',
    cancelButtonColor: '#444',
    confirmButtonText: 'Yes, delete it',
    cancelButtonText: 'Cancel',
    background: '#1a1a1a',
    color: '#fff',
  });
    if (result.isConfirmed) {
      try {
        await axios.delete(`http://127.0.0.1:5000/api/books/${bookId}`);
        toast.success("Book removed from the library");
        refreshBooks();
      } catch (error) {
        toast.error("Failed to delete book");
      }
    }
  };

  const handleBorrow = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/books/borrow', {
        userId: user.email,
        bookId: book._id
      });
      toast.success(`Borrowed! Return by: ${formatDate(response.data.returnDate)}`);
      setIsBorrowed(true);
      if (isWishlisted) {
        await axios.post('http://127.0.0.1:5000/api/wishlist/remove', {
          userId: user.email,
          bookId: book._id
        });
        setIsWishlisted(false);
        if (onWishlistChange) onWishlistChange();
      }
      refreshBooks();
    } catch (error) {
      toast.error(error.response?.data?.error || "Borrowing failed");
    }
  };

  const handleReturn = async () => {
    try {
      await axios.post('http://127.0.0.1:5000/api/books/return', {
        userId: user.email,
        bookId: book._id
      });
      toast.success("Book returned successfully!");
      setIsBorrowed(false);
      refreshBooks();
    } catch (error) {
      toast.error(error.response?.data?.error || "Return failed");
    }
  };

  const handleWishlist = async () => {
    try {
      if (isWishlisted) {
        await axios.post('http://127.0.0.1:5000/api/wishlist/remove', {
          userId: user.email,
          bookId: book._id
        });
        toast.success("Removed from wishlist");
        setIsWishlisted(false);
      } else {
        await axios.post('http://127.0.0.1:5000/api/wishlist/add', {
          userId: user.email,
          bookId: book._id
        });
        toast.success("Added to wishlist!");
        setIsWishlisted(true);
      }
      // Refresh wishlist page if callback provided
      if (onWishlistChange) onWishlistChange();
    } catch (error) {
      toast.error(error.response?.data?.error || "Wishlist action failed");
    }
  };

  return (
    <div className="book-card">
      <img src={book.cover} alt={book.title} className="book-cover" />
      <div className="book-info">
        <h3>{book.title}</h3>
        <p>by {book.author}</p>

        {book.available < 1 ? (
          <p>Not available</p>
        ) : (
          <p>Available: {book.available}</p>
        )}

        {isLibrarian ? (
          <div className="book-action-btn">
            <button onClick={() => handleDelete(book._id)}><Trash size={18} /></button>
            <button onClick={onEdit}><Edit size={18} /></button>
          </div>
        ) : (
          <div className="book-actions">
            {isBorrowed ? (
              <button className="return-btn" onClick={handleReturn}>
                Return
              </button>
            ) : (
              <button
                className="borrow-btn"
                onClick={handleBorrow}
                disabled={book.available <= 0}>
                Borrow
              </button>
            )}

            <button
              className={`wishlist-btn ${isWishlisted ? "wishlisted" : ""}`}
              onClick={handleWishlist}
            >
              <BookMarked size={18} />
              {isWishlisted ? "Wishlisted" : "Wishlist"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default BookCard;