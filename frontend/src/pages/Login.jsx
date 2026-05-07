import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import "../css/login.css";
import API_URL from '../api';

function Login() {
  const navigate = useNavigate();
  
  // 1. State now explicitly uses 'email'
  const [credentials, setCredentials] = useState({ 
    email: '', 
    password: '' 
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setCredentials(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // 2. Sending { email, password } to Flask
      const response = await axios.post(`${API_URL}/api/login`, credentials);
      
      console.log("Login Success:", response.data);
      
      // 3. Save session and Notify
      localStorage.setItem('user', JSON.stringify(response.data.user));
      toast.success(`Welcome Back, ${response.data.user.fullName}!`);
      
      setTimeout(() => {
        navigate('/dashboard');
      }, 1500);
      
    } catch (error) {
      console.error("Login Error:", error);
      const errorMsg = error.response?.data?.error || "Invalid email or password";
      toast.error(errorMsg);
    }
  };

  return (
    <div className='page-wrapper'>
      <div className='login-container'>
        <form className='login-form' onSubmit={handleSubmit}>
          <h2>Login</h2>
          
          <label htmlFor="email">Email Address</label>
          <input 
            type='email' 
            id="email"
            name="email" // MUST match state key
            placeholder='Enter your email' 
            value={credentials.email}
            onChange={handleChange}
            required
          />

          <label htmlFor="password">Password</label>
          <input 
            type='password' 
            id="password"
            name="password" // MUST match state key
            placeholder='Enter your password' 
            value={credentials.password}
            onChange={handleChange}
            required
          />

          <button type="submit" className="login-button">Sign In</button>
        </form>
        
        <p className="form-footer">
           Don't have an account? <Link to="/signup">Signup here</Link>
        </p>
      </div>
    </div>
  );
}

export default Login;
