import { auth } from "./firebase";
import { signInWithEmailAndPassword, signOut } from "firebase/auth";
import { apiPost } from "./api";

export async function login(email: string, password: string) {
  const userCred = await signInWithEmailAndPassword(auth, email, password);
  const token = await userCred.user.getIdToken();

  // ενημερώνουμε το FastAPI
  await apiPost("/auth/login", { token });

  return userCred.user;
}

export async function logout() {
  await apiPost("/auth/logout", {});
  await signOut(auth);
}
