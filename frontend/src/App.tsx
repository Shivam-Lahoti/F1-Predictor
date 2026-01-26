import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './components/HomePage';
import RaceList from './components/RaceList';
import DriversPage from './components/DriverPage';
import AnalyticsPage from './components/AnalyticsPage';
import './index.css';

function App() {
  return (
    <Router>
      <div className="App min-h-screen">
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/races" element={<RaceList />} />
          <Route path="/drivers" element={<DriversPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
