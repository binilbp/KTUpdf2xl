import { useState } from "react";
import PlaceHolder from "../assets/placeholder.png";
import LoginForm from "./LoginForm";

const HeroSection = () => {
  const [showLogin, setShowLogin] = useState(false);

  return (
    <section
      id="home"
      className="relative min-h-dvh flex flex-col lg:flex-row justify-start lg:justify-center items-center gap-14 lg:gap-28 px-6 lg:px-20 py-20 lg:py-0 lg:pb-40"
    >
      {/* Login Modal */}
      {showLogin && <LoginForm onClose={() => setShowLogin(false)} />}

      {/* Left Text Section */}
      <div className="lg:w-1/2 text-center lg:text-left space-y-6">
        <h1 className="text-4xl lg:text-5xl font-extrabold leading-snug text-transparent bg-gradient-to-r lg:bg-gradient-to-b from-[#111827] to-[#166485] bg-clip-text">
          Analyze. <br className="hidden lg:block" />
          Track Credits. <br className="hidden lg:block" />
          Visualize.
        </h1>
        <p
          className="text-base lg:text-lg leading-relaxed max-w-xl lg:max-w-4xl lg:w-full mx-auto lg:mx-0"
          style={{ color: "var(--secondary-text-color)" }}
        >
          KTU Result Analyser lets you analyze KTU results with detailed insights, effective credit
          tracking, and interactive graphs — all through a simple web interface.
        </p>
        <button
          className="bg-blue-600 px-10 py-3 text-white rounded font-semibold shadow-md hover:bg-blue-500 transition cursor-pointer"
          onClick={() => setShowLogin(true)}
        >
          Login/Register to continue
        </button>
      </div>

      {/* Right Placeholder Image */}
      <div>
        <img 
          alt="user profile"
          src={PlaceHolder} 
          className="w-70 h-70 object-cover rounded-xl"
        />
      </div>
    </section>
  );
};

export default HeroSection;
