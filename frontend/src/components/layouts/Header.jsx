import React from "react";
import { Link } from "react-router-dom";
import logo from "../../assets/Iconos/Logo.png";

const Header = () => {
  return (
    <header className="w-full bg-gray-200 text-gray-900 shadow-md">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center space-x-3">
          <img
            src={logo}
            alt="American Tactical Logo"
            className="h-12 w-auto object-contain"
          />
        </Link>

        <div className="text-base sm:text-lg font-semibold tracking-wide text-gray-900">
          Data Analytics Agent
        </div>
      </div>
    </header>
  );
};

export default Header;
