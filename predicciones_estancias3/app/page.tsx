"use client";
import { useEffect, useState } from "react";

export default function Home() {
  const [artistas, setArtistas] = useState<string[]>([]);

  const [resultado, setResultado] = useState<number | null>(null);
  const [ocupacion, setOcupacion] = useState<number | null>(null);
  const [veredicto, setVeredicto] = useState<string | null>(null);

  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    artista: "",
    lugar: "",
    capacidad_recinto: "",
    fecha: "",
    precio_minimo: "",
    precio_maximo: "",
    popularidad: "50",
    seguidores: "",
    oyentes_mensuales: "",
    seguidores_ig: "",
    seguidores_fb: "",
  });

  useEffect(() => {
    fetch("http://127.0.0.1:8001/artistas")
      .then((res) => res.json())
      .then((data) => setArtistas(data.artistas))
      .catch((err) => console.error(err));
  }, []);

  const handleChange = (e: any) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    try {
      setError(null);
      setResultado(null);
      setOcupacion(null);
      setVeredicto(null);

      if (!formData.artista) {
        setError("Debes seleccionar un artista.");
        return;
      }

      if (!formData.capacidad_recinto) {
        setError("Debes ingresar la capacidad del recinto.");
        return;
      }

      setLoading(true);

      const precio_promedio =
        (Number(formData.precio_minimo) +
          Number(formData.precio_maximo)) / 2;

      const payload = {
        artista: formData.artista,
        lugar: formData.lugar,
        capacidad_maxima: Number(formData.capacidad_recinto),
        genero_principal: "pop",
        precio_promedio,
        popularidad_spotify: Number(formData.popularidad),
        seguidores_spotify: Number(formData.seguidores),
        oyentes_mensuales: Number(formData.oyentes_mensuales),
        seguidores_ig: Number(formData.seguidores_ig),
      };

      const response = await fetch(
        "https://model-v3-vcc7.onrender.com/api/v1/predict",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        throw new Error("Error en la API");
      }

      const data = await response.json();

      // 🔑 AQUÍ ESTÁ LA CLAVE (JSON REAL)
      const asistencia = Number(data?.prediccion?.asistencia_estimada);
      const ocup = Number(data?.prediccion?.porcentaje_ocupacion);
      const ver = data?.prediccion?.veredicto_comercial;

      if (!Number.isNaN(asistencia)) {
        setResultado(asistencia);
        setOcupacion(!Number.isNaN(ocup) ? ocup : null);
        setVeredicto(ver ?? null);
      } else {
        setError("La API no devolvió una predicción válida.");
      }
    } catch (err) {
      console.error(err);
      setError("Ocurrió un error al hacer la predicción.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-black via-zinc-900 to-purple-950 text-white p-6">
      <div className="w-full max-w-4xl bg-white/5 backdrop-blur-xl rounded-3xl shadow-2xl p-10 space-y-10 animate-fadeIn">

        <h1 className="text-3xl font-bold text-center text-purple-400">
          🔮 Predicción de Asistencia a Eventos
        </h1>

        {/* ===== ARTISTA ===== */}
        <div>
          <h2 className="text-xl font-semibold text-purple-300 mb-6">
            🎤 Detalles del Artista
          </h2>

          <label>Nombre del Artista</label>
          <select
            name="artista"
            value={formData.artista}
            onChange={handleChange}
            className="w-full p-3 mt-1 mb-6 rounded-xl bg-black/40 border border-white/10"
          >
            <option value="">Seleccionar artista</option>
            {artistas.map((artista, index) => (
              <option key={index} value={artista}>
                {artista}
              </option>
            ))}
          </select>

          {/* Slider Popularidad */}
          <div className="mb-8">
            <div className="flex justify-between text-sm text-purple-300 mb-2">
              <span>Popularidad</span>
              <span className="font-bold text-purple-400">
                {formData.popularidad}
              </span>
            </div>

            <input
              type="range"
              name="popularidad"
              min="0"
              max="100"
              value={formData.popularidad}
              onChange={handleChange}
              className="w-full h-2 rounded-lg appearance-none cursor-pointer slider-purple"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label>Seguidores</label>
              <input
                type="number"
                name="seguidores"
                value={formData.seguidores}
                onChange={handleChange}
                className="w-full p-3 rounded-xl bg-black/40 border border-white/10"
              />
            </div>

            <div>
              <label>Oyentes Mensuales</label>
              <input
                type="number"
                name="oyentes_mensuales"
                value={formData.oyentes_mensuales}
                onChange={handleChange}
                className="w-full p-3 rounded-xl bg-black/40 border border-white/10"
              />
            </div>
          </div>
        </div>

        {/* ===== EVENTO ===== */}
        <div>
          <h2 className="text-xl font-semibold text-purple-300 mb-6">
            🏟️ Detalles del Evento
          </h2>

          <label>Nombre del recinto</label>
          <input
            type="text"
            name="lugar"
            value={formData.lugar}
            onChange={handleChange}
            className="w-full p-3 rounded-xl bg-black/40 border border-white/10 mb-6"
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label>Capacidad del recinto</label>
              <input
                type="number"
                name="capacidad_recinto"
                value={formData.capacidad_recinto}
                onChange={handleChange}
                className="w-full p-3 rounded-xl bg-black/40 border border-white/10"
              />
            </div>

            <div>
              <label>Fecha del evento</label>
              <input
                type="date"
                name="fecha"
                value={formData.fecha}
                onChange={handleChange}
                onClick={(e) =>
                  (e.target as HTMLInputElement).showPicker?.()
                }
                className="w-full p-3 rounded-xl bg-black/40 border border-white/10"
              />
            </div>
          </div>
        </div>

        {/* ===== BOLETOS ===== */}
        <div>
          <h2 className="text-xl font-semibold text-purple-300 mb-6">
            🎟️ Boletos y Redes
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label>Precio Mínimo (MXN)</label>
              <input
                type="number"
                name="precio_minimo"
                value={formData.precio_minimo}
                onChange={handleChange}
                className="w-full p-3 rounded-xl bg-black/40 border border-white/10"
              />
            </div>

            <div>
              <label>Precio Máximo (MXN)</label>
              <input
                type="number"
                name="precio_maximo"
                value={formData.precio_maximo}
                onChange={handleChange}
                className="w-full p-3 rounded-xl bg-black/40 border border-white/10"
              />
            </div>

            <div>
              <label>Seguidores de Instagram</label>
              <input
                type="number"
                name="seguidores_ig"
                value={formData.seguidores_ig}
                onChange={handleChange}
                className="w-full p-3 rounded-xl bg-black/40 border border-white/10"
              />
            </div>

            <div>
              <label>Seguidores de Facebook</label>
              <input
                type="number"
                name="seguidores_fb"
                value={formData.seguidores_fb}
                onChange={handleChange}
                className="w-full p-3 rounded-xl bg-black/40 border border-white/10"
              />
            </div>
          </div>
        </div>

        {/* BOTÓN */}
        <button
          type="button"
          disabled={loading}
          onClick={handleSubmit}
          className="w-full py-4 rounded-2xl bg-purple-600 hover:bg-purple-700 transition-all text-lg font-bold shadow-lg shadow-purple-500/40 hover:scale-[1.02] disabled:opacity-50"
        >
          {loading ? "Calculando..." : "Estimar Asistencia"}
        </button>

        {/* RESULTADO */}
        {resultado !== null && (
          <div className="mt-6 p-6 rounded-2xl bg-green-500/10 border border-green-500/30 text-center animate-fadeIn">
            <p className="text-sm uppercase tracking-widest text-green-300 mb-2">
              Asistencia Estimada
            </p>
            <p className="text-4xl font-extrabold text-green-400">
              {resultado.toLocaleString("es-MX")}
            </p>

            {ocupacion !== null && (
              <p className="text-green-200 mt-2">
                Ocupación: {(ocupacion * 100).toFixed(1)}%
              </p>
            )}

            {veredicto && (
              <p className="mt-2 text-xl font-bold text-purple-300">
                {veredicto}
              </p>
            )}
          </div>
        )}

        {error && (
          <div className="text-center text-red-400 mt-4">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}