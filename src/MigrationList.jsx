import { DataTableDemo } from '@/components/DataTable';
import { Input } from '@/components/ui/input';
import { getMigrationList } from '@/lib/api';
import { useQuery } from '@tanstack/react-query';
import React, { useState } from 'react';

function MigrationList() {
    const [globalFilter, setGlobalFilter] = useState("");
    const [page, setPage] = useState(1);
    const [limit] = useState(10);

    // Fetch data with page, limit, search
    // FIX: The useQuery hook now takes a single object as an argument.
    const { data, isLoading } = useQuery({
        queryKey: ["migrationList", page, globalFilter, limit], // Added limit to the query key for correctness
        queryFn: () => getMigrationList({ page, limit, search: globalFilter }),
        keepPreviousData: true, // This keeps old data visible while new data is fetching
    });

    // Handle page change
    const handlePrev = () => {
        if (page > 1) {
            setPage(page - 1);
        }
    };
    const handleNext = () => {
        // Use optional chaining with data to prevent errors if data is not yet available
        if (page < (data?.total_pages || 1)) {
            setPage(page + 1);
        }
    };

    const columns = [
        { accessorKey: "task_id", header: "Task Id" },
        { accessorKey: "circle", header: "Circle" },
        { accessorKey: "enms", header: "ENM" },
        { accessorKey: "enms-command-status", header: "ENM Command Status" },

        { accessorKey: "site_id", header: "Site Id" },
        { accessorKey: "nodes", header: "Node Id" },
        {
            accessorKey: "statusList",
            header: "Pre Check Status",
            cell: ({ row }) => row.getValue("statusList")?.pre_check_completed ? "Completed" : "N/A"
        },
        {
            accessorKey: "statusList",
            header: "Scripting Status",
            cell: ({ row }) => row.getValue("statusList")?.scripting_completed ? "Completed" : "N/A"
        },
        {
            accessorKey: "statusList",
            header: "Post Check Status",
            cell: ({ row }) => row.getValue("statusList")?.post_check_completed ? "Completed" : "N/A"
        },
        {
            accessorKey: "statusList",
            header: "Migration Status",
            cell: ({ row }) => row.getValue("statusList")?.migration_completed ? "Completed" : "N/A"
        }
    ];

    // Calculate if the next button should be disabled
    const isNextDisabled = isLoading || page >= (data?.total_pages || 1);

    return (
        <div className="p-4 bg-white dark:bg-neutral-900 flex flex-col gap-4">
            <div className="flex flex-col sm:flex-row gap-2 w-full md:w-auto">
                <Input
                    placeholder="Search..."
                    value={globalFilter}
                    onChange={(e) => {
                        setGlobalFilter(e.target.value);
                        setPage(1); // Reset to page 1 on new search
                    }}
                    className="w-fit sm:max-w-sm"
                />
            </div>

            <DataTableDemo
                data={data?.data || []}
                columns={columns}
                // These props might not be necessary if your DataTableDemo doesn't use them directly
                // globalFilter={globalFilter}
                // setGlobalFilter={setGlobalFilter}
                isLoading={isLoading}
            />

            {/* Pagination Controls */}
            <div className="flex justify-between items-center mt-4">
                <button
                    onClick={handlePrev}
                    disabled={page === 1}
                    className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
                >
                    Prev
                </button>
                <span>Page {page} of {data?.total_pages || 1}</span>
                <button
                    onClick={handleNext}
                    disabled={isNextDisabled}
                    className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
                >
                    Next
                </button>
            </div>
        </div>
    );
}

export default MigrationList;



// import React from 'react'

// export default function MigrationList() {
//   return (
//     <div>ello</div>
//   )
// }
