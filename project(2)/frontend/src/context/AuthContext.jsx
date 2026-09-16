import React, { useState, useCallback } from "react";
import client from "../api/client";
import AuthContext from "./AuthContextValue";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("utap_user");
    return raw ? JSON.parse(raw) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem("utap_token"));

  const login = useCallback(async (email, password) => {
    const res = await client.post("/auth/login", { email, password });
    const { token: t, user: u } = res.data.data;
    localStorage.setItem("utap_token", t);
    localStorage.setItem("utap_user", JSON.stringify(u));
    setToken(t);
    setUser(u);
    return u;
  }, []);

  const register = useCallback(async (payload) => {
    const res = await client.post("/auth/register", payload);
    return res.data.data;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("utap_token");
    localStorage.removeItem("utap_user");
    setToken(null);
    setUser(null);
  }, []);

  const refreshProfile = useCallback(async () => {
    const res = await client.get("/auth/me");
    const u = res.data.data;
    localStorage.setItem("utap_user", JSON.stringify(u));
    setUser(u);
    return u;
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, refreshProfile }}>
      {children}
    </AuthContext.Provider>
  );
}
