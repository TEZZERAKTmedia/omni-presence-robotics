// App.jsx
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './Pages/Home';
import Editor from './Pages/FloorMapping';
import Navbar from './Components/Navbar/Navbar'
import MappingPage from './Pages/Mapping/Mapping.jsx';
import Training from './Pages/Yolo/Training';


export default function App() {
  return (
    <Router>
      
      
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/editor" element={<Editor />} />
        <Route path="/mapping" element={<MappingPage/>} />
        <Route path="/training" element={<Training/>} />
      </Routes>
    </Router>
  );
}
