import { useState } from "react";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [modo, setModo] = useState("login");

  function handleSubmit(e) {
    e.preventDefault();

    // Aquí el condicional de la URL está perfecto
    fetch(modo === "login" ? "http://127.0.0.1:8000/auth/login" : "http://127.0.0.1:8000/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        "email": email,
        "password": password
      }),
    })
      .then(r => r.json())
      .then(data => {
        // 1. Si estamos en modo login, guardamos el token
        if (modo === "login") {
          localStorage.setItem("token", data["access_token"]);
          setToken(data["access_token"]);
        }
        // 2. Si venimos de un registro exitoso, cambiamos el modo a login
        else {
          alert("¡Registro exitoso! Ahora inicia sesión.");
          setModo("login");
        }
      });
  }

  if (token) return (
    <div>
      <h1>Estás logueado ✅</h1>
      <button onClick={() => {
        localStorage.removeItem("token");
        setToken(null);
      }}>Cerrar sesión</button>
    </div>
  )
  return (
    <form onSubmit={handleSubmit}>
      {/* Tu botón de cambiar modo que está perfecto */}
      <button type="button" onClick={() => setModo(modo === "login" ? "registro" : "login")}>
        {modo === "login" ? "Crear cuenta" : "Ya tengo cuenta"}
      </button>

      <input value={email} onChange={e => setEmail(e.target.value)} placeholder="email" />
      <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="contraseña" />

      {/* Cambiamos dinámicamente el texto del botón de envío */}
      <button>{modo === "login" ? "Entrar" : "Registrarme"}</button>
    </form>
  );
}

export default App;