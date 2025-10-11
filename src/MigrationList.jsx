import { Input } from '@/components/ui/input';
import { migData } from '@/lib/api';
import { useQuery } from '@tanstack/react-query';
import React, { useState } from 'react';
import { CheckCircle, XCircle } from 'lucide-react';
import { DataTableDemoP } from './components/DataTablePagination';

function MigrationList() {
    const [globalFilter, setGlobalFilter] = useState("");
    const [pagination, setPagination] = useState({
        pageIndex: 0, // Initial page index (0-based)
        pageSize: 10,  // Initial page size
    });

    const { data, isLoading } = useQuery({
        queryKey: ["migrationList", pagination.pageIndex, pagination.pageSize, globalFilter],
        queryFn: () => migData({
            page: pagination.pageIndex + 1,
            limit: pagination.pageSize,
            search: globalFilter
        }),
        keepPreviousData: true,
    });

    const migrationData = data?.data || [];
    const totalCount = data?.total_count || 0;
    const pageCount = Math.ceil(totalCount / pagination.pageSize);

    const columns = [
        { accessorKey: "task_id", header: "Task Id" },
        { accessorKey: "circle", header: "Circle" },
        { accessorKey: "enms", header: "ENM" },
        { accessorKey: "site_id", header: "Site Id" },
        { accessorKey: "nodes", header: "Node Id" },
        {
            accessorKey: "enm_command_status",
            header: "ENM Command Status",
            cell: ({ row }) => {
                const value = row.original.enm_command_status;
                return (
                    <div
                        className={`flex items-center w-fit gap-1 text-xs px-2 py-1 rounded-md ${value ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}
                    >
                        {value ? (
                            <>
                                <CheckCircle className="w-4 h-4 text-green-600" />
                                Completed
                            </>
                        ) : (
                            <>
                                <XCircle className="w-4 h-4 text-red-600" />
                                Not Completed
                            </>
                        )}
                    </div>
                );
            },
        },
        {
            accessorKey: "pre_check_completed",
            header: "Pre Check Status",
            cell: ({ row }) => {
                const value = row.original.pre_check_completed;
                return (
                    <div
                        className={`flex items-center w-fit gap-1 text-xs px-2 py-1 rounded-md ${value ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}
                    >
                        {value ? (
                            <>
                                <CheckCircle className="w-4 h-4 text-green-600" />
                                Completed
                            </>
                        ) : (
                            <>
                                <XCircle className="w-4 h-4 text-red-600" />
                                Not Completed
                            </>
                        )}
                    </div>
                );
            },
        },
        {
            accessorKey: "scripting_completed",
            header: "Scripting Status",
            cell: ({ row }) => {
                const value = row.original.scripting_completed;
                return (
                    <div
                        className={`flex items-center w-fit gap-1 text-xs px-2 py-1 rounded-md ${value ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}
                    >
                        {value ? (
                            <>
                                <CheckCircle className="w-4 h-4 text-green-600" />
                                Completed
                            </>
                        ) : (
                            <>
                                <XCircle className="w-4 h-4 text-red-600" />
                                Not Completed
                            </>
                        )}
                    </div>
                );
            },
        },
        {
            accessorKey: "post_check_completed",
            header: "Post Check Status",
            cell: ({ row }) => {
                const value = row.original.post_check_completed;
                return (
                    <div
                        className={`flex items-center w-fit gap-1 text-xs px-2 py-1 rounded-md ${value ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}
                    >
                        {value ? (
                            <>
                                <CheckCircle className="w-4 h-4 text-green-600" />
                                Completed
                            </>
                        ) : (
                            <>
                                <XCircle className="w-4 h-4 text-red-600" />
                                Not Completed
                            </>
                        )}
                    </div>
                );
            },
        },
        {
            accessorKey: "migration_completed",
            header: "Migration Status",
            cell: ({ row }) => {
                const value = row.original.migration_completed;
                return (
                    <div
                        className={`flex items-center w-fit gap-1 text-xs px-2 py-1 rounded-md ${value ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}
                    >
                        {value ? (
                            <>
                                <CheckCircle className="w-4 h-4 text-green-600" />
                                Completed
                            </>
                        ) : (
                            <>
                                <XCircle className="w-4 h-4 text-red-600" />
                                Not Completed
                            </>
                        )}
                    </div>
                );
            },
        },
    ];

    return (
        <div className="p-4 bg-white dark:bg-neutral-900 flex flex-col gap-4">
            <div className="flex flex-col sm:flex-row gap-2 w-full md:w-auto">
                <Input
                    placeholder="Search by Task ID..."
                    value={globalFilter}
                    onChange={(e) => {
                        setGlobalFilter(e.target.value);
                        setPagination(prev => ({ ...prev, pageIndex: 0 }));
                    }}
                    className="w-fit"
                />
            </div>

            <DataTableDemoP
                data={migrationData}
                columns={columns}
                isLoading={isLoading}
                pagination={pagination}
                setPagination={setPagination}
                pageCount={pageCount}
                totalCount={totalCount}
            />
        </div>
    );
}

export default MigrationList;