import { apiPost } from "./api";
import { auth } from "./firebase";
import { signInWithEmailAndPassword, signOut, signInWithPopup, GoogleAuthProvider } from "firebase/auth";

const googleProvider = new GoogleAuthProvider();

export async function login(email: string, password: string) {
  const userCred = await signInWithEmailAndPassword(auth, email, password);
  return userCred.user;
}

export async function loginWithGoogle() {
  const userCred = await signInWithPopup(auth, googleProvider);
  return userCred.user;
}

export async function logout() {
  const user = auth.currentUser;
  if (user) {
    try {
      const token = await user.getIdToken();
      await apiPost("/logout", {}, token);
    } catch (error) {
      console.error("Failed to notify backend about logout", error);
    }
  }
  await signOut(auth);
}
