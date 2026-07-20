import { useState } from "react";
import { useEffect } from "react";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [modo, setModo] = useState("login");
  const [notas, setNotas] = useState([]);
  const [nuevoTitulo, setNuevoTitulo] = useState("");
  const [nuevaNota, setNuevaNota] = useState("");

  useEffect(() => {
    if (token) {
      api("/notas").then(data => {
        if (data) setNotas(data);
      });
    }

  }, [token]);

  function crearNota(e) {
    e.preventDefault();
    api("/notas", "POST", { titulo: nuevoTitulo, nota: nuevaNota }).then(data => {
      if (data) {
        setNotas([...notas, data]);   // agrega la nueva a la lista existente
        setNuevoTitulo("");
        setNuevaNota("");
      }
    });
  }
  function borrarNota(id) {
    api(`/notas/${id}`, "DELETE").then(data => {
      if (data) {
        setNotas(notas.filter(n => n.id !== id));
      }
    });
  }

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
      <ul>
        {notas.map(n => <li key={n.id}>{n.titulo + " — " + n.modification_date}
          <button onClick={() => borrarNota(n.id)}>Borrar</button>
        </li>)}
      </ul>
      <form onSubmit={crearNota}>
        <input value={nuevoTitulo} onChange={e => setNuevoTitulo(e.target.value)} placeholder="título" />
        <input value={nuevaNota} onChange={e => setNuevaNota(e.target.value)} placeholder="nota" />
        <button>Crear</button>
      </form>


    </div>
  )
  function api(ruta, metodo = "GET", body = null) {
    return fetch("http://127.0.0.1:8000" + ruta, {
      method: metodo,
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token
      },
      body: body ? JSON.stringify(body) : null,
    }).then(r => {
      if (r.status === 401) {
        localStorage.removeItem("token");
        setToken(null);
        return null;
      }
      if (r.status === 204) {
        return true;
      }
      return r.json();
    })
  }
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