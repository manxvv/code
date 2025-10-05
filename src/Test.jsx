import React, { useState, useEffect } from "react";

const Test = () => {
  const [data, setData] = useState([]);
  const [page, setPage] = useState(1);
  const [limit] = useState(5); // items per page
  const [totalPages, setTotalPages] = useState(1);

  const fetchMigrationList = async (page) => {
    try {
      const token = localStorage.getItem("token"); // assume you store JWT in localStorage
      const res = await fetch(
`/migrationList?page=${page}&limit=${limit}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      const result = await res.json();

      setData(result.data);
      setTotalPages(result.total_pages);
    } catch (err) {
      console.error("Error fetching migration list:", err);
    }
  };

  useEffect(() => {
    fetchMigrationList(page);
  }, [page]);

  const handlePrev = () => {
    if (page > 1) setPage(page - 1);
  };

  const handleNext = () => {
    if (page < totalPages) setPage(page + 1);
  };

  return (
    <div>
      <h2>Migration List</h2>
      <ul>
        {data.map((item, index) => (
          <li key={index}>
            {JSON.stringify(item)}
          </li>
        ))}
      </ul>

      <div style={{ marginTop: "20px" }}>
        <button onClick={handlePrev} disabled={page === 1}>
          Prev
        </button>
        <span style={{ margin: "0 10px" }}>Page {page} of {totalPages}</span>
        <button onClick={handleNext} disabled={page === totalPages}>
          Next
        </button>
      </div>
    </div>
  );
};

export default Test;