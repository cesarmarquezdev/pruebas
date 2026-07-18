import { useState, useEffect } from "react";

function App() {
  const [estado, setEstado] = useState("cargando...");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/health")               // ← hueco 1: la URL completa de tu /health
      .then(r => r.json())
      .then(data => setEstado(data["status"]));  // ← hueco 2: sacar el campo del JSON
  }, []);

  return <h1>Backend: {estado}</h1>;
}

export default App;