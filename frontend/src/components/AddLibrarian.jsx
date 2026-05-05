import React, { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import '../css/modal.css';

function AddLibrarian({ isOpen, onClose, refreshData }) {
    const [libData, setLibData] = useState({ fullName: '', memberId: '', email: '', password: '' });

    if (!isOpen) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        // Validation
        if (libData.password.length < 6) return toast.error("Password must be 6+ characters");
        if (!libData.email.includes('@')) return toast.error("Invalid email address");

        try {
            // We'll create a specific route for this in backend
            await axios.post('http://127.0.0.1:5000/api/librarian/add', libData);
            toast.success("New Librarian registered!");
            refreshData();
            onClose();
        } catch (error) {
            toast.error(error.response?.data?.error || "Registration failed");
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <h2>Register Librarian</h2>
                <form className="modal-form" onSubmit={handleSubmit}>
                    <input type="text" placeholder="Full Name" onChange={(e)=>setLibData({...libData, fullName: e.target.value})} required />
                    <input type="text" placeholder="Employee/Librarian ID" onChange={(e)=>setLibData({...libData, memberId: e.target.value})} required />
                    <input type="email" placeholder="Work Email" onChange={(e)=>setLibData({...libData, email: e.target.value})} required />
                    <input type="password" placeholder="Temporary Password" onChange={(e)=>setLibData({...libData, password: e.target.value})} required />
                    <div className="modal-actions">
                        <button type="button" className="cancel-btn" onClick={onClose}>Cancel</button>
                        <button type="submit" className="save-btn">Create Account</button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default AddLibrarian;