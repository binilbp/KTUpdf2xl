import Header from "./components/Header";
import HeroSection from "./components/HeroSection";
import Footer from "./components/Footer";
import About from "./components/About";
import Team from "./components/Team";

function App() {

  return (
    <div className='flex flex-col min-h-dvh bg-(--primary-bg-color)'>

      <Header />

      <main>
        <HeroSection />
        <About/>
        <Team/>
      </main>

      <Footer />

    </div>
  );
};


export default App
