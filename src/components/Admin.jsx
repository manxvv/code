import { DataTableDemo } from '@/components/DataTable';
import TabsHeader from '@/components/TabHeader';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {  enms, createUsers, createEnms, createCircle, deleteEnm, circleData } from '@/lib/api';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { Edit, Trash2 } from 'lucide-react';
import React, { useState } from 'react'
import { Outlet } from 'react-router-dom';
import Modal from './Modal';
import { useForm } from 'react-hook-form';
import Swal from 'sweetalert2'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

function Admin() {
    const queryClient = useQueryClient();
    const { register, handleSubmit, reset,setValue } = useForm();
    const [globalFilter, setGlobalFilter] = useState("");
    console.log(globalFilter,"fdfd123");

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [deleteModalOpen, setDeleteModalOpen] = useState(false);
    const [selectedEnmId, setSelectedEnmId] = useState(null);
      const [vendor, setVendor] = useState("")

console.log(selectedEnmId,"fdff");

        const { data } = useQuery({
            queryKey: ["enms"],
            queryFn: enms
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
            // setError(error.message || "Something went wrong during file upload");

            console.error("Error creating ENM:", error);
        }
    });

    const vendors = [
  { value: "nokia", label: "Nokia" },
  { value: "ericsson", label: "Ericsson" },
]




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
            accessorKey: "vendor",
            header: "OEM",
cell: ({ row }) => {
  const vendor = row.getValue("vendor") || "-"; // fallback if null
  if (vendor === "-") return vendor;

  // Split words by space, capitalize first letter, join back
  return vendor
    .split(" ")
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ");
}
        },
        {
            accessorKey: "circle",
            header: "Circle",
            cell: ({ row }) => row.getValue("circle") || "-", // fallback if null
        },
        {
          accessorKey: "enm",
          header: "ENM",
          cell: ({ row }) => row.getValue("enm") || "-", // fallback if null
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
                    <div className="flex flex-col md:flex-row md:items-center md:justify-end gap-4 py-2">
            <div className="flex items-center justify-between w-full ">
  {/* Left: Search Bar */}
  <div className="flex-1 max-w-sm">
    <Input
      placeholder="Search anything..."
      value={globalFilter ?? ""}
      onChange={(event) => setGlobalFilter(event.target.value)}
      className="w-full"
    />
  </div>

  {/* Right: Vendor Dropdown + Button */}

  {/* Right: Vendor Dropdown + Button */}
  <div className="flex items-center gap-2">
    <div className="w-48">
      <Select
        onValueChange={(value) => {
          // This part is correct. It sets the globalFilter state.
          console.log("Filtering by vendor:", value); // Add this line for debugging
          setGlobalFilter(value === "all" ? "" : value);
        }}
      >
        <SelectTrigger className="w-full">
          <SelectValue placeholder="Select Vendor" />
        </SelectTrigger>
        <SelectContent>
          {/* === THE FIX IS HERE === */}
          <SelectItem value="all">All Vendors</SelectItem>

          {/* The value must be lowercase to match your API data */}
          <SelectItem value="nokia">Nokia</SelectItem>

          {/* The value must be lowercase to match your API data */}
          <SelectItem value="ericsson">Ericsson</SelectItem>
          {/* === END OF FIX === */}
        </SelectContent>
      </Select>
    </div>

    <Button
      onClick={() => {
        reset()
        setIsModalOpen(true)
      }}
    >
      Create Circle
    </Button>
  </div>
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
              {...register("circle", { required: "circle is required" })}
              placeholder="Circle"
            />
          </div>
        )}

        {vendor === "ericsson" && (
          <div>
            <label className="block text-sm font-medium mb-2">ENM</label>
            <Input
              {...register("enm", { required: "enm is required" })}
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