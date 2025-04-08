// Pages/Home.jsx
import Joystick from '../Components/Joystick/Joystick';
import CameraJoystick from '../Components/Joystick/CameraJoystick';
import VideoFeed from '../Components/Camera/VideoFeed';
import '../App.css'; // Adjust the path as necessary

export default function Home() {
  return (
    <div className="robot-ui">
      <Joystick />
      <VideoFeed />
      <CameraJoystick />
    </div>
  );
}
