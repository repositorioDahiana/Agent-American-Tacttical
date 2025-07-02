import React from "react";
import { Link } from "react-router-dom";

const Home = () => {
  return (
    <>
      <main className="flex flex-col items-center justify-center min-h-[calc(100vh-80px)] px-6 py-12 bg-gray-50 text-gray-800">
        <h1 className="text-3xl font-bold mb-2 text-center">American Tactical</h1>
        <h2 className="text-xl text-gray-600 mb-6 text-center">Data Analytics Agent</h2>

        <p className="text-center max-w-2xl text-base leading-relaxed mb-4">
          Welcome to the American Tactical Intelligence Agent.
        </p>
        <p className="text-center max-w-3xl text-sm text-gray-700 mb-4">
          This system combines a predictive model and a conversational AI agent to support data-driven decision making.
          It analyzes import trends, forecasts future demand, and helps you answer natural language questions about your product strategy.
        </p>
        <p className="text-center max-w-3xl text-sm text-gray-700 mb-8">
          Ask the agent about product stock, rotation rates, ideal import timing, and more. It interprets the data and gives you actionable insights.
        </p>

        <Link to="/dashboard">
          <button className="bg-gray-800 text-white px-6 py-3 rounded-lg shadow hover:bg-gray-700 transition">
            Start Exploring
          </button>
        </Link>
      </main>
    </>
  );
};

export default Home;
