// Pages/Home.jsx
import CameraJoystick from '../Components/Joystick/CameraJoystick';
import JoystickToggle from '../Components/Joystick/JoystickToggle';
import VideoFeed from '../Components/Camera/VideoFeed';
import CatToyController from '../Components/Joystick/CatToyController';
import '../App.css'; // Adjust the path as necessary


export default function Home() {
  return (
    
    <div className="robot-ui">
         
      
      <JoystickToggle />
      <div className="center-column">
      <VideoFeed />
      <CatToyController />
      </div>
      <CameraJoystick />
    </div>
    
  );
}
