// import React from 'react';
// import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
// import { sidebarList, toggleRoleForLink } from '@/lib/api';

// import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
// import { Switch } from "@/components/ui/switch";
// import { Toaster, toast } from "sonner";
// import { Loader2, Lock, Unlock } from 'lucide-react';

// export default function LinkSetting() {
//   const queryClient = useQueryClient();

//   const { data: links, isLoading, isError, error } = useQuery({
//     queryKey: ["sidebarlink"],
//     queryFn: sidebarList,
//   });

//   const { mutate, isLoading: isUpdating } = useMutation({
//     mutationFn: toggleRoleForLink,
//     onSuccess: (data) => {
//       queryClient.invalidateQueries({ queryKey: ['sidebarlink'] });
//       toast.success(data.message);
//     },
//     onError: (error) => {
//       toast.error(error.message);
//     },
//   });

//   const handleToggle = (linkId) => {
//     mutate({ linkId, role: 'user' });
//   };

//   if (isLoading) {
//     return (
//       <div className="flex items-center justify-center min-h-[300px]">
//         <Loader2 className="w-8 h-8 animate-spin text-neutral-400" />
//       </div>
//     );
//   }

//   if (isError) {
//     return (
//       <div className="p-4">
//         <Card className="border-red-200 bg-red-50">
//           <CardContent className="pt-4">
//             <p className="text-sm text-red-600">Error: {error.message}</p>
//           </CardContent>
//         </Card>
//       </div>
//     );
//   }

//   return (
//     <>
//       <Toaster position="top-right" richColors />
//       <div className="p-4 max-w-3xl mx-auto">
//         <Card>
//           <CardHeader className="pb-3">
//             <CardTitle className="text-xl">Page Access Control</CardTitle>
//             <CardDescription className="text-sm">
//               Manage user access to pages
//             </CardDescription>
//           </CardHeader>
//           <CardContent className="space-y-2">
//             {links?.map((link) => (
//               <div 
//                 key={link.id}
//                 className="flex items-center justify-between p-3 rounded-lg hover:bg-neutral-50 dark:hover:bg-neutral-900 transition-colors"
//               >
//                 <div className="flex items-center gap-3">
//                   {link.roles.includes('user') ? (
//                     <Unlock className="w-4 h-4 text-emerald-600" />
//                   ) : (
//                     <Lock className="w-4 h-4 text-neutral-400" />
//                   )}
//                   <span className="font-medium text-sm">{link.label}</span>
//                 </div>
//                 <Switch
//                   checked={link.roles.includes('user')}
//                   onCheckedChange={() => handleToggle(link.id)}
//                   disabled={isUpdating}
//                   className="data-[state=checked]:bg-emerald-600"
//                 />
//               </div>
//             ))}
//           </CardContent>
//         </Card>
//       </div>
//     </>
//   );
// }


import React, { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { sidebarList, toggleRoleForLink, getDomains, uploadLogo } from "@/lib/api";
import Urls from "@/config/urls";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";

import { Switch } from "@/components/ui/switch";
import { Toaster, toast } from "sonner";
import { Loader2, Lock, Unlock } from "lucide-react";

export default function LinkSetting() {
  const queryClient = useQueryClient();

  // ----------- GET DOMAINS ----------
  const { data: domainData } = useQuery({
    queryKey: ["domains"],
    queryFn: getDomains,
  });

  const domains = domainData?.domains || [];
  const [selectedDomain, setSelectedDomain] = useState("");

  // Upload preview + file
  const [logoFile, setLogoFile] = useState(null);
  const [logoPreview, setLogoPreview] = useState(null);

  // Set first domain by default
  useEffect(() => {
    if (domains.length > 0 && !selectedDomain) {
      setSelectedDomain(domains[0].domain);
    }
  }, [domains]);

  // Reset preview when domain changes (very important)
  useEffect(() => {
    setLogoPreview(null);
    setLogoFile(null);
  }, [selectedDomain]);

  // ----------- GET SIDEBAR LINKS ----------
  const { data: sidebarResponse, isLoading, isError, error } = useQuery({
    queryKey: ["sidebarlinks", selectedDomain],
    queryFn: () =>
      sidebarList(selectedDomain ? { domain: selectedDomain } : {}),
    enabled: true,
  });

  const links = Array.isArray(sidebarResponse)
    ? sidebarResponse
    : sidebarResponse?.links || [];

  // ------------------- UPLOAD LOGO -------------------
  const uploadLogoMutation = useMutation({
    mutationFn: uploadLogo,
    onSuccess: () => {
      toast.success("Logo uploaded successfully");
      queryClient.invalidateQueries({ queryKey: ["domains"] });
    },
    onError: () => {
      toast.error("Logo upload failed");
    },
  });

  const handleLogoChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLogoFile(file);
    setLogoPreview(URL.createObjectURL(file));
  };

  const handleLogoUpload = () => {
    if (!logoFile) {
      toast.error("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("domain", selectedDomain);
    formData.append("file", logoFile);

    uploadLogoMutation.mutate(formData);
  };

  // ------------------- TOGGLE ROLE -------------------
  const { mutate, isLoading: isUpdating } = useMutation({
    mutationFn: toggleRoleForLink,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["sidebarlinks"] });
      toast.success(data.message);
    },
    onError: (error) => toast.error(error.message),
  });

  const handleToggle = (linkId) => {
    mutate({ linkId, role: "user", domain: selectedDomain });
  };

  // ------------------- DOMAIN LOGO HANDLING -------------------

  const selectedDomainData = domains.find((d) => d.domain === selectedDomain);

  let domainLogoUrl = selectedDomainData?.logo_url || null;

  if (domainLogoUrl && !domainLogoUrl.startsWith("http")) {
    domainLogoUrl = `${Urls.baseURL}${domainLogoUrl}`;
  }

  // Highest priority → Upload preview  
  // Otherwise → Domain logo_url  
  const effectivePreview = logoPreview || domainLogoUrl || null;

  // ------------------- LOADING -------------------
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[300px]">
        <Loader2 className="w-8 h-8 animate-spin text-neutral-400" />
      </div>
    );
  }

  // ------------------- ERROR -------------------
  if (isError) {
    return (
      <Card className="p-4 border-red-300 bg-red-50">
        <p className="text-sm text-red-600">{error?.message}</p>
      </Card>
    );
  }

  // ------------------- MAIN UI -------------------
  return (
    <>
      <Toaster position="top-right" richColors />

      <div className="p-4 max-w-4xl mx-auto">

        <Card>

          {/* HEADER */}
          <CardHeader className="pb-3 flex flex-row items-center justify-between gap-4">

            {/* LEFT TITLE */}
            <div className="flex-1">
              <CardTitle className="text-xl">Page Access Control</CardTitle>
              <CardDescription className="text-sm">
                Manage user access
              </CardDescription>
            </div>

            {/* CENTER DROPDOWN */}
            <div className="flex-1 flex justify-center">
              <select
                value={selectedDomain}
                onChange={(e) => setSelectedDomain(e.target.value)}
                className="border rounded-md px-3 py-2 text-sm bg-white dark:bg-neutral-900"
              >
                {domains.map((d, idx) => (
                  <option key={idx} value={d.domain}>
                    {d.domain}
                  </option>
                ))}
              </select>
            </div>

            {/* RIGHT — LOGO UPLOAD & PREVIEW */}
            <div className="flex-1 flex justify-end">
              <div className="flex flex-col items-end gap-2">

                {/* FIXED PREVIEW */}
                {effectivePreview ? (
                  <img
                    src={effectivePreview}
                    alt="Logo"
                    className="h-12 w-auto object-contain border rounded shadow bg-white p-1"
                    onError={(e) => {
                      e.target.src = "/download.png";
                    }}
                  />
                ) : (
                  <div className="text-xs text-gray-400">No Logo</div>
                )}

                <input
                  type="file"
                  accept="image/*"
                  onChange={handleLogoChange}
                  className="text-xs"
                />

                <button
                  onClick={handleLogoUpload}
                  className="px-3 py-1 rounded bg-emerald-600 text-white text-xs hover:bg-emerald-700"
                >
                  Upload Logo
                </button>

              </div>
            </div>

          </CardHeader>

          {/* LINKS AREA */}
          <CardContent className="space-y-2">
            {links.map((link) => {
              const isON = link.domains?.includes(selectedDomain);

              return (
                <div key={link.id} className="flex items-center justify-between p-3 rounded-lg">
                  <div className="flex items-center gap-3">
                    {isON ? (
                      <Unlock className="w-4 h-4 text-emerald-600" />
                    ) : (
                      <Lock className="w-4 h-4 text-neutral-400" />
                    )}

                    <span className="font-medium text-sm">{link.label}</span>
                  </div>

                  <Switch
                    checked={isON}
                    onCheckedChange={() => handleToggle(link.id)}
                    disabled={isUpdating}
                    className="data-[state=checked]:bg-emerald-600"
                  />
                </div>
              );
            })}
          </CardContent>

        </Card>
      </div>
    </>
  );
}
