import React, { useState } from "react";
import UploadVideo from "./components/UploadVideo";
import ClassCreator from "./components/ClassCreator";
import "./styles/training.css";

export default function Training() {
  const [classList, setClassList] = useState(["cat_milo", "plant", "room_kitchen"]);

  const handleAddClass = (newClass) => {
    if (newClass && !classList.includes(newClass)) {
      setClassList([...classList, newClass]);
    }
  };

  return (
    <div className="training-page">
      <h1>🧠 YOLO Custom Trainer</h1>
      <UploadVideo />
      <ClassCreator currentClasses={classList} onAddClass={handleAddClass} />
    </div>
  );
}
