import React, { useState } from "react";

const suggestions = [
  "cat_luna", "cat_tree", "plant", "room_kitchen", "room_living", "robot_dock"
];

export default function ClassCreator({ currentClasses, onAddClass }) {
  const [input, setInput] = useState("");

  const handleSubmit = () => {
    if (input.trim() !== "") {
      onAddClass(input.trim());
      setInput("");
    }
  };

  return (
    <div className="class-creator">
      <h3>🏷️ Define Your Classes</h3>
      <input
        type="text"
        placeholder="e.g. cat_milo"
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      <button onClick={handleSubmit}>Add</button>

      <div className="suggestions">
        <p>Suggestions:</p>
        {suggestions.map((item, i) => (
          <button key={i} onClick={() => onAddClass(item)}>{item}</button>
        ))}
      </div>

      <div className="current-classes">
        <h4>Current Classes:</h4>
        <ul>
          {currentClasses.map((cls, idx) => (
            <li key={idx}>{idx}: {cls}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
