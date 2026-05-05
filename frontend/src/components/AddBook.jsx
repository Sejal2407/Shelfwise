import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import '../css/modal.css';

function AddBook({ isOpen, onClose, refreshBooks, initialData = null }) {
    const isEdit = !!initialData;
    const [bookData, setBookData] = useState({
        title: '', author: '', isbn: '', publisher: '', genre: 'Fiction', available: 1
    });
    const [selectedFile, setSelectedFile] = useState(null);
    const [preview, setPreview] = useState(null);

    useEffect(() => {
        if (initialData) {
            setBookData({ ...initialData });
            setPreview(initialData.cover);
        } else {
            setBookData({ title: '', author: '', isbn: '', publisher: '', genre: 'Fiction', available: 1 });
            setSelectedFile(null);
            setPreview(null);
        }
    }, [initialData, isOpen]);

    if (!isOpen) return null;

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setSelectedFile(file);
            setPreview(URL.createObjectURL(file));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData();

        Object.keys(bookData).forEach(key => {
            if (key !== '_id' && key !== 'cover') {
                formData.append(key, bookData[key]);
            }
        });

        if (selectedFile) {
            formData.append('cover', selectedFile);
        } else if (isEdit && bookData.cover) {
            formData.append('existingCover', bookData.cover);
        }

        try {
            const url = isEdit
                ? `http://127.0.0.1:5000/api/books/${initialData._id}`
                : `http://127.0.0.1:5000/api/books/add`;
            const method = isEdit ? 'put' : 'post';

            await axios({ method, url, data: formData, headers: { 'Content-Type': 'multipart/form-data' } });

            toast.success(isEdit ? "Book updated!" : "Book added!");
            setTimeout(() => { refreshBooks(); onClose(); }, 1500);
        } catch (error) {
            toast.error(error.response?.data?.error || "Error saving book");
        }
    };

    return (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
            <div className="modal-content">
                <h2>{isEdit ? "Edit Book" : "Add New Book"}</h2>

                {/* ✅ Fixed preview */}
                {preview && (
                    <div className="image-preview">
                        <img src={preview} alt="Cover Preview" />
                    </div>
                )}

                <form className="modal-form" onSubmit={handleSubmit}>

                    <div className="input-group">
                        <label>Book Title</label>
                        <input
                            type="text"
                            value={bookData.title}
                            required
                            placeholder="Enter book title"
                            onChange={(e) => setBookData({ ...bookData, title: e.target.value })}
                        />
                    </div>

                    <div className="input-group">
                        <label>Author Name</label>
                        <input
                            type="text"
                            value={bookData.author}
                            required
                            placeholder="Enter author name"
                            onChange={(e) => setBookData({ ...bookData, author: e.target.value })}
                        />
                    </div>

                    <div className="input-row">
                        <div className="input-group">
                            <label>Publisher</label>
                            <input
                                type="text"
                                value={bookData.publisher}
                                required
                                placeholder="Publisher name"
                                onChange={(e) => setBookData({ ...bookData, publisher: e.target.value })}
                            />
                        </div>
                        <div className="input-group input-small">
                            <label>Qty</label>
                            <input
                                type="number"
                                min="0"
                                value={bookData.available}
                                required
                                onChange={(e) => setBookData({ ...bookData, available: e.target.value })}
                            />
                        </div>
                    </div>

                    <div className="input-group">
                        <label>ISBN Number</label>
                        <input
                            type="text"
                            value={bookData.isbn}
                            required
                            placeholder="Enter ISBN"
                            onChange={(e) => setBookData({ ...bookData, isbn: e.target.value })}
                        />
                    </div>

                    <div className="input-group">
                        <label>Genre</label>
                        <select
                            value={bookData.genre}
                            onChange={(e) => setBookData({ ...bookData, genre: e.target.value })}
                        >
                            <option value="Fiction">Fiction</option>
                            <option value="Non-Fiction">Non-Fiction</option>
                            <option value="Classic">Classic</option>
                            <option value="Fantasy">Fantasy</option>
                            <option value="Dystopian">Dystopian</option>
                            <option value="Thriller">Thriller</option>
                            <option value="Mystery">Mystery</option>
                            <option value="Romance">Romance</option>
                            <option value="Self Help">Self Help</option>
                            <option value="Biography">Biography</option>
                            <option value="Science">Science</option>
                            <option value="History">History</option>
                        </select>
                    </div>

                    <div className="input-group">
                        <label>{isEdit ? "Change Cover Image (Optional)" : "Upload Cover Image"}</label>
                        <input
                            type="file"
                            accept="image/*"
                            onChange={handleFileChange}
                            required={!isEdit}
                        />
                    </div>

                    <div className="modal-actions">
                        <button type="button" className="cancel-btn" onClick={onClose}>Cancel</button>
                        <button type="submit" className="save-btn">{isEdit ? "Save Changes" : "Add Book"}</button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default AddBook;