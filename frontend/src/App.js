import React, { useState } from "react";
import "./App.css";

function App() {
  const [inputValue, setInputValue] = useState("");
  const [ticker, setTicker] = useState("");
  const [prediction, setPrediction] = useState(null);
  const [probability, setProbability] = useState(null)
  const [selectedPeriod, setSelectedPeriod] = useState(null);
  const [error, setError] = useState(null);

  const handlePredict = async (finalTicker) => {
    setPrediction(null);
    setProbability(null);
    setError(null);
    try {
      const response = await fetch(`http://localhost:5000/predict?ticker=${finalTicker}`);
      if (response.status === 404) {
        setError("Ticker not found");
        return;
      }
      const data = await response.json();
      if ("Prediction" in data) {
        setTicker(finalTicker);
        setPrediction(data["Prediction"]);
        setProbability(data["Increase_Prob"]);
        setSelectedPeriod("1mo");
      } else {
        setError(data["error"]);
      }
    } catch (err) {
      setError("An error occurred.");
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = inputValue.trim().toUpperCase();
    if (trimmed) {
      handlePredict(trimmed);
    }
  };

  const handlePeriodClick = (period) => {
    setSelectedPeriod(period);
  };

  const chartUrl = selectedPeriod && ticker
    ? `http://localhost:5000/create-chart?ticker=${ticker}&period=${selectedPeriod}`
    : null;

  

  return (
    <div className="App">
      <h1>Stock Direction Predictor</h1>
      <form onSubmit={handleSubmit}>
        <input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Enter stock ticker (e.g., AAPL)"
        />
      </form>

      {prediction != null && (
        <>
          <p>The model predicts that the next closing price will be {" "}
            <span style={{ color: prediction === 1 ? "green" : "red", fontWeight: "bold" }}>
            {prediction === 1 ? "higher" : "lower"} </span>{" "} than the last closing price.</p>
          <p>Probability of Increase: {probability}%</p>

          {chartUrl && (
            <div className="chart-section">
              <img
                src={chartUrl}
                alt="Stock Chart"
                className="chart-image"
                onError={() => setError("Failed to load chart image.")}
              />
            </div>
          )}

          <div style={{ marginTop: "10px" }}>
            {["1wk", "1mo", "6mo", "1y", "5y", "max"].map((period) => (
              <button
                key={period}
                onClick={() => handlePeriodClick(period)}
                style={{ margin: "5px" }}
              >
                {period.toUpperCase()}
              </button>
            ))}
          </div>
        </>
      )}

      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default App;