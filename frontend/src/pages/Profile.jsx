import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Swal from 'sweetalert2';
import "../css/profile.css";

function Profile() {
  const navigate = useNavigate();
  const savedUser = JSON.parse(localStorage.getItem('user'));
  const isLibrarian = savedUser?.role === 'librarian';
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState({
    name: savedUser?.fullName || "",
    id: "",
    email: savedUser?.email || "",
    joined: "",
    role: savedUser?.role ? `${savedUser.role.charAt(0).toUpperCase()}${savedUser.role.slice(1)}` : "",
    stats: {
      borrowed: 0,
      returned: 0,
      wishlist: 0,
      fines: "Rs. 0.00"
    }
  });

  useEffect(() => {
    if (!savedUser?.email) {
      navigate('/login');
      return;
    }

    const fetchProfile = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/profile', {
          params: { userId: savedUser.email }
        });

        setUser({
          name: response.data.fullName,
          id: response.data.memberId,
          email: response.data.email,
          joined: response.data.joined,
          role: response.data.role,
          stats: response.data.stats
        });
      } catch (error) {
        console.error("Error fetching profile details:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [navigate, savedUser?.email]);

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/login');
  };

  const handleDeleteAccount = async () => {
    const result = await Swal.fire({
      title: 'Delete Account?',
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
    if (!result.isConfirmed || !savedUser?.email) return;

    try {
      await axios.delete('http://127.0.0.1:5000/api/profile', {
        data: { userId: savedUser.email }
      });
      localStorage.removeItem('user');
      navigate('/signup');
    } catch (error) {
      console.error("Error deleting account:", error);
    }
  };

  return (
    <div className='profile-container'>
      <div className='profile-card'>
        <div className='profile-header'>
          <div className='profile-avatar'>
            {user.name ? user.name.charAt(0).toUpperCase() : "U"}
          </div>
          <div className='profile-title'>
            <h2>{user.name}</h2>
            <p className='member-id'>{user.id}</p>
            <span className='role-badge'>{user.role}</span>
          </div>
        </div>

        <hr className='divider' />

        <div className='profile-details'>
          <div className='detail-group'>
            <label>Email Address</label>
            <p>{loading ? "Loading..." : user.email}</p>
          </div>
          <div className='detail-group'>
            <label>Member Since</label>
            <p>{loading ? "Loading..." : user.joined}</p>
          </div>
        </div>

        {!isLibrarian && (
          <div className='profile-stats'>
            <div className='stat-item'>
              <h3>{user.stats.borrowed}</h3>
              <p>Active Borrows</p>
            </div>
            <div className='stat-item'>
              <h3>{user.stats.returned}</h3>
              <p>Total Read</p>
            </div>
            <div className='stat-item'>
              <h3>{user.stats.fines}</h3>
              <p>Pending Fines</p>
            </div>
          </div>
        )}

        <div className='profile-actions'>
          <button className='logout-btn' onClick={handleDeleteAccount}>Delete Account</button>
        </div>
      </div>
    </div>
  );
}

export default Profile;
