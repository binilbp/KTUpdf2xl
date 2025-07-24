import { useEffect, useState } from "react";
import { motion, easeInOut } from "framer-motion";
import { handleAuthSubmit } from "../utils/handleAuthSubmit";

const LoginForm = ({ onClose }: { onClose: () => void }) => {
  const [isRegister, setIsRegister] = useState(false);
  const [fadeIn, setFadeIn] = useState(false);

  useEffect(() => {
    setFadeIn(true);
  }, []);

  const handleClose = () => {
    setFadeIn(false);
    setTimeout(onClose, 300);
  };

  const transition = { duration: 0.3, ease: easeInOut };

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center transition-opacity duration-300 ${
        fadeIn ? "opacity-100" : "opacity-0"
      } bg-black/50`}
    >
      <motion.div
        layout
        initial={{ opacity: 0, y: 40, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 40, scale: 0.95 }}
        transition={transition}
        className="bg-white p-8 rounded-2xl shadow-2xl w-[95%] max-w-md relative z-10"
      >
        <button
          onClick={handleClose}
          className="absolute top-2 right-3 text-gray-500 hover:text-black text-2xl"
        >
          ×
        </button>

        <h2 className="text-2xl font-bold text-center mb-6">
          {isRegister ? "Register" : "Login"}
        </h2>

        <motion.form
          layout
          onSubmit={handleAuthSubmit} // <-- moved out
          className="flex flex-col gap-4"
        >
          {isRegister && (
            <>
              <motion.input
                layout
                type="text"
                name="username"
                placeholder="Username"
                required
                className="p-2 border border-gray-300 rounded"
              />
              <motion.input
                layout
                type="email"
                name="email"
                placeholder="Email"
                required
                className="p-2 border border-gray-300 rounded"
              />
              <motion.input
                layout
                type="text"
                name="institution"
                placeholder="Institution Name"
                required
                className="p-2 border border-gray-300 rounded"
              />
              <motion.input
                layout
                type="text"
                name="role"
                placeholder="Institution Role"
                required
                className="p-2 border border-gray-300 rounded"
              />
            </>
          )}

          {!isRegister && (
            <motion.input
              layout
              type="email"
              name="email"
              placeholder="Email"
              required
              className="p-2 border border-gray-300 rounded"
            />
          )}

          <motion.input
            layout
            type="password"
            name="password"
            placeholder="Password"
            required
            className="p-2 border border-gray-300 rounded"
          />

          {isRegister && (
            <motion.input
              layout
              type="password"
              name="confirmPassword"
              placeholder="Confirm Password"
              required
              className="p-2 border border-gray-300 rounded"
            />
          )}

          <motion.button
            layout
            type="submit"
            className="bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
          >
            {isRegister ? "Register" : "Login"}
          </motion.button>
        </motion.form>

        <p className="text-sm text-center mt-4">
          {isRegister ? "Already have an account?" : "Don't have an account?"}{" "}
          <button
            type="button"
            onClick={() => setIsRegister((prev) => !prev)}
            className="text-blue-600 underline hover:text-blue-800 transition-colors"
          >
            {isRegister ? "Login" : "Register"}
          </button>
        </p>
      </motion.div>
    </div>
  );
};

export default LoginForm;
