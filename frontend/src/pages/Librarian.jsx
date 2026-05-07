import axios from 'axios';
import React, { useEffect, useState } from 'react'
import "../css/librarian.css"
import AddLibrarian from '../components/AddLibrarian';
import { toast } from 'react-toastify';
import API_URL from '../api';

function Librarian() {
  const [librarian, setLibrarian] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [search, setSearch] = useState('');

  const fetchLibrarian = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/librarian`);
      setLibrarian(response.data);
    } catch (error) {
      console.log("Error fetching librarian", error);
      toast.error("Failed to load librarians");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchLibrarian(); }, []);

  const filteredLibrarians = librarian.filter(lib =>
    lib.fullName?.toLowerCase().includes(search.toLowerCase()) ||
    lib.email?.toLowerCase().includes(search.toLowerCase()) ||
    lib.memberId?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className='librarian-container'>
      <div className='librarian-header'>
        <div>
          <h2>Librarians</h2>
          <p>Total Librarians: {librarian.length}</p>
        </div>
        <div className='librarian-header-right'>
          <input
            type='text'
            className='search-input'
            placeholder='Search by name, email or ID...'
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button className='add-btn' onClick={() => setIsModalOpen(true)}>
            + Add Librarian
          </button>
        </div>
      </div>

      <div className='librarian-table-wrapper'>
        {loading ? (
          <p className="loading-text">Loading librarians...</p>
        ) : (
          <table className="librarian-table">
            <thead>
              <tr>
                <th>Sr No.</th>
                <th>Member ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Joined At</th>
              </tr>
            </thead>
            <tbody>
              {filteredLibrarians.length > 0 ? (
                filteredLibrarians.map((member, index) => (
                  <tr key={member.memberId || index}>
                    <td>{index + 1}</td>
                    <td><span className="id-badge">{member.memberId}</span></td>
                    <td>{member.fullName}</td>
                    <td>{member.email}</td>
                    <td>{member.joinedAt || 'N/A'}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="no-data">No librarians found</td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      <AddLibrarian
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        refreshBooks={fetchLibrarian}
      />
    </div>
  );
}

export default Librarian;
