import { useState } from "react";
// import userAvatar from "../assets/user.png";
import HamburgerMenu from "./Hamburger";
import SideMenu from "./SideMenu";

const scrollToSection = (id : string) => {
    const el = document.getElementById(id);
        if (el) {
            el.scrollIntoView({behavior : 'smooth'});
        }
    
};


const Header = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    return (
    <>
    <header className='sticky z-50 top-0  py-3  w-full bg-(--primary-bg-color)' >
        <nav className="text-(--primary-text-color) px-5 flex justify-between items-center" >
            <a href="#">
                <h1 className=' font-bold text-xl '>KTU Result Analyser</h1>
            </a>
            <ul className='hidden lg:flex md:gap-18 justify-between items-center font-medium'>
                <li className='cursor-pointer transition-all duration-200 hover:underline hover:underline-offset-4 ' onClick={() => scrollToSection('home')}>Home</li>
                <li className='cursor-pointer transition-all duration-200 hover:underline hover:underline-offset-4 ' onClick={() => scrollToSection('about')}>About</li>
                <li className='cursor-pointer transition-all duration-200 hover:underline hover:underline-offset-4 ' onClick={() => scrollToSection('team')}>Team</li>
                {/* <li className="cursor-pointer flex justify-between items-center gap-3">
                    <div className="w-8 mr-5 aspect-square rounded-full overflow-hidden cursor-pointer">
                        <img 
                            alt="user profile"
                            src={userAvatar} 
                            className="w-full h-full"
                        />
                    </div>
                </li> */}
            </ul>
            <button className="lg:hidden" 
                onClick={()=>setIsMenuOpen(!isMenuOpen)}>
                <HamburgerMenu/>
            </button>
        </nav>
    </header>
    <SideMenu isMenuOpen={isMenuOpen}/>
    </>
)
}
export default Header;