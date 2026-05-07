import axios from 'axios'
import React, { useEffect, useState } from 'react'
import { toast } from 'react-toastify';
import "../css/members.css";
import API_URL from '../api';

function Members() {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const fetchMembers = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/members`);
        setMembers(response.data);
      } catch (error) {
        console.log("Error fetching members", error);
        toast.error("Failed to load members");
      } finally {
        setLoading(false);
      }
    };
    fetchMembers();
  }, []);

  const filteredMembers = members.filter(member =>
    member.fullName?.toLowerCase().includes(search.toLowerCase()) ||
    member.email?.toLowerCase().includes(search.toLowerCase()) ||
    member.memberId?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className='members-container'>
      <div className='members-header'>
        <div>
          <h2>Library Members</h2>
          <p>Total Members: {members.length}</p>
        </div>
        <input
          type='text'
          className='search-input'
          placeholder='Search by name, email or ID...'
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className='members-table-wrapper'>
        {loading ? (
          <p className="loading-text">Loading members...</p>
        ) : (
          <table className="members-table">
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
              {filteredMembers.length > 0 ? (
                filteredMembers.map((member, index) => (
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
                  <td colSpan="5" className="no-data">No members found</td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default Members;
