import About from "./About";
import Footer from "./Footer";
import Header from "./Header";
import HeroSection from "./HeroSection";
import Team from "./Team";


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
