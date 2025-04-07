import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import Joystick from './Components/Joystick/Joystick'
import CameraJoystick from './Components/Joystick/CameraJoystick'
import VideoFeed from './Components/Camera/VideoFeed'

function App() {
  

  return (
    <div className='robot-ui'>
	<Joystick />
  <VideoFeed />
  <CameraJoystick />
    </ div>
  )
}

export default App
