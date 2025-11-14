import { useState } from "react";

export default function Textbox() {
  const [name, setName] = useState(""); // state to store input value

  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4">
      <input
        type="text"
        placeholder="Enter your name"
        className="border border-gray-300 rounded p-2"
        value={name} // bind state
        onChange={(e) => setName(e.target.value)} // update state on typing
      />
      <p>Your name is: {name}</p>
    </div>
  );
}