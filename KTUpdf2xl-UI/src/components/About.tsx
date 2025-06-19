
const About = () => {
  return (
    <section id="about" className="min-h-screen flex flex-col justify-center bg-gray-300 py-5 px-15  gap-6 text-center">
        <h1 className="text-4xl md:text-5xl font-normal underline -underline-offset-auto text-(--primary-text-color) ">The Story Behind</h1>
        <p className="text-(--primary-text-color) pt-6 pb-10 text-balance">
            KTU Result Analyser was created to support faculty members in quickly processing student result PDFs. Manually extracting data is tedious — this tool simplifies the process by converting PDFs to Excel and providing clear, structured data for analysis.
            Fast, accurate, and designed to save your time.
        </p>
    </section>
  )
}

export default About;