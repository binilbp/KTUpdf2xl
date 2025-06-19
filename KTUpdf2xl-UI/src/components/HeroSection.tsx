import Upload from "./Upload";
import UploadOpts from "./UploadOptions";

const HeroSection = () => {
  return (
    <section
      id="home"
      className="min-h-dvh flex flex-col lg:flex-row justify-start lg:justify-center items-center gap-14 lg:gap-28 px-6 lg:px-20 py-20 lg:py-0 lg:pb-40">
        {/*scroll-m-10 provides offset for smoothscroll to home, without this hero goes below header*/ }

      {/* Left Text Section */}
      <div className="lg:w-1/2 text-center lg:text-left space-y-6">
        <h1 className="text-4xl lg:text-5xl font-extrabold leading-snug
          text-transparent bg-gradient-to-r lg:bg-gradient-to-b from-[#111827] to-[#166485] bg-clip-text">
          Analyze. <br className="hidden lg:block" />
          Track Credits. <br className="hidden lg:block" />
          Visualize.
        </h1>
        <p className="text-base lg:text-lg leading-relaxed max-w-xl lg:max-w-4xl lg:w-full mx-auto lg:mx-0 text-(--secondary-text-color)">
          KTU Result Analyser lets you analyze KTU results with detailed insights, effective credit
          tracking, and interactive graphs — all through a simple web interface.
        </p>
      </div>

      {/* Right Upload Section */}
      <div className="lg:w-2/7 w-5/6  flex flex-col gap-6 p-6 md:p-10 border-3 rounded-2xl shadow-md border-(--primary-color)">
        <Upload />
        <UploadOpts />
      </div>
    </section>
  );
};

export default HeroSection;

