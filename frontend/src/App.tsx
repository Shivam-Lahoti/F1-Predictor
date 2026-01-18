import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './components/HomePage';
import RaceList from './components/RaceList';
import './index.css';

function App() {
  return (
    <Router>
      <div className="App min-h-screen">
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/races" element={<RaceList />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;