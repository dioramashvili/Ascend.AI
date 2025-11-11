const API_BASE_URL = 'http://localhost:8000';

export const generateScenario = async (careerTitle: string) => {
  const response = await fetch(`${API_BASE_URL}/api/v1/simulations/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ career_title: careerTitle }),
  });
  if (!response.ok) {
    throw new Error('Failed to fetch scenario');
  }
  return response.json();
};