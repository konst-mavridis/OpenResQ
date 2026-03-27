export const API_BASE = process.env.NEXT_PUBLIC_API_URL;

export async function apiGet(path: string, token?: string) {
  const res = await fetch(`https://openresq.onrender.com${path}`, {
    headers: {
      Authorization: token ? `Bearer ${token}` : "",
    },
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return res.json();
}

export async function apiPost(path: string, body: Record<string, unknown>, token?: string) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: token ? `Bearer ${token}` : "",
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return res.json();
}
