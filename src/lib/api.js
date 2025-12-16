import Urls from "../config/urls";
import http, { final_url } from "./http";
export const fetchUsers = async (role = null) => {
  try {
    let url = Urls.users;

    if (role.length > 0) {

const roles = role === 'admin' ? ['operator','crypto_admin','content_admin','admin'] : [role];
const query = roles.map(r => `role=${encodeURIComponent(r)}`).join("&");

      url += `?${query}`;
    }

    const response = await http.get(url);
    return response.data;
  } catch (error) {
    console.error("Error fetching users:", error);
    throw error;
  }
};

export const createUsers = async (data) => {
  const response = await http.post(`${Urls.register_users}`,data);
  return response.data;
};

export const createEnms = async (data) => {
  const response = await http.post(`${Urls.emns}`,data);
  return response.data;
};

export const deleteEnm = async (id) => {
  const response = await http.delete(`${Urls.emns}/${id}`);
  return response.data;
};

export const deleteAuditData = async (id) => {
  const response = await http.delete(`${Urls.get_gpl_audit_files}/${id}`);
  return response.data;
};


export const createCircle = async (data) => {
  const response = await http.post(`${Urls.circles}`,data);
  return response.data;
};

export const editUsers = async (id, data) => {
  const response = await http.put(`${Urls.users}/${id}`, data);
  return response.data;
};

export const toggleRoleForLink = async ({ linkId, role, domain }) => {
  const response = await http.put(
    `/sidebar-links/${linkId}/toggle-role`,
    {
      role,
      domain, // 👈 required value
    }
  );
  return response.data;
};

// export const toggleRoleForLink  = async ({ linkId, role }) => {
//     const payload = { role };

//   const response = await http.put(`/sidebar-links/${linkId}/toggle-role`, payload);
//   return response.data;
// };


export const deleteUsers = async (id, data) => {
  const response = await http.delete(`${Urls.users}/${id}`, data);
  return response.data;
};


export const createAdmin = async (data) => {
  const response = await http.post(`${Urls.registeradmin}`, data);
  return response.data;
};


export const uploadPdf = async (data) => {
  const response = await http.post(`${Urls.upload}`, data);
  return response.data;
};



export const uploadgplauditScripting = async (data) => {
  const response = await http.post(`${Urls.gplaudituploadScripting}`, data);
  return response.data;
};




export const uploadScripting = async (data) => {
  const response = await http.post(`${Urls.uploadScripting}`, data);
  return response.data;
};


export const uploadSettingNokia = async (data) => {
  const response = await http.post(`${Urls.gplauditNokiaSetting}`, data);
  return response.data;
};
// export const uploadSettingNokiaTwo = async (data) => {
//   const response = await http.post(`${Urls.gplauditNokiaSetting_two}`, data);
//   return response.data;
// };


export const uploadSettingNokiaTwo = async (formData) => {
  return await http.post(Urls.gplauditNokiaSetting_two, formData, {
    responseType: "blob", // IMPORTANT
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

export const uploadenm = async (data) => {

  const response = await http.post(`${Urls.uploadenm}`, data);

  return response.data;
};
export const Urlfiles = async (data) => {
  const response = await http.get(`${Urls.urlfiles}`, data);
  return response.data;
};


export const getDomains = async () => {
  const res = await http.get("/domain");
  return res.data;
};

export const sidebarList = async (data = {}) => {
  const params = {};

  // only include domain if exists
  if (data.domain) {
    params.domain = data.domain;
  }

  // you can also forward other parameters if required
  // example:
  // if (data.role) params.role = data.role;

  const response = await http.get(Urls.sidebarlinks, {
    params, // axios automatically builds ?domain=xxxx
  });
  return response.data;
};



// export const sidebarList = async (data) => {
//   const response = await http.get(`${Urls.sidebarlinks}`, data);
//   return response.data;
// };
export const uploadLogo = async (formData) => {
  const response = await http.post(
    "/upload-logo",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
};

export const Urlenmmfiles = async (data) => {
  const response = await http.get(`${Urls.urlenmfiles}`, data);
  return response.data;
};




export const userfilescountData = async (data) => {
  const response = await http.get(`${Urls.userfilescount}`, data);
  return response.data;
};

export const mListCountData = async (data) => {
  const response = await http.get(`${Urls.mlistcount}`, data);
  return response.data;
};

export const userScriptCount = async (data) => {
  const response = await http.get(`${Urls.uscriptcount}`, data);
  return response.data;
};

export const enms = async (data) => {
  const response = await http.get(`${Urls.emns}`, data);
  return response.data;
};

export const getEnms = async (data) => {
  const response = await http.get(`${Urls.emns}`, data);
  return response.data;
};

export const circleData = async (data) => {
  const response = await http.get(`${Urls.circles}`, data);
  return response.data;
};

export const Dropdown = async (data) => {
  const response = await http.get(`${Urls.files}`, data);
  return response.data;
};
export const dashboard = async (data) => {
  const response = await http.get(`${Urls.dashboard}`, data);
  return response.data;
};
export const Dashboarddata = async ({ queryKey }) => {
  const [, selectedFile] = queryKey; // ["dashboard", selectedFile]
  const response = await http.get(`${Urls.dashboard}?_id=${selectedFile}`);
  return response.data;
};

export const getMembership = async (data) => {
  const response = await http.get(`${Urls.getmembership}`, data);
  return response.data;
};
export const updateMembership = async (id,data) => {
  const response = await http.put(`${Urls.getmembership}/${id}`, data);
  return response.data;
};
export const fanclubList = async (data) => {
  const response = await http.get(`${Urls.fanclub}`, data);
  return response.data;
};
// export const updateMemberHistory = async (id,data) => {
//   const response = await http.get(`${Urls.updatemember}/${id}`, data);
//   return response.data;
// };



export const updateMemberHistory = async ({ queryKey }) => {
  const [, id] = queryKey;
  const response = await http.get(`${Urls.updatemember}/${id}`);
  return response.data;
};


export const getuser_scripting_files = async () => {
  const response = await http.get(`${Urls.user_scripting_files}`);
  return response.data;
};



export const gpl_audit_files_get = async () => {
  const response = await http.get(`${Urls.get_gpl_audit_files}`);
  return response.data;
};




export const getUsers = async () => {
  const response = await http.get(`${Urls.users}`);
  return response.data;
};



// export const getMigrationList = async () => {
//   const response = await http.get(`${Urls.migrationList}`);
//   return response.data;
// };


export const analyzeData = async () => {
  const response = await http.get(`${Urls.analyze}`);
  return response.data;
};


export const patchCampaign = async () => {
  const response = await http.patch(`${Urls.patchcampaign}`);
  return response.data;
};
export const userBlock = async (id) => {
  const response = await http.patch(`${Urls.isblocked}/${id}`);
  return response.data;
};


export const getMigrationList = async ({ page = 1, limit = 10, search = "" }) => {
  const token = localStorage.getItem("token");
  
  // Create a URLSearchParams object and remove the search param if it's empty
  const params = new URLSearchParams({ 
    page: page.toString(), 
    limit: limit.toString() 
  });
  if (search) {
    params.append('search', search);
  }

  const res = await fetch(`${final_url}/migrationList?${params.toString()}`, {
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json' // It's good practice to include this header
    },
  });

  // --- THIS IS THE CRITICAL CHANGE ---
  // You must check if the response was successful and then parse the JSON body.
  if (!res.ok) {
    // If the server responded with an error, throw an error
    // to let React Query know the request failed.
    throw new Error('Network response was not ok');
  }

  const data = await res.json(); // <-- Add this line to parse the JSON response
  
  // Make sure your API returns an object like: { data: [...], total_pages: ... }
  // If your API returns a different structure, you might need to adapt it here.
  // For example, if it returns an array directly and a header for total pages:
  // const totalPages = res.headers.get('X-Total-Pages');
  // return { data: data, total_pages: Number(totalPages) };
  
  return data; // <-- Return the parsed data
};


export const migData = async ({ page = 1, limit = 10, search = "" }) => {
  const token = localStorage.getItem("token");

  const params = {
    page,
    limit,
  };
  if (search) params.search = search;

  const response = await http.get(Urls.migrationList, {
    headers: { Authorization: `Bearer ${token}` },
    params, // Axios automatically encodes this as ?page=...&limit=...
  });

  return response.data;
};

