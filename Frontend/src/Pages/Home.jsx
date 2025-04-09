// Pages/Home.jsx
import CameraJoystick from '../Components/Joystick/CameraJoystick';
import JoystickToggle from '../Components/Joystick/JoystickToggle';
import VideoFeed from '../Components/Camera/VideoFeed';
import '../App.css'; // Adjust the path as necessary

export default function Home() {
  return (
    <>
      <VideoFeed />
    <div className="robot-ui">
      
      <JoystickToggle />
      
      <CameraJoystick />
    </div>
    </>
  );
}
