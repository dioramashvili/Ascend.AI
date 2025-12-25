import { useState } from 'react';
import './App.css';

interface Scenario {
  id: string;
  career_title: string;
  scenario_text: string;
  options: string[];
  initial_code?: string;
}

interface Evaluation {
  feedback: string;
  score: number;
  explanation: string;
}

const API_BASE_URL = 'http://localhost:8000/api';

function App() {
  const [careerTitle, setCareerTitle] = useState('');
  const [scenario, setScenario] = useState<Scenario | null>(null);
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [isCodingSimulation, setIsCodingSimulation] = useState(false);
  const [userCode, setUserCode] = useState(''); 

  const handleGenerateScenario = async () => {
    setIsLoading(true);
    setError(null);
    setScenario(null);
    setEvaluation(null);
    setUserCode(''); 

    try {
      const response = await fetch(`${API_BASE_URL}/scenarios/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          career_title: careerTitle, 
          is_coding: isCodingSimulation 
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to generate scenario: ${response.statusText}`);
      }

      const data: Scenario = await response.json();
      setScenario(data);
      
      if (data.initial_code) {
        setUserCode(data.initial_code);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEvaluate = async (answerPayload: string) => {
    if (!scenario) return;

    setIsLoading(true);
    setError(null);

          let fullContext = scenario.scenario_text;
    
    if (isCodingSimulation) {
        fullContext += `\n\nOriginal Buggy Code:\n${scenario.initial_code}`;
    } else {
        fullContext += `\n\nOptions:\n${scenario.options.join('\n')}`;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/evaluations/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          career_title: scenario.career_title,
          scenario_id: scenario.id,
          scenario_text: fullContext, 
          user_answer: answerPayload, 
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
    <div className="app-root">
      <h1>Ascend.AI Career Simulator</h1>
      
      <div className="control-panel">
        <input
          type="text"
          value={careerTitle}
          onChange={(e) => setCareerTitle(e.target.value)}
          placeholder="Enter career title (e.g., Python Developer, Data Scientist)"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !isLoading && careerTitle) {
              handleGenerateScenario();
            }
          }}
        />
        
        <label className="checkbox">
          <input 
            type="checkbox" 
            checked={isCodingSimulation} 
            onChange={(e) => setIsCodingSimulation(e.target.checked)} 
          />
          Coding Mode
        </label>

        <button 
          onClick={handleGenerateScenario} 
          disabled={isLoading || !careerTitle.trim()}
          className="generate-button"
        >
          {isLoading ? 'Generating...' : 'Generate Scenario'}
        </button>
      </div>

      {error && <div className="error-message">⚠️ {error}</div>}

      {scenario && (
        <div className="scenario-container">
          <span className="scenario-title">{scenario.career_title}</span>
          <h2>Scenario Challenge</h2>
          <p>{scenario.scenario_text}</p>
          
          {isCodingSimulation ? (
            <div>
              <h3>Fix the Code:</h3>
              <textarea 
                value={userCode}
                onChange={(e) => setUserCode(e.target.value)}
                className="text-area"
                placeholder="Write your solution here..."
              />
              <button 
                onClick={() => handleEvaluate(userCode)}
                disabled={isLoading || !userCode.trim()}
                className="evaluate-button"
              >
                {isLoading ? 'Evaluating...' : 'Submit Solution'}
              </button>
            </div>
          ) : (
            <div className="options-div">
              <h3>Choose the best action:</h3>
              <div className="options-list">
                {scenario.options.map((option, index) => (
                  <button
                    key={index}
                    onClick={() => handleEvaluate(String.fromCharCode(65 + index))} 
                    disabled={isLoading}
                  >
                    <span style={{ fontWeight: 600, marginRight: '8px' }}>
                      {String.fromCharCode(65 + index)}.
                    </span>
                    {option}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {evaluation && (
        <div className="evaluation-div">
          <h2>Evaluation Result</h2>
          <div className="score">
            {evaluation.score} / 10
          </div>
          <p><strong>Feedback:</strong> {evaluation.feedback}</p>
          <hr />
          <p>{evaluation.explanation}</p>
        </div>
      )}
    </div>
  );
}

export default App;