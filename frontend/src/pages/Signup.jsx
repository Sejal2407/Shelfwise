import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import "../css/signup.css"
import { toast } from 'react-toastify';

function Signup() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    fullName: '',
    memberId: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.password.length < 6) {
    toast.error("Password must be at least 6 characters long");
    return;
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(formData.email)) {
    toast.error("Please enter a valid email address");
    return;
  }
    if (formData.password !== formData.confirmPassword) {
      alert("Passwords do not match!");
      return;
    }
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/signup', formData);
      console.log("Server Response : ",response.data);
      
      localStorage.setItem('user', JSON.stringify(response.data.user));
      toast.success("Register Successfully!");;
      setTimeout(() => {
        navigate('/dashboard');
      },1500);
    }catch(error){
      console.error("Signup Error : ", error);
      const errorMsg = error.response?.data?.error || "Invalid email or password";
      toast.error(errorMsg);
    }
  };

  return (
    <div className='page-wrapper'>
      <div className='login-container signup-container'>
        <form className='login-form' onSubmit={handleSubmit}>
          <h2>Member Registration</h2>
          <p className="subtitle">Join the Library Management System</p>

          <label htmlFor="fullName">Full Name</label>
          <input 
            type='text' id="fullName" name="fullName" 
            placeholder='John Doe' onChange={handleChange} required 
          />

          <label htmlFor="memberId">Library Card / Student ID</label>
          <input 
            type='text' id="memberId" name="memberId" 
            placeholder='LIB-10293' onChange={handleChange} required 
          />

          <label htmlFor="email">Email Address</label>
          <input 
            type='email' id="email" name="email" 
            placeholder='email@university.edu' onChange={handleChange} required 
          />

          <label htmlFor="password">Create Password</label>
          <input 
            type='password' id="password" name="password" 
            placeholder='••••••••' onChange={handleChange} required 
          />

          <label htmlFor="confirmPassword">Confirm Password</label>
          <input 
            type='password' id="confirmPassword" name="confirmPassword" 
            placeholder='••••••••' onChange={handleChange} required 
          />

          <button type="submit" className="login-button">Create Account</button>
          
          <p className="form-footer">
            Already a member? <Link to="/login">Login here</Link>
          </p>
        </form>
      </div>
    </div>
  );
}

export default Signup;