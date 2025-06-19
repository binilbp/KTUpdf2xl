
const scrollToSection = (id : string) => {
    const el = document.getElementById(id);
        if (el) {
            el.scrollIntoView({behavior : 'smooth'});
        };
};

type menuProps = {
    isMenuOpen: boolean;
};

const SideMenu = ({isMenuOpen}: menuProps) => {

    return (
        <nav className={`${isMenuOpen ? "block": "hidden"} lg:hidden z-40 fixed bg-(--primary-bg-color)/80 backdrop-blur-md 
            px-12 py-4 w-full h-dvh flex flex-col justify-between text-(--primary-text-color)`}>
            <ul className="items-end py-14 font-semibold text-xl flex flex-col gap-5">
                <li className="cursor-pointer" onClick={() => scrollToSection('home')}>Home</li>
                <li className="cursor-pointer" onClick={() => scrollToSection('about')}>About</li>
                <li className="cursor-pointer" onClick={() => scrollToSection('team')}>Team</li>
            </ul>
            <div className="mb-20 flex flex-col gap-5 justify-around items-center">
                <button className="text-lg font-semibold cursor-pointer ">Sign Up</button> 
                {/* <button className="text-md rounded-2xl h-8 w-2/5 bg-(--primary-color) text-white font-semibold cursor-pointer border-none">Sign Up</button>  */}
                <button className="text-lg rounded-2xl h-9 w-3/4 bg-(--primary-accent-color) text-white font-semibold cursor-pointer border-none">Log In</button> 
            </div>
        </nav>
  )
}

export default SideMenu;