import { useState, useEffect, useMemo } from "react";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
  LineChart,
  Line
} from "recharts";
import { ChevronDown, Loader2 } from "lucide-react";
import { Card, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { dashboard, enms, getUsers } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";

const EDashboard = () => {
  // Simulating your existing state and queries with dummy data
  const [selectedFile, setSelectedFile] = useState(null);
  // const isLoading = false;
  const dashboardLoading = false;


   const { data: circle,isLoading:circleLoading } = useQuery({
         queryKey: ["enms"],
         queryFn: enms
     });


      const uniqueCircles = [...new Set(circle?.map((item) => item.circle).filter(Boolean))];

 

  const { data_real, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: dashboard
  });

  // Dummy data structure matching your API structure
  const data = {
    data: [
      { _id: "file1", filename: "Site_Audit_2024_Q1.xlsx" },
      { _id: "file2", filename: "Site_Audit_2024_Q2.xlsx" },
      { _id: "file3", filename: "Site_Audit_2024_Q3.xlsx" }
    ],
    site_id_status: {
      total: 100,
      pre_check_completed: 85,
      post_check_completed: 72,
      scripting_completed_completed: 68,
      migration_completed: 45
    }
  };


  console.log(data_real,"data_realdata_realdata_real")

  const dashboardData = {
    data: {
      final_result: [{
        sectorA_caution: 15,
        sectorA_notice: 8,
        sectorA_warning: 3,
        sectorB_caution: 12,
        sectorB_notice: 6,
        sectorB_warning: 2,
        sectorC_caution: 18,
        sectorC_notice: 10,
        sectorC_warning: 5,
        total_caution: 500
      }],
      final_result2: [{
        masking_areas: {
          ok_parameters: 70000,
          not_ok_parameters: 1000,
          configured_mo: 450,
          not_configured_mo: 50
        }
      }]
    }
  };

  // Auto-select first file when data loads
  useEffect(() => {
    if (!isLoading && data?.data?.length > 0 && !selectedFile) {
      setSelectedFile(data.data[0]._id);
    }
  }, [isLoading, selectedFile]);

  // const uniqueCircles = useMemo(() => {
  //       if (!enmData) return [];
  //       const circles = enmData.map(item => item.circle);
  //       return [...new Set(circles)];
  //   }, [enmData]);

  // Process hazard data for bar chart
  const hazardData = dashboardData?.data?.final_result
    ?.map(item => [
      { name: "MO Not Configured", value: 5000 },
      { name: "NSA Parameter", value: 4000 },
      { name: "Not Matched with GPL", value: 1000 }
    ])
    .flat() || [];

  // Process data for charts
  const moStatusData = [
    { name: "OK MO", value: 450 },
    { name: "Not OK MO", value: 50 }
  ];

  const parameterStatusData = [
    { name: "OK Parameters", value: 70000 },
    { name: "Not OK Parameters", value: 1000 }
  ];

  // Trends data
  const trendsData = [
    { month: "Jan", value: 85 },
    { month: "Feb", value: 78 },
    { month: "Mar", value: 72 },
    { month: "Apr", value: 68 },
    { month: "May", value: 65 },
    { month: "Jun", value: 62 }
  ];

  let list = [{
    "value": "total",
    "userValue": "Total Sites - ENM Commands",
    "bgcolor": "bg-[#9606f8]",
    "textcolor": "text-[#ffffff]"
  }, {
    "value": "pre_check_completed",
    "userValue": "Total Sites - Pre Check",
    "bgcolor": "bg-[#f14919]",
    "textcolor": "text-[#ffffff]"
  }, {
    "value": "post_check_completed",
    "userValue": "Total Sites - Post Check",
    "bgcolor": "bg-[#26c885]",
    "textcolor": "text-[#ffffff]"
  }, {
    "value": "scripting_completed_completed",
    "userValue": "Total Sites - Scripting Done",
    "bgcolor": "bg-[#26bec8]",
    "textcolor": "text-[#ffffff]"
  }, {
    "value": "migration_completed",
    "userValue": "Total Sites - Migration Done",
    "bgcolor": "bg-[#f32cad]",
    "textcolor": "text-[#ffffff]"
  }];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto p-8 space-y-8">

        {/* Header */}
        <div className="flex gap-2 justify-end">



          <div className="w-fit flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Select Circle:
            </label>

            <Select>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Choose Circle" />
              </SelectTrigger>
              <SelectContent>
               {uniqueCircles.map((circleName) => (
          <SelectItem key={circleName} value={circleName}>
            {circleName}
          </SelectItem>
        ))}
              </SelectContent>
            </Select>
          </div>

        </div>



        {/* Original Status Cards - Simplified */}
        <div className="grid grid-cols-1 md:grid-cols-5 xl:grid-cols-5 gap-4">
          {list.map((oneValueOfBoard, index) => (
            <Card key={index} className={`border text-white border-gray-200 dark:border-gray-700 ${oneValueOfBoard.bgcolor} dark:${oneValueOfBoard.bgcolor}`}>
              <CardContent className="p-4">
                <div className="">
                  <p className="text-xl text-black dark:text-white leading-tight">
                    {oneValueOfBoard.userValue || "N/A"}
                  </p>
                  <p className="text-2xl  font-bold text-black dark:text-white">
                    {data?.site_id_status?.[oneValueOfBoard.value] || 0}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        {/* Top Metrics - Minimalist Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div className="text-center space-y-1">
            <div className="text-sm text-gray-500 dark:text-gray-400">Total Site Audits</div>
            <div className="text-4xl font-light text-gray-900 dark:text-gray-100">100</div>
          </div>
          <div className="text-center space-y-1">
            <div className="text-sm text-gray-500 dark:text-gray-400">MO Checked</div>
            <div className="text-4xl font-light text-gray-900 dark:text-gray-100">500</div>
          </div>
          <div className="text-center space-y-1">
            <div className="text-sm text-gray-500 dark:text-gray-400">Parameters Audited</div>
            <div className="text-4xl font-light text-green-600">70K</div>
          </div>
          <div className="text-center space-y-1">
            <div className="text-sm text-gray-500 dark:text-gray-400">OK Parameters</div>
            <div className="text-4xl font-light text-red-500">1K</div>
          </div>
        </div>

        {/* Charts Grid - Clean and Minimal */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">

          {/* MO Status */}
          <Card className="border-0 shadow-none bg-white dark:bg-gray-800">
            <CardContent className="p-8">
              <div className="text-sm text-gray-500 dark:text-gray-400 mb-6">MO Status</div>
              <div className="h-64 relative">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={moStatusData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      innerRadius={70}
                      outerRadius={100}
                      paddingAngle={4}
                    >
                      <Cell fill="#22c55e" />
                      <Cell fill="#ef4444" />
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "white",
                        border: "1px solid #e5e7eb",
                        borderRadius: "4px",
                        fontSize: "14px"
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-xs text-gray-500 dark:text-gray-400">OK MO</div>
                    <div className="text-2xl font-light text-gray-900 dark:text-gray-100">450</div>
                  </div>
                </div>
              </div>
              <div className="flex justify-center space-x-6 mt-4 text-xs text-gray-500 dark:text-gray-400">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>OK MO</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  <span>Not OK MO</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Parameter Status */}
          <Card className="border-0 shadow-none bg-white dark:bg-gray-800">
            <CardContent className="p-8">
              <div className="text-sm text-gray-500 dark:text-gray-400 mb-6">Parameter Status</div>
              <div className="h-64 space-y-8">
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">OK Parameters</span>
                    <span className="text-gray-900 dark:text-gray-100">70K</span>
                  </div>
                  <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-sm h-2">
                    <div className="bg-green-500 h-2 rounded-sm" style={{ width: "98.6%" }}></div>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">Not OK Parameters</span>
                    <span className="text-gray-900 dark:text-gray-100">1K</span>
                  </div>
                  <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-sm h-2">
                    <div className="bg-red-500 h-2 rounded-sm" style={{ width: "1.4%" }}></div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Not OK Details */}
          <Card className="border-0 shadow-none bg-white dark:bg-gray-800">
            <CardContent className="p-8">
              <div className="text-sm text-gray-500 dark:text-gray-400 mb-6">Not OK Details</div>
              <div className="space-y-6">
                {hazardData.map((item, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 dark:text-gray-300">{item.name}</span>
                    <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {item.value.toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Trends */}
          <Card className="border-0 shadow-none bg-white dark:bg-gray-800">
            <CardContent className="p-8">
              <div className="text-sm text-gray-500 dark:text-gray-400 mb-6">Trends</div>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trendsData}>
                    <XAxis
                      dataKey="month"
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 12, fill: "#9ca3af" }}
                    />
                    <YAxis hide />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "white",
                        border: "1px solid #e5e7eb",
                        borderRadius: "4px",
                        fontSize: "12px"
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="#6b7280"
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default EDashboard;