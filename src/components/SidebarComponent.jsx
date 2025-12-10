// import React, { useState } from "react";
// import { Sidebar, SidebarBody, SidebarLink } from "../components/ui/Sidebar";
// import {
//   IconAlertTriangle,
//   IconArrowLeft,
//   IconBrandTabler,
//   IconUser,
//   IconUserBolt,
//   IconUserCircle,
//   IconUsers,
// } from "@tabler/icons-react";
// import { Link, Outlet, useNavigate } from "react-router-dom";
// import { motion } from "framer-motion";
// import { cn } from "../lib/utils";
// import { useDispatch, useSelector } from "react-redux";
// import Header from "./Header";
// import { logout } from "@/features/auth/authSlice";
// import Modal from "./Modal";
// import { useSidebar } from "../components/ui/Sidebar";
// import { useQuery } from "@tanstack/react-query";
// import { sidebarList } from "@/lib/api";
// import { Settings } from "lucide-react";


// const LogoutButton = ({ onClick, className }) => {
//   const { open, animate } = useSidebar();

//   return (
//     <button
//       onClick={onClick}
//       className={cn(
//         "flex items-center justify-start gap-2 group/sidebar py-3 px-2 rounded-lg transition-all duration-200 mb-1 w-full",
//         "text-slate-300 hover:bg-slate-800 hover:text-orange-400 hover:translate-x-1",
//         className
//       )}
//     >
//       <span className="transition-colors duration-200 group-hover/sidebar:text-orange-400">
//         <IconArrowLeft className="h-5 w-5 flex-shrink-0" />
//       </span>
//       <motion.span
//         animate={{
//           display: animate ? (open ? "inline-block" : "none") : "inline-block",
//           opacity: animate ? (open ? 1 : 0) : 1,
//         }}
//         className="text-sm font-medium group-hover/sidebar:translate-x-1 transition-all duration-200 whitespace-pre inline-block !p-0 !m-0"
//       >
//         Logout
//       </motion.span>
//     </button>
//   );
// };

// // Skeleton loader component for the sidebar
// const SidebarSkeleton = () => {
//   return (
//     <div className="mt-8 flex flex-col gap-2 animate-pulse">
//       {[...Array(5)].map((_, i) => (
//         <div key={i} className="flex items-center gap-3 group/sidebar py-3 px-2 rounded-lg">
//           <div className="h-5 w-5 bg-slate-700 rounded-md"></div>
//           <div className="h-4 w-28 bg-slate-700 rounded-md"></div>
//         </div>
//       ))}
//     </div>
//   );
// };


// export function SidebarDemo({ outlet }) {
//   const navigate = useNavigate();
//   const dispatch = useDispatch();
//   const [modalOpen, setModalOpen] = useState(false);

//   const role = useSelector((state) => state.auth.user.role)

//   // 1. Destructure isLoading and isError from useQuery
//   const { data, isLoading, isError } = useQuery({
//     queryKey: ["sidebarlink"],
//     queryFn: sidebarList
//   });


//   const links = data
//     ? [
//       ...data
//         // .filter(link => link.roles && link.roles.includes(role))
//         .map((link) => ({
//           ...link,
//           // icon: iconMap[link.icon] || <IconUsers className="h-5 w-5 flex-shrink-0" />
//         })),
//       ...(role === "admin"
//         ? [
//           {
//             label: "Settings",
//             href: "admin/link-settings",
//             // icon: <Settings className="h-5 w-5 flex-shrink-0" />,
//           },
//         ]
//         : []),
//     ]
//     : [];


//   // let userEmail = JSON.parse(localStorage.getItem("authData"))["user"]["email"]
//   // const user = useSelector((state) => state.auth.user);
//   const handleLogout = () => {
//     dispatch(logout());
//     navigate("/auth/login");
//   };

//   const getHeaderTitle = () => {
//     switch (location.pathname) {
//       case "/app/e-dashboard":
//         return "/// Dashboard";
//       case "/app/n-dashboard":
//         return "Nokia Dashboard";
//       case "/app/users":
//         return "User Management";
//       case "/app/check-in-out":
//         return "Check IN/OUT";
//       case "/app/scripting":
//         return "Scripting";
//       case "/app/migration-list":
//         return "Migration List";
//       case "/app/admin/users":
//         return "User Management";
//       case "/app/admin/circle-enm":
//         return "Circle - ENM";
//       case "/app/enm-command":
//         return "ENM Command";
//       case "/app/gpl-audit-///":
//         return "GPL Audit ///";
//       case "/app/gpl-audit-nokia":
//         return "GPL Audit Nokia";
//              case "/app/scripting-nokia":
//         return "Scripting Nokia";
//              case "/app/admin/link-settings":
//         return "Settings";
//       default:
//         return "DataYog";
//     }
//   };


//   const [open, setOpen] = useState(false);

//   return (
//     <>
//       <div
//         className={cn(
//           "flex flex-col md:flex-row  bg-white dark:bg-neutral-900 w-full flex-1 mx-auto border border-neutral-200 dark:border-neutral-500 overflow-hidden h-full"
//         )}
//       >
//         <Sidebar open={open} setOpen={setOpen} animate={false}>
//           <SidebarBody className="justify-between gap-3">
//             <div className=" flex justify-center ">
//               <Logo />
//             </div>
//             <div className="flex no-scrollbar border border-t-2  border-x-0 items-start flex-col flex-1 overflow-y-auto overflow-x-hidden">
//               <div className="mt-8 flex flex-col gap-2 w-full">
//                 {/* 2. Add conditional rendering for links */}
//                 {isLoading ? (
//                   <SidebarSkeleton />
//                 ) : isError ? (
//                   <div className="text-red-500 text-sm px-2">
//                     Failed to load links.
//                   </div>
//                 ) : (
//                   <>
//                     {links.map((link, idx) => (
//                       <SidebarLink
//                         key={idx}
//                         link={{
//                           label: link.label,
//                           href: link.href,
//                           // icon: link.icon,
//                         }}
//                       />
//                     ))}
//                     <LogoutButton onClick={() => setModalOpen(true)} />
//                   </>
//                 )}
//               </div>
//             </div>
//             {/* <div>
//               <div className="flex items-center gap-2 px-3 py-2 rounded-md text-white cursor-pointer">
//                 <IconUserCircle size={18} />
//                 <div className="flex flex-col">
//                   <span>
//                     {user?.role ? user.role.charAt(0).toUpperCase() + user.role.slice(1) : "User"}
//                   </span>
//                   <span>
//                     {userEmail}
//                   </span>
//                 </div>
//               </div>


//             </div> */}
//           </SidebarBody>
//         </Sidebar>

//         <div className="flex no-scrollbar border flex-col flex-1 overflow-hidden">
//           <Header header={getHeaderTitle()} />
//           <div className="flex-1 no-scrollbar overflow-y-auto">
//             {outlet}
//           </div>
//         </div>
//       </div>
//       <Modal
//         isOpen={modalOpen}
//         onClose={() => setModalOpen(false)}
//         title="Confirm Logout"
//         size="sm"
//         showCloseButton={true}
//         closeOnBackdrop={true}
//         closeOnEscape={true}
//       >
//         <div className="p-4">
//           <p className="text-sm text-gray-700 dark:text-gray-300 mb-4">
//             Are you sure you want to log out?
//           </p>
//           <div className="flex justify-end gap-2">
//             <button
//               onClick={() => setModalOpen(false)}
//               className="px-4 py-2 text-sm rounded bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-white"
//             >
//               Cancel
//             </button>
//             <button
//               onClick={handleLogout}
//               className="px-4 py-2 text-sm rounded bg-red-500 text-white hover:bg-red-600 dark:bg-red-600 dark:hover:bg-red-700"
//             >
//               Logout
//             </button>
//           </div>
//         </div>
//       </Modal>
//     </>
//   );
// }

// export const Logo = () => {
//   return (
//     <Link
//       to="/"
//       className="font-normal flex space-x-2 items-center text-sm text-black py-1 relative z-20"
//     >
//       <img
//         src="/download.png"
//         alt="Company Logo"
//         className="h-12 w-auto object-contain"
//         onError={(e) => {
//           e.target.style.display = 'none';
//         }}
//       />
//     </Link>
//   );
// };

// export const LogoIcon = () => {
//   return (
//     <Link
//       to="/"
//       className="font-normal flex space-x-2 items-center text-sm text-black py-1 relative z-20"
//     >
//       <div className="h-5 w-6 bg-black dark:bg-white rounded-br-lg rounded-tr-sm rounded-tl-lg rounded-bl-sm flex-shrink-0" />
//     </Link>
//   );
// };

import React, { useState, useEffect } from "react";
import { Sidebar, SidebarBody, SidebarLink } from "../components/ui/Sidebar";
import {
  IconArrowLeft,
} from "@tabler/icons-react";
import { Link, Outlet, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { cn } from "../lib/utils";
import { useDispatch, useSelector } from "react-redux";
import Header from "./Header";
import { logout } from "@/features/auth/authSlice";
import Modal from "./Modal";
import { useSidebar } from "../components/ui/Sidebar";
import { useQuery } from "@tanstack/react-query";
import { sidebarList } from "@/lib/api";
import { Settings } from "lucide-react";
import Urls from "../config/urls"; // ⬅️ API base yahan se

const LogoutButton = ({ onClick, className }) => {
  const { open, animate } = useSidebar();

  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center justify-start gap-2 group/sidebar py-3 px-2 rounded-lg transition-all duration-200 mb-1 w-full",
        "text-slate-300 hover:bg-slate-800 hover:text-orange-400 hover:translate-x-1",
        className
      )}
    >
      <span className="transition-colors duration-200 group-hover/sidebar:text-orange-400">
        <IconArrowLeft className="h-5 w-5 flex-shrink-0" />
      </span>
      <motion.span
        animate={{
          display: animate ? (open ? "inline-block" : "none") : "inline-block",
          opacity: animate ? (open ? 1 : 0) : 1,
        }}
        className="text-sm font-medium group-hover/sidebar:translate-x-1 transition-all duration-200 whitespace-pre inline-block !p-0 !m-0"
      >
        Logout
      </motion.span>
    </button>
  );
};

// Skeleton loader component for the sidebar
const SidebarSkeleton = () => {
  return (
    <div className="mt-8 flex flex-col gap-2 animate-pulse">
      {[...Array(5)].map((_, i) => (
        <div
          key={i}
          className="flex items-center gap-3 group/sidebar py-3 px-2 rounded-lg"
        >
          <div className="h-5 w-5 bg-slate-700 rounded-md"></div>
          <div className="h-4 w-28 bg-slate-700 rounded-md"></div>
        </div>
      ))}
    </div>
  );
};

export function SidebarDemo({ outlet }) {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [modalOpen, setModalOpen] = useState(false);

  const role = useSelector((state) => state.auth.user.role);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["sidebarlink"],
    queryFn: sidebarList,
  });

  const links = data
    ? [
        ...data.map((link) => ({
          ...link,
        })),
        ...(role === "admin"
          ? [
              {
                label: "Settings",
                href: "admin/link-settings",
              },
            ]
          : []),
      ]
    : [];

  const handleLogout = () => {
    dispatch(logout());
    navigate("/auth/login");
  };

  const getHeaderTitle = () => {
    switch (location.pathname) {
      case "/app/e-dashboard":
        return "/// Dashboard";
      case "/app/n-dashboard":
        return "Nokia Dashboard";
      case "/app/users":
        return "User Management";
      case "/app/check-in-out":
        return "Check IN/OUT";
      case "/app/scripting":
        return "Scripting";
      case "/app/migration-list":
        return "Migration List";
      case "/app/admin/users":
        return "User Management";
      case "/app/admin/circle-enm":
        return "Circle - ENM";
      case "/app/enm-command":
        return "ENM Command";
      case "/app/gpl-audit-///":
        return "GPL Audit ///";
      case "/app/gpl-audit-nokia":
        return "GPL Audit Nokia";
      case "/app/scripting-nokia":
        return "Scripting Nokia";
      case "/app/admin/link-settings":
        return "Settings";
      default:
        return "DataYog";
    }
  };

  const [open, setOpen] = useState(false);

  return (
    <>
      <div
        className={cn(
          "flex flex-col md:flex-row bg-white dark:bg-neutral-900 w-full flex-1 mx-auto border border-neutral-200 dark:border-neutral-500 overflow-hidden h-full"
        )}
      >
        <Sidebar open={open} setOpen={setOpen} animate={false}>
          <SidebarBody className="justify-between gap-3">
            <div className="flex justify-center">
              <Logo />
            </div>
            <div className="flex no-scrollbar border border-t-2 border-x-0 items-start flex-col flex-1 overflow-y-auto overflow-x-hidden">
              <div className="mt-8 flex flex-col gap-2 w-full">
                {isLoading ? (
                  <SidebarSkeleton />
                ) : isError ? (
                  <div className="text-red-500 text-sm px-2">
                    Failed to load links.
                  </div>
                ) : (
                  <>
                    {links.map((link, idx) => (
                      <SidebarLink
                        key={idx}
                        link={{
                          label: link.label,
                          href: link.href,
                        }}
                      />
                    ))}
                    <LogoutButton onClick={() => setModalOpen(true)} />
                  </>
                )}
              </div>
            </div>
          </SidebarBody>
        </Sidebar>

        <div className="flex no-scrollbar border flex-col flex-1 overflow-hidden">
          <Header header={getHeaderTitle()} />
          <div className="flex-1 no-scrollbar overflow-y-auto">{outlet}</div>
        </div>
      </div>
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Confirm Logout"
        size="sm"
        showCloseButton={true}
        closeOnBackdrop={true}
        closeOnEscape={true}
      >
        <div className="p-4">
          <p className="text-sm text-gray-700 dark:text-gray-300 mb-4">
            Are you sure you want to log out?
          </p>
          <div className="flex justify-end gap-2">
            <button
              onClick={() => setModalOpen(false)}
              className="px-4 py-2 text-sm rounded bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-white"
            >
              Cancel
            </button>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-sm rounded bg-red-500 text-white hover:bg-red-600 dark:bg-red-600 dark:hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}

// 🔥 Dynamic Logo – login se aaya hua logo_url + server se fetch
export const Logo = () => {
  const [logoSrc, setLogoSrc] = useState("/download.png");

  useEffect(() => {
    try {
      const raw = localStorage.getItem("authData");
      if (raw) {
        const parsed = JSON.parse(raw);
        const stored = parsed?.user?.logo_url; // backend se aya hua

        if (stored) {
          // agar full URL hai (http...) to direct use karo
          if (stored.startsWith("http")) {
            setLogoSrc(stored);
          } else {
            // warna API base prefix karke server se fetch
            setLogoSrc(`${Urls.baseURL}${stored}`);
          }
        }
      }
    } catch (e) {
      // ignore, default logo रहेगा
    }
  }, []);

  return (
    <Link
      to="/"
      className="font-normal flex space-x-2 items-center text-sm text-black py-1 relative z-20"
    >
      <img
        src={logoSrc}
        alt="Company Logo"
        className="h-12 w-auto object-contain"
        onError={(e) => {
          e.target.src = "/download.png"; // fallback
        }}
      />
    </Link>
  );
};

export const LogoIcon = () => {
  return (
    <Link
      to="/"
      className="font-normal flex space-x-2 items-center text-sm text-black py-1 relative z-20"
    >
      <div className="h-5 w-6 bg-black dark:bg-white rounded-br-lg rounded-tr-sm rounded-tl-lg rounded-bl-sm flex-shrink-0" />
    </Link>
  );
};
