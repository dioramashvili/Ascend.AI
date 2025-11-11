import { useState } from 'react';
import './App.css';

interface Scenario {
  id: string;
  career_title: string;
  scenario_text: string;
  options: string[];
}

interface Evaluation {
  feedback: string;
  score: number;
  explanation: string;
}

const API_BASE_URL = 'http://localhost:8000/api';

function App() {
  const [careerTitle, setCareerTitle] = useState('software engineer');
  const [scenario, setScenario] = useState<Scenario | null>(null);
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);


  const handleGenerateScenario = async () => {
    setIsLoading(true);
    setError(null);
    setScenario(null); 
    setEvaluation(null); 

    try {
      const response = await fetch(`${API_BASE_URL}/scenarios/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ career_title: careerTitle }),
      });

      if (!response.ok) {
        throw new Error(`Failed to generate scenario: ${response.statusText}`);
      }

      const data: Scenario = await response.json();
      setScenario(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEvaluateAnswer = async (answer: string) => {
    if (!scenario) return; // Should not happen if buttons are visible

    setIsLoading(true);
    setError(null);

    // The backend expects 'A', 'B', or 'C'
    const selectedOptionLetter = answer.charAt(0);

    try {
      const response = await fetch(`${API_BASE_URL}/evaluations/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          career_title: scenario.career_title,
          scenario_id: scenario.id,
          scenario_text: scenario.scenario_text,
          user_answer: selectedOptionLetter,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`Evaluation failed: ${errorData.detail || response.statusText}`);
      }
      
      const data: Evaluation = await response.json();
      setEvaluation(data);

    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };



  return (
    <div style={{ fontFamily: 'sans-serif', maxWidth: '800px', margin: 'auto', padding: '20px' }}>
      <h1>CareerSim Backend Test</h1>
      
    
      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          value={careerTitle}
          onChange={(e) => setCareerTitle(e.target.value)}
          placeholder="Enter a career title"
          style={{ padding: '8px', marginRight: '10px' }}
        />
        <button onClick={handleGenerateScenario} disabled={isLoading}>
          Generate Scenario
        </button>
      </div>

      {isLoading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}

      {scenario && (
        <div style={{ border: '1px solid #ccc', padding: '15px', marginBottom: '20px' }}>
          <h2>Scenario: {scenario.career_title}</h2>
          <p>{scenario.scenario_text}</p>
          <h3>Options:</h3>
          <div>
            {scenario.options.map((option) => (
              <button
                key={option}
                onClick={() => handleEvaluateAnswer(option)}
                disabled={isLoading}
                style={{ margin: '5px' }}
              >
                {option}
              </button>
            ))}
          </div>
        </div>
      )}
      {evaluation && (
         <div style={{ border: '1px solid #0c0', padding: '15px', backgroundColor: '#f0fff0' }}>
           <h2>Evaluation Result</h2>
           <p><strong>Feedback:</strong> {evaluation.feedback}</p>
           <p><strong>Score:</strong> {evaluation.score} / 10</p>
           <p><strong>Explanation:</strong> {evaluation.explanation}</p>
         </div>
      )}
    </div>
  );
}

export default App;