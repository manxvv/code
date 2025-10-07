import React, { useState, useMemo } from "react";
import { useForm } from "react-hook-form";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Swal from "sweetalert2";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Modal from "@/components/Modal";
import { DataTableDemo } from "@/components/DataTable";
import { Edit, Trash2, Download, X } from "lucide-react";
import { deleteAuditData, enms, getuser_scripting_files, getUsers, gpl_audit_files_get, uploadgplauditScripting, uploadScripting, Urlenmmfiles } from "@/lib/api";
import Urls from "@/config/urls";
import { useSelector } from "react-redux";
import { final_url } from "@/lib/http";

function Gpl() {
    const queryClient = useQueryClient();
    const { register, handleSubmit, watch } = useForm();

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [commonisModalOpen, setCommonIsModalOpen] = useState(false);
    const [commonisModalData, setCommonIsModalData] = useState(false);
    const [commonisModalHead, setCommonIsModalHead] = useState(false);
    const [globalFilter, setGlobalFilter] = useState("");
    const [error, setError] = useState(null);
    const [uploading, setUploading] = useState(false);

    const [taskId, setTaskId] = useState("");
    const { data: enms_list } = useQuery({
        queryKey: ["enmfiles"],
        queryFn: Urlenmmfiles
    });


    // Fetch users
    const { data: gpl_audit_files = [] } = useQuery({
        queryKey: ["gpl_audit_files"],
        queryFn: gpl_audit_files_get,
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


            console.log(formData, "formDataformDataformData")
            return uploadgplauditScripting(formData);
        },
        onSuccess: (res) => {
            Swal.close();
            setUploading(false);
            setError(null);
            queryClient.invalidateQueries(["user_scripting_files"]);
            console.log("File uploaded successfully:", res);
            setIsModalOpen(false)
        },
        onError: (err) => {
            Swal.close();
            setUploading(false);
            setError(err?.response?.data?.message || "Something went wrong during file upload");
            console.error("File upload failed:", err);
        },
    });

    
    const onSubmit = (data) => {
        const formData = new FormData();
        formData.append("circle", data.circle);
        // formData.append("enm", data.enm);

        console.log(data, "datadatadatadatadatadatadata")

        if (data.Efile) {

            console.log(data.Efile, "data.Efiledata.Efiledata.Efile")
            const efiles = Array.from(data.Efile); // convert {"0":file,"1":file,...} → [file,file,...]
            efiles.forEach((file) => {
                formData.append("Efile", file);
            });
        }
        if (data.sitefile?.length) formData.append("siteList", data.sitefile[0]);

        uploadFileMutation(formData);
    };


      const { mutate: deleteEnmMutation } = useMutation({
            mutationFn:  deleteAuditData,
            onSuccess: () => {
                queryClient.invalidateQueries(["gpl_audit_files"]);
                // setDeleteModalOpen(false);
                // setSelectedEnmId(null);
            },
            onError: (error) => {
                console.error("Error deleting ENM:", error);
            }
        });

   const handleDelete = (id) => {
    console.log(id,"DDS");
    
    deleteEnmMutation(id)
   }

    const downloadFile = async (url, token, filename) => {
        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            console.error("Download failed", await response.json());
            return;
        }


        let filename_name = url.split("/").pop()

        let filename_new = filename_name.split("\\").pop()

        const blob = await response.blob();
        const link = document.createElement("a");
        link.href = window.URL.createObjectURL(blob);
        link.download = filename_new;
        document.body.appendChild(link);
        link.click();
        link.remove();
    };


    const columns = [
        {
            accessorKey: "aud_task_id",
            header: "Task Id",
            cell: ({ row }) => row.getValue("aud_task_id"),
        },
        {
            accessorKey: "circle",
            header: "Circle",
            cell: ({ row }) => row.getValue("circle"),
        },
        
        {
            
            accessorKey: "enms",
            header: "ENM",
            cell: ({ row }) => row.getValue("enms"),
        },
               {
            accessorKey: "username",
            header: "User Name",
            cell: ({ row }) => row.getValue("username"),
        },
        {
            accessorKey: "timestamp",
            header: "Time Stamp",
            cell: ({ row }) => row.getValue("timestamp"),
        },
        // {
        //     accessorKey: "site_id",
        //     header: "Site Id",
        //     cell: ({ row }) => {

        //         row.getValue("site_id")


        //         return <p className="cursor-pointer text-blue-600" onClick={() => {
        //             setCommonIsModalOpen(true)

        //             setCommonIsModalHead("View Sites")
        //             setCommonIsModalData(<><ul>{row.getValue("site_id").split("/").map((oneVal) => {
        //                 return <li>{oneVal}</li>
        //             })}</ul></>)
        //         }}>View Sites</p>
        //     },
        // },
        // {
        //     accessorKey: "nodes",
        //     header: "Node Id",
        //     cell: ({ row }) => {

        //         row.getValue("nodes")


        //         return <p className="cursor-pointer text-blue-600" onClick={() => {
        //             setCommonIsModalOpen(true)

        //             setCommonIsModalHead("View Nodes")
        //             setCommonIsModalData(<><ul>{row.getValue("nodes").split("/").map((oneVal) => {
        //                 return <li>{oneVal}</li>
        //             })}</ul></>)
        //         }}>View Nodes</p>
        //     },
        // },


        {
            accessorKey: "zip_path",
            header: "DOWNLOAD",
            cell: ({ row }) => {
                const file = row.original;
                const token = useSelector((state) => state.auth.access_token);

                console.log(row, "rowrowrowrowrowrowrowrowrowrowrowrow")
                return (
                    <Button
                        onClick={() =>
                            downloadFile(final_url + "/" + file.zip_path, token)
                        }
                    >
                        Download
                    </Button>
                );
            },
        },
        {
            id: "actions",
            header: "Actions",
            cell: ({ row }) => {
                const user = row.original;
console.log(user,"iser");

                return (
                    <div className="flex gap-2">
                      
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDelete(user.uID)}
                        >
                            <Trash2 className="h-4 w-4 text-red-600" />
                        </Button>
                    </div>
                );
            },
            enableSorting: false,
            enableHiding: false,
        }

    ];


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
                    className="w-fit"
                />
                <Button onClick={() => setIsModalOpen(true)}>New Audit</Button>
            </div>

            <DataTableDemo
                columns={columns}
                data={gpl_audit_files || []}
                globalFilter={globalFilter}
                setGlobalFilter={setGlobalFilter}
            />


            <Modal
                isOpen={commonisModalOpen}
                onClose={() => setCommonIsModalOpen(false)}
                title={commonisModalHead}
                size="lg"
                showCloseButton
                closeOnBackdrop
                closeOnEscape
            >
                <div className="h-80 overflow-x-hidden">

                    {commonisModalData}
                </div>

            </Modal>

            <Modal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                title="Create New Audit"
                size="lg"
                showCloseButton
                closeOnBackdrop
                closeOnEscape
            >
                <div className="max-h-[70vh] overflow-y-auto p-6">
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* Circle */}
                            {/* <div className='flex flex-col'>
                <label className="mb-2 font-medium text-gray-700 dark:text-gray-300">
                  Task Id
                </label>
                <input

                  {...register("taskId", {
                    onChange: (e) => {
                      setTaskId(e.target.value)
                    }
                  })}
                  autoComplete={false} placeholder='Task Id' type='text' value={taskId} list='task_ids' onChange={(e) => {
                    setTaskId(e.target.value)
                  }}
                  className="p-2 border rounded-md bg-white dark:bg-neutral-800 border-gray-300 dark:border-neutral-700" />

                <datalist id='task_ids'>
                  <option>Task Id</option>

                  {JSON.stringify(enms_list)}

                  {
                    enms_list && enms_list.map((one_enm) => {
                      return <option>{one_enm.task_id}</option>
                    })
                  }
                </datalist>

                {
                  enms_list && enms_list.filter((oneenm) => {

                    if (taskId == "") {
                      return false
                    } else {
                      return oneenm.task_id == taskId
                    }
                  }).length == 0 && taskId != "" && <p>Please select valid Task Id</p>
                }


              </div> */}
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
                            {/* <div className="flex flex-col">
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
              </div> */}

                            {/* Software Release */}
                            {/* <div className="flex flex-col">
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
              </div> */}

                            {/* Site List */}
                            {/* <div className="flex flex-col">
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
              </div> */}

                            {/* ENM Logs */}
                            <div className="flex flex-col">
                                <label className="mb-2 font-medium text-gray-700 dark:text-gray-300">
                                    Site List
                                </label>
                                <input
                                    type="file"
                                    {...register("sitefile")}
                                    accept=".xlsx,.xls"

                                    onChange={(e) => setValue("sitefile", e.target.files[0])}
                                    className="p-1.5 border rounded-md text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-gray-100 dark:file:bg-neutral-700 file:text-gray-700 dark:file:text-gray-300 hover:file:bg-gray-200 dark:hover:file:bg-neutral-600"
                                />
                            </div>
                            <div className="flex flex-col">
                                <label className="mb-2 font-medium text-gray-700 dark:text-gray-300">
                                    ENM Dump
                                </label>
                                <input
                                    type="file"
                                    {...register("Efile")}
                                    multiple
                                    onChange={(e) => setValue("Efile", e.target.files)}
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

export default Gpl;
