import { useState } from "react";
import { useEffect } from "react";
import ReactMarkdown from "react-markdown";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [modo, setModo] = useState("login");
  const [notas, setNotas] = useState([]);
  const [nuevoTitulo, setNuevoTitulo] = useState("");
  const [nuevaNota, setNuevaNota] = useState("");
  const [editarTitulo, setEditarTitulo] = useState("");
  const [editarNota, setEditarNota] = useState("");
  const [editarNotaid, setEditarNotaid] = useState("");
  const [vistaNota, setVistaNota] = useState("")
  useEffect(() => {
    if (token) {
      api("/notas").then(data => {
        if (data) setNotas(data);
      });
    }

  }, [token]);

  function verNota(id) {
    api(`/notas/${id}`).then(data => {
      if (data) {
        setVistaNota(data)
          ;
      }
    });
  }
  function empezarEditar(nota) {
    setEditarNotaid(nota.id);
    setEditarTitulo(nota.titulo);
    setEditarNota(nota.nota);
  }


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
  function guardarEdicion(e) {
    e.preventDefault();
    api(`/notas/${editarNotaid}`, "PATCH", { titulo: editarTitulo, nota: editarNota }).then(data => {
      if (data) {
        setNotas(notas.map(n => n.id === editarNotaid ? data : n));
        setEditarNotaid("");
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

  const inputClass =
    "flex-1 px-3 py-2 rounded-lg border border-[var(--border)] bg-transparent " +
    "focus:outline-none focus:border-[var(--accent)] transition-colors";
  const btnGhostClass =
    "text-sm px-3 py-1.5 rounded-lg border border-[var(--border)] " +
    "hover:bg-[var(--accent-bg)] transition-colors";
  const btnPrimaryClass =
    "px-4 py-2 rounded-lg bg-[var(--accent)] text-white font-medium " +
    "hover:opacity-90 transition-opacity";

  if (token) return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)] p-6">
      <div className="max-w-2xl mx-auto flex flex-col gap-6">
        <div className="flex justify-between items-center">
          <h1 className="text-xl font-medium text-[var(--text-h)]">Estás logueado ✅</h1>
          <button className={btnGhostClass} onClick={() => {
            localStorage.removeItem("token");
            setToken(null);
          }}>Cerrar sesión</button>
        </div>

        <ul className="flex flex-col gap-2">
          {notas.map(n => (
            <li key={n.id} className="p-3 rounded-lg border border-[var(--border)]">
              {n.id === editarNotaid ? (
                <form onSubmit={guardarEdicion} className="flex flex-col sm:flex-row gap-2">
                  <input className={inputClass} value={editarTitulo} onChange={e => setEditarTitulo(e.target.value)} />
                  <input className={inputClass} value={editarNota} onChange={e => setEditarNota(e.target.value)} />
                  <button className={btnPrimaryClass}>Guardar</button>
                </form>
              ) : (
                <div className="flex justify-between items-center gap-3 flex-wrap">
                  <span
                    onClick={() => verNota(n.id)}
                    className="cursor-pointer hover:text-[var(--accent)] transition-colors truncate"
                  >
                    {n.titulo + " — " + n.modification_date}
                  </span>
                  <div className="flex gap-2 shrink-0">
                    <button className={btnGhostClass} onClick={() => empezarEditar(n)}>Editar</button>
                    <button className={btnGhostClass} onClick={() => borrarNota(n.id)}>Borrar</button>
                  </div>
                </div>
              )}
            </li>
          ))}
        </ul>

        {vistaNota && (
          <div className="p-4 rounded-lg border border-[var(--border)] bg-[var(--code-bg)] flex flex-col gap-3 text-left">
            <h2 className="text-lg font-medium text-[var(--text-h)]">{vistaNota.titulo}</h2>
            <ReactMarkdown>{vistaNota.nota}</ReactMarkdown>
            <button className={btnGhostClass + " self-start"} onClick={() => setVistaNota("")}>Cerrar</button>
          </div>
        )}

        <form onSubmit={crearNota} className="flex flex-col sm:flex-row gap-2">
          <input className={inputClass} value={nuevoTitulo} onChange={e => setNuevoTitulo(e.target.value)} placeholder="título" />
          <input className={inputClass} value={nuevaNota} onChange={e => setNuevaNota(e.target.value)} placeholder="nota" />
          <button className={btnPrimaryClass}>Crear</button>
        </form>
      </div>
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
    <div className="min-h-screen flex items-center justify-center bg-[var(--bg)] text-[var(--text)] p-6">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm flex flex-col gap-4 p-8 rounded-xl border border-[var(--border)] shadow-[var(--shadow)]"
      >
        <div className="flex justify-between items-center">
          <h1 className="text-xl font-medium text-[var(--text-h)]">Notas</h1>
          {/* Tu botón de cambiar modo que está perfecto */}
          <button
            type="button"
            onClick={() => setModo(modo === "login" ? "registro" : "login")}
            className="text-sm text-[var(--accent)] hover:underline"
          >
            {modo === "login" ? "Crear cuenta" : "Ya tengo cuenta"}
          </button>
        </div>

        <input
          value={email}
          onChange={e => setEmail(e.target.value)}
          placeholder="email"
          className="px-3 py-2 rounded-lg border border-[var(--border)] bg-transparent focus:outline-none focus:border-[var(--accent)] transition-colors"
        />
        <input
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          placeholder="contraseña"
          className="px-3 py-2 rounded-lg border border-[var(--border)] bg-transparent focus:outline-none focus:border-[var(--accent)] transition-colors"
        />

        {/* Cambiamos dinámicamente el texto del botón de envío */}
        <button className="px-4 py-2 rounded-lg bg-[var(--accent)] text-white font-medium hover:opacity-90 transition-opacity">
          {modo === "login" ? "Entrar" : "Registrarme"}
        </button>
      </form>
    </div>
  );
}

export default App;