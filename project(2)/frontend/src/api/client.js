import axios from "axios";

// Base URL of the Flask REST API. Configurable via VITE_API_URL for
// deployment; defaults to local dev server on port 9999.
const baseURL = import.meta.env.VITE_API_URL || "http://localhost:9999/api";

const client = axios.create({ baseURL });

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("utap_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response && err.response.status === 401) {
      localStorage.removeItem("utap_token");
      localStorage.removeItem("utap_user");
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

export default client;
