import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

export const analyzeUser = async (username, force = false) => {
  const res = await axios.get(`${API}/analyze/${encodeURIComponent(username)}`, {
    params: force ? { force: true } : {},
  });
  return res.data;
};

export const fetchHistory = async (limit = 10) => {
  const res = await axios.get(`${API}/history`, { params: { limit } });
  return res.data;
};

export const deleteProfile = async (username) => {
  const res = await axios.delete(`${API}/profile/${encodeURIComponent(username)}`);
  return res.data;
};
