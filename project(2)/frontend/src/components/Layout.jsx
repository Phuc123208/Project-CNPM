import React from "react";
import Sidebar from "./Sidebar";

export default function Layout({ children }) {
  return (
    <div className="page-wrap">
      <Sidebar />
      <div className="main-area">
        <div className="content">{children}</div>
      </div>
    </div>
  );
}
