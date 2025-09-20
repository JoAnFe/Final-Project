export const API = import.meta.env.VITE_API ?? "http://localhost:8000";
const DASH_USER = import.meta.env.VITE_DASH_USER ?? "admin";
const DASH_PASS = import.meta.env.VITE_DASH_PASS ?? "changeme";

export async function token() {
  const body = new URLSearchParams({
    username: DASH_USER,
    password: DASH_PASS,
  });
  const r = await fetch(`${API}/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  return (await r.json()).access_token as string;
}
export async function listAlerts(tok: string) {
  const r = await fetch(`${API}/alerts`, { headers: {Authorization:`Bearer ${tok}`}});
  return await r.json();
}
export async function listDevices(tok: string) {
  const r = await fetch(`${API}/devices`, { headers: {Authorization:`Bearer ${tok}`}});
  return await r.json();
}
export async function readings(tok: string, id: string) {
  const r = await fetch(`${API}/readings/${id}?limit=200`, { headers: {Authorization:`Bearer ${tok}`}});
  return await r.json();
}
