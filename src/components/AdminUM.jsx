import { DataTableDemo } from '@/components/DataTable';
import TabsHeader from '@/components/TabHeader';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { enms, createUsers, createEnms, createCircle, deleteEnm, circleData, fetchUsers, deleteUsers } from '@/lib/api';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { Edit, Trash2 } from 'lucide-react';
import React, { useState } from 'react'
import { Outlet } from 'react-router-dom';
import Modal from './Modal';
import { useForm } from 'react-hook-form';
import Swal from 'sweetalert2';
import { toast } from 'sonner';

function AdminUM() {
    const queryClient = useQueryClient();
    const { register, handleSubmit, reset } = useForm();
    const [globalFilter, setGlobalFilter] = useState("");
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [deleteModalOpen, setDeleteModalOpen] = useState(false);
    const [selectedEnmId, setSelectedEnmId] = useState(null);
    // console.log(selectedEnmId, "fdff");

    const { data } = useQuery({
        queryKey: ["users"],
        queryFn: fetchUsers
    });


const { mutate } = useMutation({
    mutationFn: createUsers,
    onSuccess: (res) => {
        // This was already correct, notifies on success
        toast.success(res.message || "User created successfully!");
        queryClient.invalidateQueries(["enms"]); // Assuming you might want to refetch a list of users, adjust query key if needed
        setIsModalOpen(false);
    },
    onError: (error) => {
        // Updated to correctly display the error message
        toast.error(error?.response?.data?.error || "An error occurred while creating the user.");
        console.error("Error creating user:", error);
    }
});

const { mutate: deleteEnmMutation } = useMutation({
    mutationFn: deleteUsers,
    onSuccess: () => {
        // ADDED: Success toast on deletion
        toast.success("User deleted successfully.");
        queryClient.invalidateQueries(["enms"]); // Adjust query key if needed
        setDeleteModalOpen(false);
        setSelectedEnmId(null);
    },
    onError: (error) => {
        // ADDED: Error toast on deletion failure
        toast.error(error?.response?.data?.error || "Failed to delete the user.");
        console.error("Error deleting user:", error);
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
            accessorKey: "full_name",
            header: "Full Name",
            cell: ({ row }) => row.getValue("full_name") || "-", // fallback if null
        },
        {
            accessorKey: "email",
            header: "Email",
            cell: ({ row }) => row.getValue("email") || "-", // fallback if null
        },
        {
            id: "actions",
            header: "Actions",
            cell: ({ row }) => (
                <div className="flex gap-2">
                    {/* Later you can add edit here */}
                    <Button
                        variant="destructive"
                        size="icon"
                        onClick={() => {
                            setSelectedEnmId(row.original.id);
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
                    <div className="flex flex-col md:flex-row md:items-center md:justify-end gap-4 py-4">
                        <div className="flex flex-col sm:flex-row flex-end gap-2 w-full md:w-auto">
                            <Button onClick={() => {
                                reset();
                                setIsModalOpen(true);
                            }}>
                                Create User
                            </Button>
                            <Input
                                placeholder="Search User..."
                                value={globalFilter ?? ""}
                                onChange={(event) => setGlobalFilter(event.target.value)}
                                className="w-full sm:max-w-sm"
                            />
                        </div>
                    </div>
                    <DataTableDemo
                        data={data || []}
                        columns={columns}
                        globalFilter={globalFilter}
                        setGlobalFilter={setGlobalFilter}
                    />
                </div>
            </div>

            {/* Create ENM Modal */}
            <Modal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                title={"Create User"}
                size="sm"
                showCloseButton={true}
                closeOnBackdrop={true}
                closeOnEscape={true}
            >
                <form
                    onSubmit={handleSubmit(onSubmit)}
                    className="space-y-2 p-0"
                >
                    
                    <div>
                        <label className="block text-sm font-medium mb-2">Full Name</label>
                        <Input
                            {...register("full_name", { required: "Full Name is required" })}
                            placeholder="Full Name"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-2">Email</label>
                        <Input
                            {...register("email", { required: "Email is required" })}
                            placeholder="Email"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-2">Password</label>
                        <Input
                            {...register("password", { required: "Password is required" })}
                            placeholder="Password"
                        />
                    </div>

                    <div className="flex justify-end">
                        <Button type="submit">
                            Submit
                        </Button>
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
                    <p>Are you sure you want to delete this User?</p>
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

export default AdminUM;
