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
import Swal from 'sweetalert2';
import { Edit, Trash2 } from 'lucide-react';
import { Outlet } from 'react-router-dom';
import Modal from './Modal';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { enms, createEnms, deleteEnm } from '@/lib/api';

function Admin() {
    const queryClient = useQueryClient();
    const { register, handleSubmit, reset, setValue } = useForm();

    // --- STATE CHANGES ---
    // State for the text search input
    const [globalFilter, setGlobalFilter] = useState("");
    // NEW: State specifically for the vendor dropdown filter
    const [columnFilters, setColumnFilters] = useState([]);
    // --- END OF STATE CHANGES ---

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [deleteModalOpen, setDeleteModalOpen] = useState(false);
    const [selectedEnmId, setSelectedEnmId] = useState(null);
    const [vendor, setVendor] = useState("");

    const { data } = useQuery({
        queryKey: ["enms"],
        queryFn: enms,
    });

    const { mutate } = useMutation({
        mutationFn: createEnms,
        onSuccess: () => {
            Swal.fire("", "Successful", "success");
            queryClient.invalidateQueries(["enms"]);
            setIsModalOpen(false);
        },
        onError: (error) => {
            Swal.fire("", error?.response?.data?.message || "Error", "error");
            console.error("Error creating ENM:", error);
        }
    });

    const { mutate: deleteEnmMutation } = useMutation({
        mutationFn: deleteEnm,
        onSuccess: () => {
            queryClient.invalidateQueries(["enms"]);
            setDeleteModalOpen(false);
            setSelectedEnmId(null);
        },
        onError: (error) => {
            console.error("Error deleting ENM:", error);
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
                return vendorValue
                    // .split(" ")
                    // .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
                    // .join(" ");
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
                            // Make sure you're getting the correct ID field from your data
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
            <div className="flex flex-1">
                <div className="p-2 md:p-10 bg-white dark:bg-neutral-900 flex flex-col gap-2 flex-1 w-full h-full">
                    <Outlet />
                    <div className="flex flex-col md:flex-row md:items-center md:justify-end gap-4 py-2">
                        <div className="flex items-center justify-between w-full ">
                            {/* Left: Search Bar */}
                            <div className="flex-1 max-w-sm">
                                <Input
                                    placeholder="Search anything..."
                                    value={globalFilter ?? ""}
                                    onChange={(event) => setGlobalFilter(event.target.value)}
                                    className="w-fit" // Changed from w-fit for better responsiveness
                                />
                            </div>

                            {/* Right: Vendor Dropdown + Button */}
                            <div className="flex items-center gap-2">
                                <div className="w-48">
                                    {/* --- MODIFIED VENDOR SELECT --- */}
                                    <Select
                                        onValueChange={(value) => {
                                            if (value === "all") {
                                                // If "All" is selected, clear the filter for the 'vendor' column
                                                setColumnFilters(
                                                    columnFilters.filter((f) => f.id !== "vendor")
                                                );
                                            } else {
                                                // Set the filter for the 'vendor' column
                                                setColumnFilters([
                                                    ...columnFilters.filter((f) => f.id !== "vendor"), // Remove old vendor filter
                                                    { id: "vendor", value: value }, // Add new one
                                                ]);
                                            }
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
                                    {/* --- END OF MODIFICATION --- */}
                                </div>
                                <Button
                                    onClick={() => {
                                        reset();
                                        setVendor(""); // Reset vendor selection in modal
                                        setIsModalOpen(true);
                                    }}
                                >
                                    Create Circle
                                </Button>
                            </div>
                        </div>
                    </div>
                    {/* --- MODIFIED DATATABLE PROPS --- */}
                    <DataTableDemo
                        data={data || []}
                        columns={columns}
                        globalFilter={globalFilter}
                        setGlobalFilter={setGlobalFilter}
                        columnFilters={columnFilters}      // Pass the new state
                        setColumnFilters={setColumnFilters}  // Pass the setter
                    />
                    {/* --- END OF MODIFICATION --- */}
                </div>
            </div>

            {/* --- Modals remain the same, ensure you have them here --- */}
            {/* Create ENM Modal */}
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
                                setValue("vendor", value)
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

            {/* Delete Confirmation Modal */}
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