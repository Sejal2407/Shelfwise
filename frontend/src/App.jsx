import React from 'react'
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import Navbar from './components/navbar'
import Dashboard from './pages/Dashboard'
import Books from './pages/Books'
import BorrowedBooks from './pages/BorrowedBooks'
import Wishlist from './pages/Wishlist'
import Login from './pages/Login'
import "./App.css";
import Profile from './pages/Profile'
import Signup from './pages/Signup'
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Members from './pages/Members'
import Librarian from './pages/Librarian'

// 1. Create a wrapper component to handle Navbar visibility
function NavigationHandler() {
  const location = useLocation();
  
  if (location.pathname === '/login' || location.pathname === '/signup') {
    return null;
  }
  
  return <Navbar />;
}

function App() {
  return (
    <BrowserRouter>
    <ToastContainer 
        position="top-right"
        autoClose={1500}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="dark"
      />
     
      <NavigationHandler />
      
      <div className="main">
        <Routes>
          <Route path='/' element={<Navigate to ="/dashboard" />} />
          <Route path='/dashboard' element={<Dashboard/>}/>
          <Route path='/books' element={<Books/>} />
          <Route path='/borrowed' element={<BorrowedBooks/>}/>
          <Route path='/wishlist' element={<Wishlist/>}/>
          <Route path='/login' element={<Login/>}/>
          <Route path='/signup' element={<Signup/>}/>
          <Route path='/profile' element={<Profile/>}/>
          <Route path='/members' element={<Members/>}/>
          <Route path='/librarians' element={<Librarian/>}/>
        </Routes>
      </div>
    </BrowserRouter> 
  );
}

export default App;