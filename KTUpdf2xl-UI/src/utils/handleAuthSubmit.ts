

export const handleAuthSubmit = (
  e: React.FormEvent<HTMLFormElement>
): void => {
  e.preventDefault();
  const formData = new FormData(e.currentTarget);
  const data: { [key: string]: string } = {};

  formData.forEach((value, key) => {
    data[key] = value.toString();
  });

  console.log("Form Data:", data);
  // You can call an API here later
};
