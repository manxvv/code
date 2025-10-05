import React, { useState, useMemo } from "react";
import { useForm } from "react-hook-form";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Swal from "sweetalert2";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Modal from "@/components/Modal";
import { DataTableDemo } from "@/components/DataTable";
import { Edit, Trash2, Download } from "lucide-react";
import { enms, getuser_scripting_files, getUsers, uploadScripting, Urlenmmfiles } from "@/lib/api";
import Urls from "@/config/urls";
import { useSelector } from "react-redux";
import { final_url } from "@/lib/http";

function ScriptingNokia() {
  const queryClient = useQueryClient();
  const [loadingRow, setLoadingRow] = useState(null);
  const { register, handleSubmit, watch } = useForm();
  const [downloading, setDownloading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [rowStates, setRowStates] = useState({});
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [commonisModalOpen, setCommonIsModalOpen] = useState(false);
  const [commonisModalData, setCommonIsModalData] = useState(false);
  const [commonisModalHead, setCommonIsModalHead] = useState(false);
  const [globalFilter, setGlobalFilter] = useState("");
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);
  
  const [uploadingId, setUploadingId] = useState(null);
  const [uploadErrorId, setUploadErrorId] = useState(null);
  const [uploadErrorMsg, setUploadErrorMsg] = useState("");
  
  const [taskId, setTaskId] = useState("");
  const { data: enms_list } = useQuery({
    queryKey: ["enmfiles"],
    queryFn: Urlenmmfiles
  });


  // Fetch users
  const { data: user_scripting_files = [] } = useQuery({
    queryKey: ["user_scripting_files"],
    queryFn: getuser_scripting_files,
  });

  const { data } = useQuery({
    queryKey: ["files"],
    queryFn: Urlenmmfiles
  });


  const { data: enmsdata } = useQuery({
    queryKey: ["enms"],
    queryFn: enms
  });
  // const { mutate: uploadFileMutation } = useMutation({
  //   mutationFn: async ({ rowId, formData }) => {
  //     // mark row uploading
  //     setRowStates((prev) => ({
  //       ...prev,
  //       [rowId]: { uploading: true, error: null },
  //     }));
  
  //     return uploadScripting(formData);
  //   },
  //   onSuccess: (res, { rowId }) => {
  //     setRowStates((prev) => ({
  //       ...prev,
  //       [rowId]: { uploading: false, error: null },
  //     }));
  //     queryClient.invalidateQueries(["user_scripting_files"]);
  //     setIsModalOpen(false);
  //   },
  //   onError: (err, { rowId }) => {
  //     setRowStates((prev) => ({
  //       ...prev,
  //       [rowId]: {
  //         uploading: false,
  //         error: err?.response?.data?.message || "Something went wrong during file upload",
  //       },
  //     }));
  //   },
  // });
  const { mutate: uploadFileMutation } = useMutation({
    mutationFn: async ({ rowId, formData }) => {
      // Set row status to uploading
      setRowStates((prev) => ({
        ...prev,
        [rowId]: { status: "uploading", errorMsg: "" },
      }));
      return uploadScripting(formData);
    },
    onSuccess: (res, { rowId }) => {
      setRowStates((prev) => ({
        ...prev,
        [rowId]: { status: "completed", errorMsg: "" },
      }));
      queryClient.invalidateQueries(["user_scripting_files"]);
      setIsModalOpen(false); // Close modal after success
    },
    onError: (err, { rowId }) => {
      setRowStates((prev) => ({
        ...prev,
        [rowId]: { status: "error", errorMsg: err?.response?.data?.message || "Upload failed" },
      }));
    },
  });
  // const onSubmit = async (data) => {
  //   const formData = new FormData();
  //   formData.append("taskId", taskId);
  //   formData.append("softwareRelease", data.softwareRelease);
  
  //   if (data.Efile?.length) formData.append("eFile", data.Efile[0]);
  
  //   try {
  //     await uploadFileMutation(formData);
  //     setIsModalOpen(false); 
  //   } catch (error) {

  //     console.error(error);
  //   }
  // };
  
  // const onSubmit = async (data) => {
  //   const formData = new FormData();
  //   formData.append("taskId", taskId);
  //   formData.append("softwareRelease", data.softwareRelease);
  //   if (data.Efile?.length) formData.append("eFile", data.Efile[0]);
  
  //   // Set row to pending first
  //   setRowStates((prev) => ({
  //     ...prev,
  //     [taskId]: { status: "pending", errorMsg: "" },
  //   }));
  
  //   try {
  //     await new Promise((resolve, reject) => {
  //       uploadFileMutation({ rowId: taskId, formData }, {
  //         onSuccess: resolve,
  //         onError: reject,
  //       });
  //     });
  //   } catch (error) {
  //     console.error(error);
  //   }
  // };

  const onSubmit = async (data) => {
    const formData = new FormData();
    formData.append("taskId", taskId);
    formData.append("softwareRelease", data.softwareRelease);
    if (data.Efile?.length) formData.append("eFile", data.Efile[0]);
  
    // Optional: mark row as pending
    setRowStates((prev) => ({
      ...prev,
      [taskId]: { status: "pending", errorMsg: "" },
    }));
  
    try {
      await new Promise((resolve, reject) => {
        uploadFileMutation(
          { rowId: taskId, formData },
          {
            onSuccess: (res) => {
              // Close modal on success
              setIsModalOpen(false);
  
              // Optional: mark row as completed
              setRowStates((prev) => ({
                ...prev,
                [taskId]: { status: "completed", errorMsg: "" },
              }));
              resolve(res);
            },
            onError: (err) => {
              // Show error if upload fails
              setRowStates((prev) => ({
                ...prev,
                [taskId]: {
                  status: "error",
                  errorMsg:
                    err?.response?.data?.message || "Something went wrong",
                },
              }));
              reject(err);
            },
          }
        );
      });
    } catch (error) {
      console.error(error);
    }
  };

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
      accessorKey: "taskId",
      header: "Task Id",
      cell: ({ row }) => row.getValue("taskId"),
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
      accessorKey: "site_id",
      header: "Site Id",
      cell: ({ row }) => {

        row.getValue("site_id")


        return <p className="cursor-pointer text-blue-600" onClick={() => {
          setCommonIsModalOpen(true)

          setCommonIsModalHead("View Sites")
          setCommonIsModalData(<><ul>{row.getValue("site_id").split("/").map((oneVal) => {
            return <li>{oneVal}</li>
          })}</ul></>)
        }}>View Sites</p>
      },
    },
    {
      accessorKey: "nodes",
      header: "Node Id",
      cell: ({ row }) => {

        row.getValue("nodes")


        return <p className="cursor-pointer text-blue-600" onClick={() => {
          setCommonIsModalOpen(true)

          setCommonIsModalHead("View Nodes")
          setCommonIsModalData(<><ul>{row.getValue("nodes").split("/").map((oneVal) => {
            return <li>{oneVal}</li>
          })}</ul></>)
        }}>View Nodes</p>
      },
    },
    
    {
      accessorKey: "nsa_op_folder",
      header: "DOWNLOAD",
      cell: ({ row }) => {
        const file = row.original;
        const token = useSelector((state) => state.auth.access_token);
        const [rowStates, setRowStates] = useState({});
    
        const handleDownload = async () => {
          
          setRowStates((prev) => ({
            ...prev,
            [file.id]: { loading: true, progress: 0 },
          }));
    
          try {
            
            for (let i = 0; i <= 100; i += 10) {
              await new Promise((resolve) => setTimeout(resolve, 100));
              setRowStates((prev) => ({
                ...prev,
                [file.id]: { ...prev[file.id], progress: i },
              })); 
            }
            await downloadFile(final_url + "/" + file.nsa_op_folder, token);
          } catch (error) {
            console.error("Download failed:", error);
          } finally {
            
            setRowStates((prev) => ({
              ...prev,
              [file.id]: { loading: false, progress: 0 },
            }));
          }
        };
    
        const rowState = rowStates[file.id] || { loading: false, progress: 0 }; 
    
        return (
          <div>
            <Button
              onClick={handleDownload}
              disabled={rowState.loading} 
              style={{
                backgroundColor: rowState.loading ? "#ccc" : "#007bff",
                color: rowState.loading ? "#666" : "#fff",
                cursor: rowState.loading ? "not-allowed" : "pointer",
              }}
            >
              {rowState.loading ? "Downloading..." : "Download"}
            </Button>
    
            {rowState.loading && ( 
              <div style={{ marginTop: "10px" }}>
                <div>Downloading: {rowState.progress}%</div>
                <div style={{ width: "100%", background: "#eee", borderRadius: "5px" }}>
                  <div
                    style={{
                      width: `${rowState.progress}%`,
                      background: "#4caf50",
                      height: "8px",
                      borderRadius: "5px",
                    }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        );
      },
    },

    
    {
      accessorKey: "status",
      header: "Processing",
      cell: ({ row }) => row.getValue("status"),
    },
    // {
    //   id: "status",
    //   header: "Processing",
    //   cell: ({ row }) => {



        
    //     return row.getValue("status")

    //     // return row.status
    //     // const rowState = rowStates[row.original.taskId] || { status: "pending", errorMsg: "" };
    
    //     // return (
    //     //   <div className="flex flex-col gap-1">
    //     //     {rowState.status === "pending" && <span className="text-gray-500 text-sm">Pending</span>}
    //     //     {rowState.status === "uploading" && (
    //     //       <div className="flex items-center gap-2">
    //     //         <svg className="animate-spin h-5 w-5 text-blue-500" viewBox="0 0 24 24">
    //     //           <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
    //     //           <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
    //     //         </svg>
    //     //         <span className="text-blue-500 text-sm">Uploading...</span>
    //     //       </div>
    //     //     )}
    //     //     {rowState.status === "completed" && <span className="text-green-600 text-sm">Completed</span>}
    //     //     {rowState.status === "error" && <span className="text-red-500 text-sm">{rowState.errorMsg}</span>}
    //     //   </div>
    //     // );
    //   },
    //   enableSorting: false,
    //   enableHiding: false,
    // },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const user = row.original;

        return (
          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => handleEdit(user)}
            >

              <Edit className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => handleDelete(user._id)}
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
          className="max-w-xs"
        />
        <Button onClick={() => setIsModalOpen(true)}>Upload Script</Button>
      </div>

      {/* Table */}
      <DataTableDemo
        columns={columns}
        data={user_scripting_files || []} // or whatever data you want to show
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
              <div className='flex flex-col'>
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
                  {/* <option>Task Id</option> */}

                  {JSON.stringify(enms_list)}

                  {enms_list && enms_list.map((one_enm, idx) => (
                  <option key={idx}>{one_enm.task_id}</option>
                ))}
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


                {/* </select> */}
              </div>
              {/* <div className="flex flex-col">
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
              </div> */}

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

export default ScriptingNokia;
