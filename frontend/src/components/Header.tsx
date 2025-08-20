import React from 'react';
import { Navbar, NavbarBrand, NavbarToggle, NavbarCollapse, NavbarLink, Dropdown, DropdownHeader, DropdownItem, DropdownDivider, Avatar } from 'flowbite-react';
import ThemeToggle from './ThemeToggle';
import { useAuth } from '../context/AuthContext';

const Header: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <Navbar fluid rounded className="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-10">
      <NavbarBrand href="#">
        <img src="/homepage_icon.png" className="mr-3 h-6 sm:h-9 rounded-full" alt="VoiceTutor Logo" />
        <span className="self-center whitespace-nowrap text-xl font-semibold dark:text-white">VoiceTutor</span>
      </NavbarBrand>
      
      <div className="flex md:order-2 items-center">
        <ThemeToggle />
        {user ? (
          <div className="relative group hidden md:block">
            <div className="cursor-pointer">
              <Avatar alt="User settings" img={user.picture} rounded />
            </div>
            <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-lg shadow-lg py-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-20">
              <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="block text-sm text-gray-900 dark:text-white">{user.name}</span>
                    <span className="block truncate text-sm font-medium text-gray-500 dark:text-gray-400">{user.email}</span>
                  </div>
                  <div className="flex items-center ml-4">
                    <div className="h-2 w-2 rounded-full bg-green-500 mr-1"></div>
                    <span className="text-xs font-medium text-green-600 dark:text-green-400">Active</span>
                  </div>
                </div>
              </div>
              <div className="py-1">
                <button className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700">Dashboard</button>
                <button className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700">Settings</button>
                <button className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700">My Files</button>
                <div className="border-t border-gray-100 dark:border-gray-700 my-1"></div>
                <button 
                  onClick={logout}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
                >
                  Sign out
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="hidden md:block text-sm text-gray-700 dark:text-gray-300 ml-2">
            Guest User
          </div>
        )}

        {/* Mobile version with click behavior for better UX */}
        {user ? (
          <div className="md:hidden">
            <Dropdown
              arrowIcon={false}
              inline
              label={
                <Avatar alt="User settings" img={user.picture} rounded />
              }
            >
              <DropdownHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <span className="block text-sm">{user.name}</span>
                    <span className="block truncate text-sm font-medium">{user.email}</span>
                  </div>
                  <div className="flex items-center ml-4">
                    <div className="h-2 w-2 rounded-full bg-green-500 mr-1"></div>
                    <span className="text-xs font-medium text-green-600 dark:text-green-400">Active</span>
                  </div>
                </div>
              </DropdownHeader>
              <DropdownItem>Dashboard</DropdownItem>
              <DropdownItem>Settings</DropdownItem>
              <DropdownItem>My Files</DropdownItem>
              <DropdownDivider />
              <DropdownItem onClick={logout}>Sign out</DropdownItem>
            </Dropdown>
          </div>
        ) : (
          <div className="md:hidden text-sm text-gray-700 dark:text-gray-300 ml-2">
            Guest User
          </div>
        )}
        <NavbarToggle />
      </div>
      
      <NavbarCollapse>
        <NavbarLink href="#" active>
          Home
        </NavbarLink>
        <NavbarLink href="#">About</NavbarLink>
        <NavbarLink href="#">Services</NavbarLink>
        <NavbarLink href="#">Pricing</NavbarLink>
        <NavbarLink href="#">Contact</NavbarLink>
      </NavbarCollapse>
    </Navbar>
  );
};

export default Header;