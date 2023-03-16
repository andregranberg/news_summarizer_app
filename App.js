import { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [articles, setArticles] = useState([]);
  const [selected, setSelected] = useState({});
  const [summaries, setSummaries] = useState([]);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/api/articles')
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        setArticles(data);
      })
      .catch((error) => {
        console.error('Error fetching articles:', error);
      });
  }, []);

  const handleCheckboxChange = (index) => {
    setSelected((prevState) => ({
      ...prevState,
      [index]: !prevState[index],
    }));
  };

  const handleSubmit = () => {
    const selectedArticles = articles.filter((_, index) => selected[index]);
    fetch('http://127.0.0.1:5000/api/summarize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(selectedArticles),
    })
      .then((response) => response.json())
      .then((data) => setSummaries(data));
  };

  return (
    <div className="App">
      {/* ... */}
      <div className="articles">
        <h2>Articles</h2>
        {articles.map((article, index) => (
          <div key={index} className="article">
            <label>
              <input
                type="checkbox"
                checked={selected[index] || false}
                onChange={() => handleCheckboxChange(index)}
              />
              {article.title}
            </label>
          </div>
        ))}
        <button onClick={handleSubmit}>Done</button>
      </div>
      <div className="summaries">
        <h2>Summaries</h2>
        {summaries && summaries.length > 0 ? (
          summaries.map((summary, index) => (
            <div key={index} className="summary">
              <h3>{summary.title}</h3>
              <p>{summary.summary}</p>
            </div>
          ))
        ) : (
          <p>No summaries available.</p>
        )}
      </div>
    </div>
  );
}

export default App;
