import React, { useState, useMemo } from "react";
import { useForm } from "react-hook-form";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Swal from "sweetalert2";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Modal from "@/components/Modal";
import { DataTableDemo } from "@/components/DataTable";
import { Edit, Trash2, Download } from "lucide-react";
import { enms, getUsers, uploadScripting, Urlenmmfiles } from "@/lib/api";

function Scripting() {
  const queryClient = useQueryClient();
  const { register, handleSubmit, watch } = useForm();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [globalFilter, setGlobalFilter] = useState("");
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);



  // Fetch users
  const { data: users = [] } = useQuery({
    queryKey: ["users"],
    queryFn: getUsers,
  });

  const { data } = useQuery({
    queryKey: ["files"],
    queryFn: Urlenmmfiles
  });


  const { data: enmsdata } = useQuery({
    queryKey: ["enms"],
    queryFn: enms
  });




  // ✅ mutation for file upload
  const { mutate: uploadFileMutation, isLoading: isUploading } = useMutation({
    mutationFn: async (formData) => {
      setUploading(true);
      Swal.fire({
        title: "Processing...",
        text: "Please wait",
        allowOutsideClick: false,
        didOpen: () => Swal.showLoading(),
      });

      return uploadScripting(formData);
    },
    onSuccess: (res) => {
      Swal.close();
      setUploading(false);
      setError(null);
      queryClient.invalidateQueries(["datatable"]);
      console.log("File uploaded successfully:", res);
    },
    onError: (err) => {
      Swal.close();
      setUploading(false);
      setError(err?.message || "Something went wrong during file upload");
      console.error("File upload failed:", err);
    },
  });

  const onSubmit = (data) => {
    const formData = new FormData();
    formData.append("circle", data.circle);
    formData.append("enm", data.enm);
    formData.append("softwareRelease", data.softwareRelease);

    if (data.Efile?.length) formData.append("eFile", data.Efile[0]);
    if (data.siteList?.length) formData.append("siteList", data.siteList[0]);

    uploadFileMutation(formData);
  };

  const columns = useMemo(
    () => [
      { Header: "Circle", accessor: "circle", id: "circle" },
      { Header: "ENM", accessor: "enm", id: "enm" },
      { Header: "Software Release", accessor: "softwareRelease", id: "softwareRelease" },
      {
        Header: "Actions",
        id: "actions", // 👈 add this
        Cell: ({ row }) => (
          <div className="flex gap-2">
            <Edit
              size={16}
              className="cursor-pointer text-blue-500"
              onClick={() => console.log("edit", row.original)}
            />
            <Trash2
              size={16}
              className="cursor-pointer text-red-500"
              onClick={() => console.log("delete", row.original)}
            />
            <Download
              size={16}
              className="cursor-pointer text-green-500"
              onClick={() => console.log("download", row.original)}
            />
          </div>
        ),
      },
    ],
    []
  );


  const selectedCircle = watch("circle") || "";
  const selectedEnm = watch("enm") || "";

  // Filter options based on selections
  const filteredCircles = useMemo(() => {
    if (!selectedEnm) return [...new Set(enmsdata && enmsdata.map((e) => e.circle))];
    return [
      ...new Set(
        enmsdata.filter((e) => e.enm === selectedEnm).map((e) => e.circle)
      ),
    ];
  }, [enmsdata, selectedEnm]);

  const filteredEnms = useMemo(() => {
    if (!selectedCircle) return [...new Set(enmsdata && enmsdata.map((e) => e.enm))];
    return [
      ...new Set(
        enmsdata.filter((e) => e.circle === selectedCircle).map((e) => e.enm)
      ),
    ];
  }, [enmsdata, selectedCircle]);


  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <Input
          placeholder="Search..."
          value={globalFilter}
          onChange={(e) => setGlobalFilter(e.target.value)}
          className="max-w-xs"
        />
        <Button onClick={() => setIsModalOpen(true)}>Upload Script</Button>
      </div>

      {/* Table */}
      <DataTableDemo
        columns={columns}
        data={users || []} // or whatever data you want to show
        globalFilter={globalFilter}
        setGlobalFilter={setGlobalFilter}
      />

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
                <label className="mb-2 font-medium text-gray-700 dark:text-gray-300">
                  Circle
                </label>
                <select
                  {...register("circle")}
                  className="p-2 border rounded-md bg-white dark:bg-neutral-800 border-gray-300 dark:border-neutral-700"
                >
                  <option value="">Select</option>
                  {filteredCircles.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>

              {/* ENM */}
              <div className="flex flex-col">
                <label className="mb-2 font-medium text-gray-700 dark:text-gray-300">
                  ENM
                </label>
                <select
                  {...register("enm")}
                  className="p-2 border rounded-md bg-white dark:bg-neutral-800 border-gray-300 dark:border-neutral-700"
                >
                  <option value="">Select</option>
                  {filteredEnms.map((e) => (
                    <option key={e} value={e}>
                      {e}
                    </option>
                  ))}
                </select>
              </div>

              {/* Software Release */}
              <div className="flex flex-col">
                <label className="mb-2 font-medium text-gray-700 dark:text-gray-300">
                  Software Release
                </label>
                <select
                  {...register("softwareRelease")}
                  className="p-2 border rounded-md bg-white dark:bg-neutral-800 border-gray-300 dark:border-neutral-700"
                >
                  <option value="">Select</option>
                  {["24Q2"].map((op) => (
                    <option key={op} value={op}>
                      {op}
                    </option>
                  ))}
                </select>
              </div>

              {/* Site List */}
              <div className="flex flex-col">
                <label className="mb-2 font-medium text-gray-700 dark:text-gray-300">
                  Site List
                </label>
                <input
                  type="file"
                  {...register("siteList")}
                  accept=".xlsx,.xls"
                  onChange={(e) => setValue("siteList", e.target.files[0])}
                  className="p-1.5 border rounded-md text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-gray-100 dark:file:bg-neutral-700 file:text-gray-700 dark:file:text-gray-300 hover:file:bg-gray-200 dark:hover:file:bg-neutral-600"
                />
              </div>

              {/* ENM Logs */}
              <div className="flex flex-col">
                <label className="mb-2 font-medium text-gray-700 dark:text-gray-300">
                  ENM Log
                </label>
                <input
                  type="file"
                  {...register("Efile")}
                  accept=".txt"
                  onChange={(e) => setValue("Efile", e.target.files[0])}
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
    </div>
  );
}

export default Scripting;
