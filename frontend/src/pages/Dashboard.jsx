import React, { useEffect, useState } from 'react'
import "../css/dashboard.css"
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { AlertTriangle, Clock, BookOpen, Users, BookMarked, RotateCcw } from 'lucide-react';
import API_URL from '../api';

function Dashboard() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user'));
  const isLibrarian = user?.role === 'librarian';

  const [stats, setStats] = useState({
    totalBorrowed: 0,
    returnedThisMonth: 0,
    totalFine: 0
  });
  const [libStats, setLibStats] = useState({
    totalBooks: 0,
    totalMembers: 0,
    totalBorrowed: 0,
    totalReturned: 0
  });
  const [alerts, setAlerts] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) { navigate('/login'); return; }
    if (isLibrarian) {
      fetchLibrarianDashboard();
    } else {
      fetchDashboard();
    }
  }, []);

  const fetchDashboard = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/dashboard`, {
        params: { userId: user.email }
      });
      const data = response.data;
      setStats({
        totalBorrowed: data.totalBorrowed,
        returnedThisMonth: data.returnedThisMonth,
        totalFine: data.totalFine
      });
      setAlerts(data.alerts);
      setRecentActivity(data.recentActivity);
    } catch (error) {
      console.error("Dashboard fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLibrarianDashboard = async () => {
    try {
      const [booksRes, membersRes, borrowedRes] = await Promise.all([
        axios.get(`${API_URL}/api/books`),
        axios.get(`${API_URL}/api/members`),
        axios.get(`${API_URL}/api/librarian-dashboard`)
      ]);
      setLibStats({
        totalBooks: booksRes.data.length,
        totalMembers: membersRes.data.length,
        totalBorrowed: borrowedRes.data.totalBorrowed,
        totalReturned: borrowedRes.data.totalReturned
      });
      setRecentActivity(borrowedRes.data.recentActivity);
    } catch (error) {
      console.error("Librarian dashboard error:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr || dateStr === "—") return "—";
    const date = new Date(dateStr);
    const day = date.getDate();
    const month = date.toLocaleString('default', { month: 'long' });
    const year = date.getFullYear();
    const suffix =
      day % 10 === 1 && day !== 11 ? 'st' :
      day % 10 === 2 && day !== 12 ? 'nd' :
      day % 10 === 3 && day !== 13 ? 'rd' : 'th';
    return `${day}${suffix} ${month} ${year}`;
  };

  return (
    <div className='dashboard-section'>
      <div className='dashboard-header'>
        <div>
          <h2>Welcome, {user?.fullName}!</h2>
          <p>{isLibrarian ? "Here's your library overview" : "Here's your library activity at a glance"}</p>
        </div>
      </div>

      {/* Stat Cards */}
      {isLibrarian ? (
        <div className='stat-card'>
          <div className='stat-item'>
            <BookOpen size={28} className='stat-icon' />
            <p className='stat-label'>Total Books</p>
            <p className='stat-value'>{libStats.totalBooks}</p>
          </div>
          <div className='stat-item'>
            <Users size={28} className='stat-icon' />
            <p className='stat-label'>Total Members</p>
            <p className='stat-value'>{libStats.totalMembers}</p>
          </div>
          <div className='stat-item'>
            <BookMarked size={28} className='stat-icon' />
            <p className='stat-label'>Currently Borrowed</p>
            <p className='stat-value'>{libStats.totalBorrowed}</p>
          </div>
          <div className='stat-item'>
            <RotateCcw size={28} className='stat-icon' />
            <p className='stat-label'>Total Returned</p>
            <p className='stat-value'>{libStats.totalReturned}</p>
          </div>
        </div>
      ) : (
        <div className='stat-card'>
          <div className='stat-item'>
            <p className='stat-label'>Total Books Borrowed</p>
            <p className='stat-value'>{stats.totalBorrowed}</p>
          </div>
          <div className='stat-item'>
            <p className='stat-label'>Returned This Month</p>
            <p className='stat-value'>{stats.returnedThisMonth}</p>
          </div>
          <div className='stat-item'>
            <p className='stat-label'>Pending Fines</p>
            <p className='stat-value' style={{ color: stats.totalFine > 0 ? '#e74c3c' : '#2ecc71' }}>
              ₹{stats.totalFine}
            </p>
          </div>
        </div>
      )}

      {/* Alert Box — only for members */}
      {!isLibrarian && alerts.length > 0 && (
        <div className='alert-box'>
          <p className='alert-heading'>⚠️ Alerts</p>
          {alerts.map((alert, index) => (
            <div key={index} className={`alert-item alert-${alert.type}`}>
              {alert.type === 'overdue' ? (
                <AlertTriangle size={16} className='alert-icon' />
              ) : (
                <Clock size={16} className='alert-icon' />
              )}
              <span>{alert.message}</span>
            </div>
          ))}
        </div>
      )}

      {/* Recent Activity */}
      <div className='recent'>
        <h3>{isLibrarian ? "Recent Borrowing Activity (All Members)" : "My Recent Activity"}</h3>
        {loading ? (
          <p style={{ color: '#aaa' }}>Loading...</p>
        ) : recentActivity.length === 0 ? (
          <p style={{ color: '#aaa' }}>No recent activity found.</p>
        ) : (
          <div className='activity-table-wrapper'>
            <table className='activity-table'>
              <thead>
                <tr>
                  <th>Type</th>
                  {isLibrarian && <th>Member</th>}
                  <th>Book Name</th>
                  <th>Author</th>
                  <th>Publisher</th>
                  <th>Date of Activity</th>
                </tr>
              </thead>
              <tbody>
                {recentActivity.map((activity, index) => (
                  <tr key={index}>
                    <td>
                      <span className={`badge badge-${activity.type.toLowerCase()}`}>
                        {activity.type}
                      </span>
                    </td>
                    {isLibrarian && <td>{activity.memberName || '—'}</td>}
                    <td>{activity.bookName}</td>
                    <td>{activity.author}</td>
                    <td>{activity.publisher}</td>
                    <td>{formatDate(activity.date)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
