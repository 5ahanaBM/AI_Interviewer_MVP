import axios from "axios";

const BASE_URL = "http://localhost:8000"; // adjust if backend is remote

export const uploadResume = async (file) => {
  const form = new FormData();
  form.append("file", file);
  const response = await axios.post(`${BASE_URL}/upload_resume`, form);
  return response.data;
};

export async function startSession(sessionId, skills, job_title = "") {
  const response = await axios.post(`${BASE_URL}/start_session`, {
    session_id: sessionId,
    skills: skills,
  });
  return response.data;
};

export const nextQuestion = async (sessionId, userInput) => {
  const response = await axios.post(`${BASE_URL}/next_question`, {
    session_id: sessionId,
    user_input: userInput,
  });
  return response.data;
};
