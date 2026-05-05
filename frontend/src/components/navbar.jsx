import React, { useEffect, useState } from 'react'
import {NavLink, useLocation, useNavigate} from "react-router-dom"
import "../css/navbar.css"
import { toast } from 'react-toastify';

function Navbar(){
  const navigate = useNavigate();
  const location = useLocation();
  const [user,setUser] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    const savedUser = JSON.parse(localStorage.getItem('user'));
    setUser(savedUser);
  },[location]);
  
  const handleLogout = () => {
    localStorage.removeItem('user');
    setShowDropdown(false);
    toast.info("Logged Out Sucessfully",{ autoClose: 500 });
    setTimeout(() => {
      localStorage.removeItem('user');
      navigate('/login');
  }, 500);
  }

  const isLibrarian = user?.role === 'librarian';

  return (
    <div className='nav-container'>
        <div className='nav-content'>
            <NavLink to="/dashboard">Shelwise</NavLink>
            <div className='nav-right'>
              {user ? (
                <div className='profile-menu'>
                  <div className='profile-trigger'
                       onClick={() => setShowDropdown(!showDropdown)}>
                      <span>{user.fullName} <small>({user.role})</small> </span>
                      <i className={`arrow ${showDropdown ? 'up' : 'down'}`}></i>      
                  </div>
                  {/* Dropdown Menu */}
                  {showDropdown && (
                    <div className="dropdown-menu">
                      <NavLink to="/profile" onClick={() => setShowDropdown(false)}>
                        My Profile
                      </NavLink>
                      <button onClick={handleLogout} className="logout-btn">
                        Logout
                      </button>
                    </div>
                  )}
                </div>
              ):(
                <NavLink to="/login" className="login-link">Login</NavLink>
              )}
            </div>
        </div>
        {user && (
          <div className='nav-links'>
            <NavLink to ="/dashboard">Dashboard</NavLink>
            <NavLink to = "/books">Books</NavLink>
            {isLibrarian ? (
              <>
                <NavLink to="/members">Members</NavLink>
                <NavLink to="/librarians">Librarians</NavLink>
              </>
            ):(
              <>
                <NavLink to = "/borrowed">Borrowed Books</NavLink>
                <NavLink to = "/wishlist">Wishlist</NavLink> 
              </>
            )}
          </div>
        )}
    </div>
  )
}

export default Navbar;