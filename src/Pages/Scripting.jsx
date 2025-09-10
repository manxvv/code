import React, { useState, useMemo } from 'react';
import { useForm } from 'react-hook-form';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import Modal from '@/components/Modal';
import { DataTableDemo } from '@/components/DataTable';
import { Edit, Trash2, Download } from 'lucide-react';
import { getUsers, getEnms } from '@/lib/api';
import { Outlet } from 'react-router-dom';

function Scripting() {
  const { register, handleSubmit, watch, setValue } = useForm();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [globalFilter, setGlobalFilter] = useState("");

  // Fetch users
  const { data: users = [] } = useQuery({
    queryKey: ["users"],
    queryFn: getUsers,
  });

  // Fetch ENMs
  const { data: enmsdata = [] } = useQuery({
    queryKey: ["enmsdata"],
    queryFn: getEnms,
  });

  // Watch selected circle and ENM
  const selectedCircle = watch('circle') || '';
  const selectedEnm = watch('enm') || '';

  // Filter options based on selections
  const filteredCircles = useMemo(() => {
    if (!selectedEnm) return [...new Set(enms.map(e => e.circle))];
    return [...new Set(enms.filter(e => e.enm === selectedEnm).map(e => e.circle))];
  }, [enms, selectedEnm]);

  const filteredEnms = useMemo(() => {
    if (!selectedCircle) return [...new Set(enms.map(e => e.enm))];
    return [...new Set(enms.filter(e => e.circle === selectedCircle).map(e => e.enm))];
  }, [enms, selectedCircle]);

  const columns = [
    { accessorKey: "circle", header: "CIRCLE" },
    { accessorKey: "enm", header: "ENM" },
    { accessorKey: "username", header: "USERNAME" },
    { accessorKey: "site_count", header: "SITE COUNT" },
    { accessorKey: "created_time", header: "CREATED TIME" },
    {
      id: "download",
      header: "DOWNLOAD",
      cell: ({ row }) => (
        <Button variant="outline" size="sm" className="flex items-center gap-2">
          <Download className="h-4 w-4" /> ZIP
        </Button>
      ),
      enableSorting: false,
      enableHiding: false,
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <div className="flex gap-2">
          <Button variant="ghost" size="icon">
            <Edit className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon">
            <Trash2 className="h-4 w-4 text-red-600" />
          </Button>
        </div>
      ),
      enableSorting: false,
      enableHiding: false,
    },
  ];

  const onSubmit = (data) => {
    console.log("Form submitted:", data);
  };

  return (
    <>
      <div className="flex flex-1">
        <div className="p-2 md:p-10 bg-white dark:bg-neutral-900 flex flex-col gap-2 flex-1 w-full h-full">
          <Outlet />

          <div className="flex flex-col md:flex-row md:items-center md:justify-end gap-4 py-4">
            <div className="flex flex-col sm:flex-row flex-end gap-2 w-full md:w-auto">
              <Button
                className="bg-orange-500 text-white font-bold px-8 py-2.5 rounded-md hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-50 w-full"
                onClick={() => setIsModalOpen(true)}
              >
                Create Script
              </Button>

              <Input
                placeholder="Search users..."
                value={globalFilter ?? ""}
                onChange={(e) => setGlobalFilter(e.target.value)}
                className="w-full sm:max-w-sm"
              />
            </div>
          </div>

          <DataTableDemo
            data={users}
            columns={columns}
            globalFilter={globalFilter}
            setGlobalFilter={setGlobalFilter}
          />
        </div>
      </div>

      {/* Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create New Script"
        size="lg"
        showCloseButton
        closeOnBackdrop
        closeOnEscape
      >
        <div className="max-h-[70vh] overflow-y-auto p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

              {/* Circle */}
              <div className="flex flex-col">
                <label className="mb-2 font-medium text-gray-700 dark:text-gray-300">Circle</label>
                <select
                  {...register('circle')}
                  className="p-2 border rounded-md bg-white dark:bg-neutral-800 border-gray-300 dark:border-neutral-700"
                >
                  <option value="">Select</option>
                  {filteredCircles.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              {/* ENM */}
              <div className="flex flex-col">
                <label className="mb-2 font-medium text-gray-700 dark:text-gray-300">ENM</label>
                <select
                  {...register('enm')}
                  className="p-2 border rounded-md bg-white dark:bg-neutral-800 border-gray-300 dark:border-neutral-700"
                >
                  <option value="">Select</option>
                  {filteredEnms.map((e) => (
                    <option key={e} value={e}>{e}</option>
                  ))}
                </select>
              </div>

              {/* Software Release */}
              <div className="flex flex-col">
                <label className="mb-2 font-medium text-gray-700 dark:text-gray-300">Software Release</label>
                <select
                  {...register('softwareRelease')}
                  className="p-2 border rounded-md bg-white dark:bg-neutral-800 border-gray-300 dark:border-neutral-700"
                >
                  <option value="">Select</option>
                  {["24Q2"].map(op => <option key={op} value={op}>{op}</option>)}
                </select>
              </div>

              {/* Site List */}
              <div className="flex flex-col">
                <label className="mb-2 font-medium text-gray-700 dark:text-gray-300">Site List</label>
                <input
                  type="file"
                  {...register('siteList')}
                  accept=".xlsx,.xls"
                  className="p-1.5 border rounded-md text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-gray-100 dark:file:bg-neutral-700 file:text-gray-700 dark:file:text-gray-300 hover:file:bg-gray-200 dark:hover:file:bg-neutral-600"
                />
              </div>

              {/* ENM Logs */}
              <div className="flex flex-col">
                <label className="mb-2 font-medium text-gray-700 dark:text-gray-300">ENM Logs</label>
                <input
                  type="file"
                  {...register('Efile')}
                  accept=".txt"
                  className="p-1.5 border rounded-md text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-gray-100 dark:file:bg-neutral-700 file:text-gray-700 dark:file:text-gray-300 hover:file:bg-gray-200 dark:hover:file:bg-neutral-600"
                />
              </div>

            </div>

            <div className="pt-6 flex justify-end">
              <button
                type="submit"
                className="bg-orange-500 text-white font-bold px-8 py-2.5 rounded-md hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-50 w-full"
              >
                Submit
              </button>
            </div>
          </form>
        </div>
      </Modal>
    </>
  );
}

export default Scripting;
