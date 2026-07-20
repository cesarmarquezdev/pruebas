# Patrones de JS/React en App.jsx

Sacados directo de tu código, con la línea real donde aparecen. Cuando te trabes con algo nuevo, búscalo aquí primero.

---

## 1. Hooks de React

### `useState`
```js
const [notas, setNotas] = useState([]);
```
- Línea 9. Declara una variable de estado (`notas`) y su función para cambiarla (`setNotas`).
- Patrón fijo: `const [valor, setValor] = useState(valorInicial)`.
- **Regla de oro**: nunca cambies `notas` directo (`notas.push(...)`). Siempre usa `setNotas(...)`.

### `useEffect`
```js
useEffect(() => {
  if (token) { ... }
}, [token]);
```
- Línea 13. Corre el código de adentro cuando el componente se pinta por primera vez, y **cada vez que cambia algo en el array `[token]`**.
- Ese array se llama "dependencias". Si estuviera vacío `[]`, correría solo una vez.

---

## 2. Funciones flecha (`=>`)

```js
e => setEmail(e.target.value)
```
- Lo que está a la **izquierda** de `=>` es el/los parámetro(s) que recibe la función. `e` no es un nombre libre, es "el evento que me llega".
- Formas que vas a ver:
  - `e => algo` — un parámetro, sin llaves, retorna `algo` automáticamente.
  - `() => borrarNota(n.id)` — sin parámetros (los `()` vacíos), retorna el resultado automáticamente.
  - `() => { linea1; linea2; }` — con llaves `{}`, para varias líneas. Aquí **no** hay retorno automático, si quieres devolver algo necesitas `return`.

**Por qué se envuelve en flecha dentro de `onClick`**: `onClick={funcion()}` ejecuta `funcion` YA, al pintar la página. `onClick={() => funcion()}` la deja lista para ejecutarse solo cuando haya click.

---

## 3. Template literals (comillas invertidas \`)

```js
`/notas/${id}`
```
- Línea 32. Con backticks \` puedes meter variables dentro de un string usando `${variable}`.
- Diferente de `"texto normal"` (comillas dobles/simples), donde `${id}` sería texto literal, no se evalúa.

---

## 4. Arrays: `.map()` y `.filter()`

### `.map()` — transforma cada elemento
```js
notas.map(n => <li key={n.id}>...</li>)
```
- Línea 73. Recorre `notas` y devuelve un **array nuevo** con cada elemento transformado (aquí, convertido en un `<li>`).
- `n` es cada nota individual en cada vuelta del recorrido — mismo concepto que el parámetro de una flecha.
- `key={n.id}` es obligatorio en React cuando pintas listas con `.map`, para que identifique cada elemento.

### `.filter()` — decide qué se queda
```js
notas.filter(n => n.id !== id)
```
- Línea 34. Recorre `notas` y devuelve un array nuevo **solo con los elementos donde la condición da `true`**.
- Aquí: "quédate con las notas cuyo id sea distinto al que quiero borrar" = todas menos esa.
- Distinto de `.map()`: `.filter()` no transforma, solo incluye o excluye.

---

## 5. Fetch y promesas (`.then()`)

```js
fetch(url, {...}).then(r => r.json()).then(data => { ... })
```
- `fetch(...)` hace la petición y devuelve una "promesa" (algo que se resuelve más adelante).
- Cada `.then()` se ejecuta cuando lo anterior termina, y recibe el resultado como parámetro.
- `r` = la respuesta cruda del servidor (status, headers...). `r.json()` = convierte el body a un objeto JS (y es asíncrono también, por eso necesita su propio `.then`).
- Si `r.json()` intenta parsear una respuesta **vacía** (como un DELETE con status 204), truena. Por eso a veces hay que chequear `r.status` antes de llamar `r.json()`.

---

## 6. Spread operator (`...`)

```js
setNotas([...notas, data]);
```
- Línea 25. `...notas` "desempaqueta" todos los elementos del array viejo dentro de uno nuevo. El resultado es un array nuevo con todo lo de antes + `data` al final.
- Por qué no `notas.push(data)`: en React nunca mutas el estado directo, siempre creas una copia nueva y se la pasas a `setX`.

---

## 7. Parámetros por defecto

```js
function api(ruta, metodo = "GET", body = null) { ... }
```
- Línea 86. Si no le pasas `metodo` o `body` al llamar `api(...)`, usan el valor por defecto (`"GET"` y `null`).

---

## 8. Operador ternario (`? :`)

```js
modo === "login" ? "Crear cuenta" : "Ya tengo cuenta"
```
- Línea 107. Atajo de `if/else` en una sola línea, útil dentro de JSX (donde no puedes escribir un `if` normal entre llaves).
- Forma: `condición ? valorSiTrue : valorSiFalse`.

---

## 9. JSX: atributos van dentro de la etiqueta

```jsx
<button onClick={...}>Texto</button>
```
- El atributo (`onClick`, `value`, `key`, etc.) **siempre va antes** del `>` que cierra la etiqueta de apertura.
- Una vez que escribes `>`, la etiqueta ya "cerró para atributos" — todo lo que sigue es contenido (texto, otros elementos), no más atributos.
- Expresiones JS dentro del JSX van entre llaves `{ }` (por ejemplo `{n.titulo}`, `{modo === "login" ? ... : ...}`).

---

## 10. Comparación de igualdad: `!==` / `===`

```js
n.id !== id
```
- Usa siempre `===` / `!==` (con 3 signos), no `==`/`!=`. Los de 3 signos comparan también el tipo (un `number` nunca es igual a un `string` aunque "se parezcan"), evitando bugs raros.

---

## Pendiente de resolver en tu código actual
- `borrarNota` (línea 33): el `if (___)` sigue sin llenar — falta decidir la condición ahora que sabes que el DELETE responde 204 (sin body).
- `api()` (línea 94-100): falta el chequeo de `r.status === 204` antes de `r.json()`, para no tronar en respuestas sin contenido.
