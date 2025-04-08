// App.jsx
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './Pages/Home';
import Editor from './Pages/FloorMapping';

export default function App() {
  return (
    <Router>
      <nav className="p-4 flex gap-4 bg-gray-200">
        <Link to="/">Home</Link>
        <Link to="/editor">Editor</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/editor" element={<Editor />} />
      </Routes>
    </Router>
  );
}
