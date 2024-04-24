import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

import ParaChain from "./pages/ParaChain/ParaChain";
import RelayChain from "./pages/RelayChain/RelayChain";

import Logo from "./assets/logo.svg?react";
import "./index.css";

const router = createBrowserRouter([
  {
    path: "/",
    element: <ParaChain />,
  },
  {
    path: "/relaychain",
    element: <RelayChain />,
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <div className="app-wrapper">
      <div className="header">
        <Logo />
      </div>
      <div className="app-container">
        <RouterProvider router={router} />
      </div>
    </div>
  </React.StrictMode>
);
