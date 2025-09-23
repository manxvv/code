import React from 'react'
import ThemeToggle from './ThemeToggle'
import { useSelector } from 'react-redux';

export default function Header({ header }) {


  const role = useSelector((state) => state.auth.user.role)


  let userEmail = JSON.parse(localStorage.getItem("authData"))["user"]["email"]
  const user = useSelector((state) => state.auth.user);
  return (
    <div className='h-16 bg-slate-800 dark:bg-neutral-800 dark:border-neutral-800 border-b border-slate-700 p-2 flex items-center justify-between shadow-sm'>
      <span className='font-bold text-2xl text-slate-100'>{header}</span>
      <div className="flex flex-row gap-2 items-center">
        <div className="flex flex-col">
          <span className='text-amber-50'>
            {user?.role ? user.role.charAt(0).toUpperCase() + user.role.slice(1) : "User"}
          </span>
          <span className='text-amber-50'>
            {userEmail}
          </span>
        </div>
        <ThemeToggle />
      </div>
    </div>
  )
}