import React, { useEffect, useState } from 'react'
import "../css/borrowedBooks.css"
import { LogOut } from "lucide-react"
import axios from 'axios';
import { toast } from 'react-toastify';
import API_URL from '../api';

function BorrowedBooks() {

  const [activeFilter, setActiveFilter] = useState("Yet to Return");
  const [borrowedBooks, setBorrowedBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const user = JSON.parse(localStorage.getItem('user'));

  const fetchBorrowedBooks = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/borrowed`, {
        params: { userId: user.email }
      });
      setBorrowedBooks(response.data);
    } catch (error) {
      console.error("Error fetching borrowed books", error);
      toast.error("Failed to load borrowed books");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchBorrowedBooks();
  }, []);

  const handleReturn = async (borrowId) => {
    try {
      console.log("Returning borrowId:", borrowId); // 👈 debug log
      const response = await axios.post(`${API_URL}/api/books/return-by-record`, {
        borrowId: borrowId
      });
      console.log("Return response:", response.data); // 👈 debug log
      toast.success("Book returned successfully!");
      fetchBorrowedBooks();
    } catch (error) {
      console.error("Return error:", error.response?.data); // 👈 debug log
      toast.error(error.response?.data?.error || "Return failed");
    }
  };

  const today = new Date().toISOString().split('T')[0];

  const filteredBooks = borrowedBooks.filter((book) => {
    if (activeFilter === "Yet to Return") return book.status === "borrowed";
    if (activeFilter === "Total Borrowed Books") return true;
    if (activeFilter === "Pending Fines") return book.status === "borrowed" && book.returnDate < today;
    return true;
  });

  return (
    <div className="borrowed-section">

      {/* Same header style as Books page */}
      <div className="borrowed-header">
        <div>
          <h2>Borrowed Books</h2>
          <p>Total Records: {borrowedBooks.length}</p>
        </div>
      </div>

      <div className='filter-btn'>
        <button
          className={activeFilter === "Yet to Return" ? "active" : ""}
          onClick={() => setActiveFilter("Yet to Return")}
        >Yet to Return</button>
        <button
          className={activeFilter === "Total Borrowed Books" ? "active" : ""}
          onClick={() => setActiveFilter("Total Borrowed Books")}
        >Total Borrowed Books</button>
        <button
          className={activeFilter === "Pending Fines" ? "active" : ""}
          onClick={() => setActiveFilter("Pending Fines")}
        >Pending Fines</button>
      </div>

      <div className="borrowed-table-wrapper">
        {loading ? (
          <p>Loading...</p>
        ) : filteredBooks.length === 0 ? (
          <p>No books found.</p>
        ) : (
          <table className='borrowed-table'>
            <thead>
              <tr>
                <th>ISBN</th>
                <th>Book Name</th>
                <th>Author</th>
                <th>Date Borrowed</th>
                <th>Expected Return</th>
                <th>Status</th>
                <th>Return</th>
              </tr>
            </thead>
            <tbody>
              {filteredBooks.map((book, index) => (
                <tr key={index}>
                  <td>{book.isbn}</td>
                  <td>{book.bookName}</td>
                  <td>{book.author}</td>
                  <td>{book.dateBorrowed}</td>
                  <td>{book.returnDate}</td>
                  <td>
                    <span className={
                      book.status === "returned" ? "status-returned" :
                      book.returnDate < today ? "status-overdue" :
                      "status-borrowed"
                    }>
                      {book.status === "returned" ? "Returned" :
                       book.returnDate < today ? "Overdue" :
                       "Borrowed"}
                    </span>
                  </td>
                  <td>
                    {book.status === "borrowed" ? (
                      <LogOut
                        size={20}
                        className="return-icon"
                        onClick={() => handleReturn(book.borrowId)}
                        title="Return Book"
                      />
                    ) : (
                       book.returnDate
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default BorrowedBooks;
