import React, { useEffect, useState } from 'react';

function App() {
  const [df_opm, setDf_opm] = useState([]);
  const [selectedValue, setSelectedValue] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/df_opm")
      .then((response) => response.json())
      .then((df_opm) => setDf_opm(df_opm))
      .catch((error) => console.log("Error: No se puede cargar los datos", error));
  }, []);

  const handleSelectChange = (event) => {
    setSelectedValue(event.target.value);
  };

  const uniqueValues = [...new Set(df_opm.map((row) => row["O.P. Número"]))];

  const filteredData = selectedValue
    ? df_opm.filter((row) => row["O.P. Número"] === selectedValue)
    : df_opm;

  return (
    <div className="App">
      <h1>Prueba de conexión</h1>
      {df_opm.length > 0 ? (
        <div>
          <label htmlFor="op_number">Selecciona un número de O.P.</label>
          <select id="op_number" value={selectedValue} onChange={handleSelectChange}>
            <option value="">Seleccione una opción</option>
            {uniqueValues.map((value, index) => (
              <option key={index} value={value}>
                {value}
              </option>
            ))}
          </select>
          <table>
            <thead>
              <tr>
                {Object.keys(df_opm[0]).map((key) => (
                  <th key={key}>{key}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredData.map((row, index) => (
                <tr key={index}>
                  {Object.keys(row).map((key) => (
                    <td key={key}>{row[key]}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <h2>Cargando...</h2>
      )}
    </div>
  );
}

export default App;
