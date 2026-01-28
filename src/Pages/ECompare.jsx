import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { useMutation } from "@tanstack/react-query";
import Swal from "sweetalert2";
import Modal from "@/components/Modal";
import { Button } from "@/components/ui/button";
import { runEricCompare } from "@/lib/api";

function ECompare() {
  const compareForm = useForm();
  const settingForm = useForm();

  const [compareOpen, setCompareOpen] = useState(false);
  const [settingOpen, setSettingOpen] = useState(false);

  // ================= SINGLE MUTATION =================
  const { mutate, isLoading } = useMutation({
    mutationFn: async (formData) => {
      Swal.fire({
        title: "Processing...",
        text: "Please wait",
        allowOutsideClick: false,
        didOpen: () => Swal.showLoading(),
      });

      return runEricCompare(formData);
    },

    onSuccess: (response) => {
      Swal.close();

      const headers = response.headers || {};
      const contentType = headers["content-type"];
      const disposition = headers["content-disposition"];

      // ================= FILE DOWNLOAD =================
      if (disposition) {
        const blob = new Blob([response.data], { type: contentType });

        let filename = "download";
        if (disposition.includes("filename=")) {
          filename = disposition.split("filename=")[1].replace(/"/g, "");
        }

        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;

        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      }

      // ✅ ONLY THIS MESSAGE
      Swal.fire({
        icon: "success",
        title: "Operation completed",
        timer: 2000,
        showConfirmButton: false,
      });

      setCompareOpen(false);
      setSettingOpen(false);
      compareForm.reset();
      settingForm.reset();
    },

    onError: (err) => {
      Swal.close();
      Swal.fire(
        "Error",
        err?.response?.data?.message || "Request failed",
        "error",
      );
    },
  });

  // ================= SUBMIT HANDLERS =================
  const onCompareSubmit = (data) => {
    if (!data.old || !data.new) {
      Swal.fire("Error", "Both OLD and NEW files are required", "error");
      return;
    }

    const formData = new FormData();
    formData.append("type", "compare");
    formData.append("old", data.old[0]);
    formData.append("new", data.new[0]);

    mutate(formData);
  };

  const onSettingSubmit = (data) => {
    if (!data.settings) {
      Swal.fire("Error", "Settings file required", "error");
      return;
    }

    const formData = new FormData();
    formData.append("type", "setting");
    formData.append("settings", data.settings[0]);

    mutate(formData);
  };

  // ================= UI =================
  return (
    <div className="p-4">
      <div className="flex justify-end gap-4 mb-4">
        <Button variant="outline" onClick={() => setSettingOpen(true)}>
          Upload Settings
        </Button>
        <Button onClick={() => setCompareOpen(true)}>Compare</Button>
      </div>

      {/* ===================== COMPARE MODAL ===================== */}
      <Modal
        isOpen={compareOpen}
        onClose={() => setCompareOpen(false)}
        title="Compare Old vs New"
        size="lg"
      >
        <div className="p-6">
          <form
            onSubmit={compareForm.handleSubmit(onCompareSubmit)}
            className="space-y-6"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block mb-1 font-medium">Old ZIP</label>
                <input
                  type="file"
                  accept=".zip"
                  {...compareForm.register("old", { required: true })}
                  className="p-1 border rounded-md w-full"
                />
              </div>

              <div>
                <label className="block mb-1 font-medium">New ZIP</label>
                <input
                  type="file"
                  accept=".zip"
                  {...compareForm.register("new", { required: true })}
                  className="p-1 border rounded-md w-full"
                />
              </div>
            </div>

            <Button
              type="submit"
              disabled={isLoading}
              className="w-full bg-orange-500 hover:bg-orange-600"
            >
              {isLoading ? "Comparing..." : "Compare Now"}
            </Button>
          </form>
        </div>
      </Modal>

      {/* ===================== SETTINGS MODAL ===================== */}
      <Modal
        isOpen={settingOpen}
        onClose={() => setSettingOpen(false)}
        title="Upload Settings"
        size="md"
      >
        <div className="p-6">
          <form
            onSubmit={settingForm.handleSubmit(onSettingSubmit)}
            className="space-y-6"
          >
            <div>
              <label className="block mb-1 font-medium">
                Settings File (CSV / XLSX)
              </label>
              <input
                type="file"
                accept=".csv,.xlsx,.xls"
                {...settingForm.register("settings", { required: true })}
                className="p-1 border rounded-md w-full"
              />
            </div>

            <Button
              type="submit"
              disabled={isLoading}
              className="w-full bg-orange-500 hover:bg-orange-600"
            >
              {isLoading ? "Uploading..." : "Upload Settings"}
            </Button>
          </form>
        </div>
      </Modal>
    </div>
  );
}

export default ECompare;
