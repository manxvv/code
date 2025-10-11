// src/pages/Admin.jsx

import { DataTableDemo } from '@/components/DataTable';
// ... other imports
import React, { useState } from 'react'; // Make sure React is imported
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { Trash2 } from 'lucide-react';
import { Outlet } from 'react-router-dom';
import Modal from './Modal';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { enms, createEnms, deleteEnm } from '@/lib/api';
import { Toaster, toast } from 'sonner';

function Admin() {
    const queryClient = useQueryClient();
    const { register, handleSubmit, reset, setValue } = useForm();

    // --- STATE CHANGES ---
    const [globalFilter, setGlobalFilter] = useState("");
    const [columnFilters, setColumnFilters] = useState([]);
    // --- !! FIX: ADD PAGINATION STATE !! ---
    const [pagination, setPagination] = useState({
        pageIndex: 0, // initial page index
        pageSize: 10, // initial page size
    });
    // --- END OF STATE CHANGES ---

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [deleteModalOpen, setDeleteModalOpen] = useState(false);
    const [selectedEnmId, setSelectedEnmId] = useState(null);
    const [vendor, setVendor] = useState("");

    const { data, isLoading } = useQuery({ // Added isLoading
        queryKey: ["enms"],
        queryFn: enms,
    });

    const { mutate } = useMutation({
        mutationFn: createEnms,
        onSuccess: () => {
            toast.success("Circle created successfully.");
            queryClient.invalidateQueries(["enms"]);
            setIsModalOpen(false);
            reset();
        },
        onError: (error) => {
            toast.error(error?.response?.data?.message || "Error creating circle.");
            console.error("Error creating ENM:", error);
        }
    });

    const { mutate: deleteEnmMutation } = useMutation({
        mutationFn: deleteEnm,
        onSuccess: (response) => {
            queryClient.invalidateQueries(["enms"]);
            setDeleteModalOpen(false);
            setSelectedEnmId(null);
            toast.success(response.message);
        },
        onError: (error) => {
            console.error("Error deleting ENM:", error);
            toast.error(error.message);
        }
    });

    const onSubmit = (formData) => {
        mutate(formData);
    };

    const confirmDelete = () => {
        if (selectedEnmId) {
            deleteEnmMutation(selectedEnmId);
        }
    };

    const columns = [
        {
            accessorKey: "oem",
            header: "OEM",
            cell: ({ row }) => {
                const vendorValue = row.getValue("oem") || "-";
                if (vendorValue === "-") return vendorValue;
                return vendorValue.charAt(0).toUpperCase() + vendorValue.slice(1);
            }
        },
        {
            accessorKey: "circle",
            header: "Circle",
            cell: ({ row }) => row.getValue("circle") || "-",
        },
        {
            accessorKey: "enm",
            header: "ENM",
            cell: ({ row }) => row.getValue("enm") || "-",
        },
        {
            id: "actions",
            header: "Actions",
            cell: ({ row }) => (
                <div className="flex gap-2">
                    <Button
                        variant="destructive"
                        size="icon"
                        onClick={() => {
                            setSelectedEnmId(row.original._id || row.original.id);
                            setDeleteModalOpen(true);
                        }}
                    >
                        <Trash2 className="h-4 w-4" />
                    </Button>
                </div>
            ),
        },
    ];

    return (
        <>
            <Toaster position="top-right" richColors />
            <div className="flex flex-1">
                <div className="p-2 md:p-10 bg-white dark:bg-neutral-900 flex flex-col gap-2 flex-1 w-full h-full">
                    <Outlet />
                    <div className="flex flex-col md:flex-row md:items-center md:justify-end gap-4 py-2">
                        <div className="flex items-center justify-between w-full ">
                            <div className="flex-1 max-w-sm">
                                <Input
                                    placeholder="Search anything..."
                                    value={globalFilter ?? ""}
                                    onChange={(event) => setGlobalFilter(event.target.value)}
                                    className="w-full"
                                />
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-48">
                                    <Select
                                        onValueChange={(value) => {
                                            const newColumnFilters = columnFilters.filter((f) => f.id !== "oem");
                                            if (value !== "all") {
                                                newColumnFilters.push({ id: "oem", value: value });
                                            }
                                            setColumnFilters(newColumnFilters);
                                        }}
                                    >
                                        <SelectTrigger className="w-full">
                                            <SelectValue placeholder="Select Vendor" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="all">All Vendors</SelectItem>
                                            <SelectItem value="nokia">Nokia</SelectItem>
                                            <SelectItem value="ericsson">Ericsson</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                                <Button
                                    onClick={() => {
                                        reset();
                                        setVendor("");
                                        setIsModalOpen(true);
                                    }}
                                >
                                    Create Circle
                                </Button>
                            </div>
                        </div>
                    </div>
                    
                    {/* --- !! FIX: PASS ALL REQUIRED PROPS TO DATATABLE !! --- */}
                    <DataTableDemo
                        columns={columns}
                        data={data || []}
                        isLoading={isLoading}
                        pagination={pagination}
                        setPagination={setPagination}
                        globalFilter={globalFilter}
                        setGlobalFilter={setGlobalFilter}
                        columnFilters={columnFilters}
                        setColumnFilters={setColumnFilters}
                        // totalCount is derived from data length for client-side pagination
                        totalCount={(data || []).length} 
                    />
                    {/* --- END OF FIX --- */}
                </div>
            </div>

            {/* Modals remain unchanged */}
            <Modal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                title={"Create Circle"}
                size="sm"
                showCloseButton={true}
                closeOnBackdrop={true}
                closeOnEscape={true}
            >
                <form
                    onSubmit={handleSubmit(onSubmit)}
                    className="space-y-4 p-4"
                >
                    <div>
                        <label className="block text-sm font-medium mb-2">OEM</label>
                        <Select
                            onValueChange={(value) => {
                                setVendor(value)
                                setValue("oem", value)
                            }}
                        >
                            <SelectTrigger className="w-full">
                                <SelectValue placeholder="Select Vendor" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="nokia">Nokia</SelectItem>
                                <SelectItem value="ericsson">Ericsson</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    {(vendor === "nokia" || vendor === "ericsson") && (
                        <div>
                            <label className="block text-sm font-medium mb-2">Circle</label>
                            <Input
                                {...register("circle", { required: "Circle is required" })}
                                placeholder="Circle"
                            />
                        </div>
                    )}

                    {vendor === "ericsson" && (
                        <div>
                            <label className="block text-sm font-medium mb-2">ENM</label>
                            <Input
                                {...register("enm", { required: "ENM is required" })}
                                placeholder="ENM"
                            />
                        </div>
                    )}

                    <div className="flex justify-end">
                        <Button type="submit">Submit</Button>
                    </div>
                </form>
            </Modal>
            <Modal
                isOpen={deleteModalOpen}
                onClose={() => setDeleteModalOpen(false)}
                title={"Delete ENM"}
                size="sm"
                showCloseButton={true}
                closeOnBackdrop={true}
                closeOnEscape={true}
            >
                <div className="p-4 space-y-4">
                    <p>Are you sure you want to delete this ENM?</p>
                    <div className="flex justify-end gap-2">
                        <Button
                            variant="secondary"
                            onClick={() => setDeleteModalOpen(false)}
                        >
                            Cancel
                        </Button>
                        <Button
                            variant="destructive"
                            onClick={confirmDelete}
                        >
                            Delete
                        </Button>
                    </div>
                </div>
            </Modal>
        </>
    );
}

export default Admin;