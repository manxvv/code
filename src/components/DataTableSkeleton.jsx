import { Skeleton } from "@/components/ui/skeleton";

// A component to represent a single skeleton row that matches your table's columns
const SkeletonRow = () => (
    <div className="flex items-center space-x-4 p-4">
        <Skeleton className="h-6 flex-1" />
        <Skeleton className="h-6 flex-1" />
        <Skeleton className="h-6 flex-1" />
        <Skeleton className="h-6 flex-1" />
        <Skeleton className="h-6 flex-1" />
        <Skeleton className="h-6 flex-1" />
        <Skeleton className="h-6 w-24" /> {/* For the download button column */}
    </div>
);

export function DataTableSkeleton() {
  return (
    <div className="bg-white dark:bg-neutral-800 rounded-xl shadow-sm border border-gray-200 dark:border-neutral-700">
        {/* Skeleton for Table Header */}
        <div className="border-b border-gray-200 dark:border-neutral-700">
            <SkeletonRow />
        </div>

        {/* Skeleton for Table Body Rows */}
        <div className="divide-y divide-gray-200 dark:divide-neutral-700">
            {/* Create 5 placeholder rows */}
            {Array.from({ length: 5 }).map((_, index) => (
                <SkeletonRow key={index} />
            ))}
        </div>
    </div>
  );
}