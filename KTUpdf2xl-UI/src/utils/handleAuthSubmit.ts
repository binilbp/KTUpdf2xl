import type { NavigateFunction } from "react-router-dom";

export const handleAuthSubmit = async (
  e: React.FormEvent<HTMLFormElement>,
  navigate: NavigateFunction,
  isRegister: boolean
): Promise<void> => {
  e.preventDefault();
  const formData = new FormData(e.currentTarget);
  const data: { [key: string]: string } = {};

  formData.forEach((value, key) => {
    data[key] = value.toString();
  });

  console.log("Form Data:", data);

  if (isRegister && data.password !== data.confirmPassword) {
    alert("Passwords do not match!");
    return;
  }

  if (isRegister) {
    delete data.confirmPassword;
  }

  const endpoint = isRegister
    ? "http://localhost:8000/signup"
    : "http://localhost:8000/login";

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Request Failed");
    }

    const result = await response.json();
    const token = result.token;

    if (token) {
      localStorage.setItem("token", token);
    }

    navigate("/dashboard");
  } catch (error) {
    console.error("Auth error:", error);
    alert("Authentication failed: " + error);
  }
};
