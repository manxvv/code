import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { sidebarList, toggleRoleForLink } from '@/lib/api';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Toaster, toast } from "sonner";
import { Loader2, Lock, Unlock } from 'lucide-react';

export default function LinkSetting() {
  const queryClient = useQueryClient();

  const { data: links, isLoading, isError, error } = useQuery({
    queryKey: ["sidebarlink"],
    queryFn: sidebarList,
  });

  const { mutate, isLoading: isUpdating } = useMutation({
    mutationFn: toggleRoleForLink,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['sidebarlink'] });
      toast.success(data.message);
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const handleToggle = (linkId) => {
    mutate({ linkId, role: 'user' });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[300px]">
        <Loader2 className="w-8 h-8 animate-spin text-neutral-400" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-4">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-4">
            <p className="text-sm text-red-600">Error: {error.message}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <>
      <Toaster position="top-right" richColors />
      <div className="p-4 max-w-3xl mx-auto">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-xl">Page Access Control</CardTitle>
            <CardDescription className="text-sm">
              Manage user access to pages
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {links?.map((link) => (
              <div 
                key={link.id}
                className="flex items-center justify-between p-3 rounded-lg hover:bg-neutral-50 dark:hover:bg-neutral-900 transition-colors"
              >
                <div className="flex items-center gap-3">
                  {link.roles.includes('user') ? (
                    <Unlock className="w-4 h-4 text-emerald-600" />
                  ) : (
                    <Lock className="w-4 h-4 text-neutral-400" />
                  )}
                  <span className="font-medium text-sm">{link.label}</span>
                </div>
                <Switch
                  checked={link.roles.includes('user')}
                  onCheckedChange={() => handleToggle(link.id)}
                  disabled={isUpdating}
                  className="data-[state=checked]:bg-emerald-600"
                />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </>
  );
}